"""Data ingestion script for populating Qdrant vector store.

Usage:
    uv run python scripts/ingest_data.py

This script:
1. Loads articles from data/stock_news.json
2. Chunks the text into smaller segments
3. Generates embeddings using OpenAI
4. Stores vectors in Qdrant with metadata
"""

import asyncio
from pathlib import Path

from src.config import get_settings
from src.core.logging import get_logger
from src.rag.data_loader import load_json_data, chunk_documents
from src.rag.vector_store import get_vector_store

logger = get_logger(__name__)


async def ingest_data():
    """Ingest stock news data into Qdrant."""
    settings = get_settings()

    # Path to data file (relative to backend root)
    data_path = Path(__file__).parent.parent.parent.parent / "data" / "stock_news.json"

    if not data_path.exists():
        logger.error(
            "Data file not found",
            path=str(data_path),
            message="Please ensure stock_news.json exists in the data/ directory"
        )
        return

    logger.info("Starting data ingestion", data_file=str(data_path))

    # Step 1: Load documents
    logger.info("Loading documents from JSON...")
    documents = load_json_data(data_path)

    if not documents:
        logger.error("No documents loaded", message="Check data file format and content")
        return

    logger.info("Documents loaded", count=len(documents))

    # Step 2: Chunk documents
    logger.info("Chunking documents...")
    chunked_docs = chunk_documents(documents, chunk_size=1000, chunk_overlap=200)
    logger.info("Documents chunked", chunks=len(chunked_docs))

    # Step 3: Initialize collection if needed
    logger.info(
        "Initializing Qdrant collection",
        collection=settings.QDRANT_COLLECTION_NAME,
    )
    from src.rag.vector_store import initialize_collection
    await initialize_collection()

    # Step 4: Get vector store
    logger.info(
        "Initializing vector store",
        collection=settings.QDRANT_COLLECTION_NAME,
        host=settings.QDRANT_HOST,
        port=settings.QDRANT_PORT,
    )
    vector_store = get_vector_store()

    # Step 5: Add documents to vector store
    logger.info("Adding documents to vector store...")
    try:
        # Extract texts and metadatas
        texts = [doc.page_content for doc in chunked_docs]
        metadatas = [doc.metadata for doc in chunked_docs]

        # Add to vector store (this will embed and store)
        await vector_store.aadd_texts(texts=texts, metadatas=metadatas)

        logger.info(
            "✅ Data ingestion complete",
            total_chunks=len(chunked_docs),
            collection=settings.QDRANT_COLLECTION_NAME,
        )
    except Exception as e:
        logger.error(
            "Failed to ingest data",
            error=str(e),
            error_type=type(e).__name__,
        )
        raise


def main():
    """Main entry point."""
    try:
        asyncio.run(ingest_data())
    except KeyboardInterrupt:
        logger.info("Ingestion cancelled by user")
    except Exception as e:
        logger.error("Ingestion failed", error=str(e))
        raise


if __name__ == "__main__":
    main()
