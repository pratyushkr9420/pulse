"""RAG chain implementation using LCEL.

Per .cursorrules: NO LangGraph - pure LCEL implementation.
"""

from typing import Any

from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_openai import ChatOpenAI

from src.config import get_settings
from src.rag.retrievers import RetrieverType, get_retriever
from src.schemas.chat import SourceInfo

# RAG Prompt Template
RAG_PROMPT = ChatPromptTemplate.from_template(
    """You are a helpful financial news assistant for Pulse, a stock news chatbot.
Answer the question based ONLY on the following context from financial news articles.
If you cannot answer from the context, say "I don't have information about that in my sources."

Always cite your sources by mentioning the headline and ticker symbol.
Be concise but informative. Focus on facts from the articles.

Context:
{context}

Question: {question}

Answer:"""
)


def format_docs(docs: list[Document]) -> str:
    """Format documents for context injection.

    Args:
        docs: List of retrieved documents.

    Returns:
        Formatted string with document content and metadata.
    """
    formatted = []
    for i, doc in enumerate(docs, 1):
        meta = doc.metadata
        formatted.append(
            f"[{i}] {meta.get('headline', 'Untitled')} ({meta.get('ticker', 'N/A')})\n"
            f"Source: {meta.get('source', 'Unknown')} - {meta.get('date', 'N/A')}\n"
            f"{doc.page_content}\n"
        )
    return "\n---\n".join(formatted)


def extract_sources(docs: list[Document]) -> list[SourceInfo]:
    """Extract source information from documents.

    Args:
        docs: List of retrieved documents.

    Returns:
        List of SourceInfo objects.
    """
    sources = []
    seen_links = set()

    for doc in docs:
        meta = doc.metadata
        link = meta.get("link", "")

        # Deduplicate by link
        if link in seen_links:
            continue
        seen_links.add(link)

        # Extract relevance score from metadata (set by invoke_rag) or document attribute
        # Fallback to 0.85 if not available
        relevance_score = meta.get('_score', getattr(doc, 'score', 0.85))
        if isinstance(relevance_score, str):
            relevance_score = 0.85

        sources.append(
            SourceInfo(
                title=meta.get("headline", "Untitled"),
                ticker=meta.get("ticker", "N/A"),
                link=link,
                snippet=doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                relevance_score=min(max(float(relevance_score), 0.0), 1.0),
            )
        )

    return sources


def create_rag_chain(
    retriever_type: RetrieverType = "self_query",
    ticker_filter: list[str] | None = None,
) -> Any:
    """Create RAG chain using LCEL.

    Args:
        retriever_type: Type of retriever to use.
        ticker_filter: Optional ticker filter.

    Returns:
        LCEL chain for RAG.
    """
    settings = get_settings()

    retriever = get_retriever(retriever_type, ticker_filter)

    llm = ChatOpenAI(
        model=settings.OPENAI_MODEL,
        temperature=0.1,
        api_key=settings.OPENAI_API_KEY,  # type: ignore[arg-type]
    )

    # LCEL chain composition
    chain = (
        RunnableParallel(
            context=retriever | format_docs,
            question=RunnablePassthrough(),
        )
        | RAG_PROMPT
        | llm
        | StrOutputParser()
    )

    return chain


async def invoke_rag(
    question: str,
    retriever_type: RetrieverType = "self_query",
    ticker_filter: list[str] | None = None,
) -> dict[str, Any]:
    """Invoke RAG chain and return response with sources.

    Args:
        question: User's question.
        retriever_type: Type of retriever to use.
        ticker_filter: Optional ticker filter.

    Returns:
        Dict with 'response' and 'sources' keys.
    """
    retriever = get_retriever(retriever_type, ticker_filter)

    # Get documents for source extraction
    docs = await retriever.ainvoke(question)

    # Attach actual similarity scores from vector store to documents
    # This runs a parallel search to get scores without changing retrieval behavior
    try:
        from src.rag.vector_store import get_vector_store
        vector_store = get_vector_store()

        # Get same number of docs with scores (match retriever's k value, default is 5)
        k = len(docs) if docs else 5
        docs_with_scores = await vector_store.asimilarity_search_with_score(
            question, k=k, filter=_build_qdrant_filter(ticker_filter)
        )

        # Match retrieved docs with scored docs by content and attach scores
        # Create a mapping of page_content -> score for O(n) lookup
        score_map = {doc.page_content: score for doc, score in docs_with_scores}

        for doc in docs:
            if doc.page_content in score_map:
                score = score_map[doc.page_content]
                # Normalize Qdrant cosine similarity from [-1, 1] to [0, 1]
                # Higher cosine similarity = more similar, so (score + 1) / 2
                normalized_score = (score + 1.0) / 2.0
                doc.metadata['_score'] = normalized_score
    except Exception:
        # If score extraction fails, continue without scores (will use 0.85 default)
        # This ensures backward compatibility and graceful degradation
        pass

    # Create and invoke chain
    chain = create_rag_chain(retriever_type, ticker_filter)
    response = await chain.ainvoke(question)

    # Extract sources
    sources = extract_sources(docs)

    return {
        "response": response,
        "sources": sources,
    }


def _build_qdrant_filter(ticker_filter: list[str] | None) -> dict[str, Any] | None:
    """Build Qdrant filter dict from ticker filter.

    Args:
        ticker_filter: Optional list of ticker symbols.

    Returns:
        Qdrant filter dict or None.
    """
    if not ticker_filter:
        return None

    return {
        "must": [
            {
                "key": "metadata.ticker",
                "match": {"any": ticker_filter}
            }
        ]
    }
