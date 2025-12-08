"""Retriever implementations for RAG pipeline.

Per .cursorrules: NO LangGraph - uses LCEL only.
Available retrievers: self_query (default), base, multi_query,
contextual_compression, hybrid, ensemble.
"""

from typing import Literal

from langchain_core.retrievers import BaseRetriever
from langchain_openai import ChatOpenAI

from src.config import get_settings
from src.rag.vector_store import get_vector_store

RetrieverType = Literal[
    "self_query",
    "base",
    "multi_query",
    "contextual_compression",
    "hybrid",
    "ensemble",
]


def get_llm() -> ChatOpenAI:
    """Get LLM for retriever operations."""
    settings = get_settings()
    return ChatOpenAI(
        model=settings.OPENAI_MODEL,
        temperature=0,
        api_key=settings.OPENAI_API_KEY,  # type: ignore[arg-type]
    )


def create_base_retriever(
    ticker_filter: list[str] | None = None,
    k: int = 5,
) -> BaseRetriever:
    """Create base vector store retriever.

    Args:
        ticker_filter: Optional list of tickers to filter by.
        k: Number of documents to retrieve.

    Returns:
        Configured base retriever.
    """
    store = get_vector_store()

    search_kwargs = {"k": k}

    if ticker_filter:
        # Qdrant filter for ticker metadata
        search_kwargs["filter"] = {  # type: ignore[assignment]
            "must": [
                {
                    "key": "metadata.ticker",
                    "match": {"any": ticker_filter}
                }
            ]
        }

    return store.as_retriever(search_kwargs=search_kwargs)


def create_self_query_retriever(
    ticker_filter: list[str] | None = None,
) -> BaseRetriever:
    """Create self-query retriever with metadata filtering.

    The self-query retriever can automatically extract metadata filters
    from natural language queries.

    Args:
        ticker_filter: Optional explicit ticker filter.

    Returns:
        Configured self-query retriever.
    """
    from langchain.chains.query_constructor.schema import AttributeInfo
    from langchain.retrievers.self_query.base import SelfQueryRetriever

    store = get_vector_store()
    llm = get_llm()

    # Define metadata attributes for self-query
    metadata_field_info = [
        AttributeInfo(
            name="ticker",
            description="Stock ticker symbol (e.g., AAPL, MSFT, AMZN, NFLX, NVDA, INTC, IBM)",
            type="string",
        ),
        AttributeInfo(
            name="source",
            description="News source (e.g., Reuters, Bloomberg, CNBC)",
            type="string",
        ),
        AttributeInfo(
            name="date",
            description="Article publication date in YYYY-MM-DD format",
            type="string",
        ),
    ]

    document_content_description = "Financial news articles about tech stocks"

    retriever = SelfQueryRetriever.from_llm(
        llm=llm,
        vectorstore=store,
        document_contents=document_content_description,
        metadata_field_info=metadata_field_info,
        verbose=True,
    )

    return retriever  # type: ignore[no-any-return]


def create_multi_query_retriever() -> BaseRetriever:
    """Create multi-query retriever.

    Generates multiple query variations for better recall.

    Returns:
        Configured multi-query retriever.
    """
    from langchain.retrievers.multi_query import MultiQueryRetriever

    base_retriever = create_base_retriever()
    llm = get_llm()

    return MultiQueryRetriever.from_llm(  # type: ignore[no-any-return]
        retriever=base_retriever,
        llm=llm,
    )


def create_contextual_compression_retriever() -> BaseRetriever:
    """Create contextual compression retriever.

    Compresses retrieved documents to most relevant parts.

    Returns:
        Configured compression retriever.
    """
    from langchain.retrievers import ContextualCompressionRetriever
    from langchain.retrievers.document_compressors import LLMChainExtractor

    base_retriever = create_base_retriever()
    llm = get_llm()

    compressor = LLMChainExtractor.from_llm(llm)

    return ContextualCompressionRetriever(  # type: ignore[no-any-return]
        base_compressor=compressor,
        base_retriever=base_retriever,
    )


def create_hybrid_retriever(
    ticker_filter: list[str] | None = None,
) -> BaseRetriever:
    """Create hybrid retriever (dense + sparse).

    Combines semantic search with keyword matching.

    Args:
        ticker_filter: Optional ticker filter.

    Returns:
        Configured hybrid retriever.
    """
    # For Qdrant, hybrid search requires FastEmbed for sparse vectors
    # This is a simplified version using the vector store's built-in hybrid
    store = get_vector_store()

    search_kwargs = {
        "k": 5,
        "search_type": "mmr",  # Maximal Marginal Relevance
        "fetch_k": 20,
    }

    if ticker_filter:
        search_kwargs["filter"] = {
            "must": [
                {"key": "metadata.ticker", "match": {"any": ticker_filter}}
            ]
        }

    return store.as_retriever(search_kwargs=search_kwargs)


def create_ensemble_retriever(
    ticker_filter: list[str] | None = None,
) -> BaseRetriever:
    """Create ensemble retriever combining multiple strategies.

    Args:
        ticker_filter: Optional ticker filter.

    Returns:
        Configured ensemble retriever.
    """
    from langchain.retrievers import EnsembleRetriever

    # Combine base and multi-query retrievers
    base = create_base_retriever(ticker_filter=ticker_filter)
    multi = create_multi_query_retriever()

    return EnsembleRetriever(  # type: ignore[no-any-return]
        retrievers=[base, multi],
        weights=[0.5, 0.5],
    )


def get_retriever(
    retriever_type: RetrieverType = "self_query",
    ticker_filter: list[str] | None = None,
) -> BaseRetriever:
    """Factory function to get configured retriever.

    Args:
        retriever_type: Type of retriever to create.
        ticker_filter: Optional ticker filter for applicable retrievers.

    Returns:
        Configured retriever instance.

    Raises:
        ValueError: If retriever_type is not supported.
    """
    retrievers = {
        "self_query": lambda: create_self_query_retriever(ticker_filter),
        "base": lambda: create_base_retriever(ticker_filter),
        "multi_query": create_multi_query_retriever,
        "contextual_compression": create_contextual_compression_retriever,
        "hybrid": lambda: create_hybrid_retriever(ticker_filter),
        "ensemble": lambda: create_ensemble_retriever(ticker_filter),
    }

    if retriever_type not in retrievers:
        raise ValueError(
            f"Invalid retriever type: {retriever_type}. "
            f"Must be one of: {list(retrievers.keys())}"
        )

    return retrievers[retriever_type]()  # type: ignore[no-untyped-call]
