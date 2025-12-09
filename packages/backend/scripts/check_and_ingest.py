"""Conditional data ingestion script for Docker entrypoint.

This script checks if the Qdrant collection already has data and only
ingests if the collection is empty or doesn't exist.

Usage:
    uv run python scripts/check_and_ingest.py

Exit codes:
    0 - Success (data already exists or ingestion completed)
    1 - Error (missing data file, ingestion failed, etc.)
"""

import asyncio
import sys
from pathlib import Path

from src.config import get_settings
from src.core.logging import get_logger
from src.rag.data_loader import chunk_documents, load_json_data
from src.rag.vector_store import get_qdrant_client, get_vector_store, initialize_collection

logger = get_logger(__name__)


async def check_collection_has_data() -> bool:
    """Check if Qdrant collection exists and has data.

    Returns:
        True if collection exists and has documents, False otherwise.
    """
    settings = get_settings()
    try:
        client = get_qdrant_client()

        # Check if collection exists
        collections = client.get_collections().collections
        collection_names = [c.name for c in collections]

        if settings.QDRANT_COLLECTION_NAME not in collection_names:
            logger.info(
                "Collection does not exist",
                collection=settings.QDRANT_COLLECTION_NAME,
            )
            return False

        # Check if collection has data
        collection_info = client.get_collection(settings.QDRANT_COLLECTION_NAME)
        points_count = collection_info.points_count

        if points_count == 0:
            logger.info(
                "Collection exists but is empty",
                collection=settings.QDRANT_COLLECTION_NAME,
            )
            return False

        logger.info(
            "Collection exists with data",
            collection=settings.QDRANT_COLLECTION_NAME,
            points_count=points_count,
        )
        return True

    except Exception as e:
        logger.error(
            "Failed to check collection",
            error=str(e),
            error_type=type(e).__name__,
        )
        return False


async def ingest_data():
    """Ingest stock news data into Qdrant."""
    settings = get_settings()

    # Path to data file (relative to backend root)
    data_path = Path(__file__).parent.parent / "data" / "stock_news.json"

    if not data_path.exists():
        logger.error(
            "Data file not found",
            path=str(data_path),
            message="Please ensure stock_news.json exists in the data/ directory",
        )
        sys.exit(1)

    logger.info("Starting data ingestion", data_file=str(data_path))

    # Step 1: Load documents
    logger.info("Loading documents from JSON...")
    documents = load_json_data(data_path)

    if not documents:
        logger.error("No documents loaded", message="Check data file format and content")
        sys.exit(1)

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
    await initialize_collection()

    # Step 4: Get vector store
    logger.info(
        "Initializing vector store",
        collection=settings.QDRANT_COLLECTION_NAME,
        host=settings.QDRANT_HOST,
        port=settings.QDRANT_PORT,
    )
    vector_store = get_vector_store()

    # Step 5: Add documents to vector store with batching
    logger.info("Adding documents to vector store...")
    try:
        # Extract texts and metadatas
        texts = [doc.page_content for doc in chunked_docs]
        metadatas = [doc.metadata for doc in chunked_docs]

        # Add to vector store with batching to prevent rate limits
        logger.info(f"Storing {len(texts)} document chunks in vector store")

        # Batch processing to prevent API rate limits
        BATCH_SIZE = 100
        total_batches = (len(texts) + BATCH_SIZE - 1) // BATCH_SIZE

        for i in range(0, len(texts), BATCH_SIZE):
            batch_texts = texts[i : i + BATCH_SIZE]
            batch_metadatas = metadatas[i : i + BATCH_SIZE]
            batch_num = i // BATCH_SIZE + 1

            logger.info(
                f"Ingesting batch {batch_num}/{total_batches} ({len(batch_texts)} chunks)"
            )
            await vector_store.aadd_texts(texts=batch_texts, metadatas=batch_metadatas)

            # Rate limiting: wait 2 seconds between batches (except for the last batch)
            if i + BATCH_SIZE < len(texts):
                await asyncio.sleep(2)

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
        sys.exit(1)


async def main():
    """Main entry point - check if data exists and ingest if needed."""
    logger.info("🔍 Checking Qdrant collection status...")

    has_data = await check_collection_has_data()

    if has_data:
        logger.info("✅ Collection already has data - skipping ingestion")
        return

    logger.info("📥 Collection is empty - starting data ingestion...")
    await ingest_data()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Ingestion cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error("Ingestion failed", error=str(e))
        sys.exit(1)
