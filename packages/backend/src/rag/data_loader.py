"""Data loader for ingesting news articles."""

import json
from pathlib import Path
from urllib.parse import urlparse

from langchain_core.documents import Document

from src.core.logging import get_logger

logger = get_logger(__name__)


def _extract_source_from_url(url: str) -> str:
    """Extract source domain from URL.

    Args:
        url: Article URL.

    Returns:
        Source domain (e.g., 'finance.yahoo.com').
    """
    try:
        parsed = urlparse(url)
        return parsed.netloc or "unknown"
    except Exception:
        return "unknown"


def load_json_data(file_path: str | Path) -> list[Document]:
    """Load news articles from JSON file into LangChain Documents.

    Handles two formats:
    1. Nested dict: {ticker: [{title, link, ticker, full_text}, ...]}
    2. Flat array: [{headline, content, ticker, source, link, date}, ...]

    Args:
        file_path: Path to JSON file containing news articles.

    Returns:
        List of LangChain Document objects.
    """
    file_path = Path(file_path)

    with open(file_path, encoding='utf-8') as f:
        data = json.load(f)

    documents = []
    skipped = 0

    # Check if data is nested dict (stock_news.json format)
    if isinstance(data, dict) and all(isinstance(v, list) for v in data.values()):
        # Nested format: {ticker: [articles]}
        for ticker, articles in data.items():
            for article in articles:
                # Required fields for nested format
                if not all(k in article for k in ["title", "link", "ticker", "full_text"]):
                    skipped += 1
                    continue

                # Skip empty content
                if not article.get("full_text", "").strip():
                    skipped += 1
                    continue

                # Extract source from URL
                source = _extract_source_from_url(article["link"])

                doc = Document(
                    page_content=article["full_text"],
                    metadata={
                        "headline": article["title"],
                        "ticker": article["ticker"],
                        "source": source,
                        "link": article["link"],
                        "date": "2025",  # Default date
                    }
                )
                documents.append(doc)

    elif isinstance(data, list):
        # Flat array format: [{headline, content, ticker, source, link, date}]
        required_fields = {"headline", "content", "ticker", "source", "link", "date"}

        for item in data:
            # Validate required fields
            if not required_fields.issubset(item.keys()):
                skipped += 1
                continue

            # Skip empty content
            if not item.get("content", "").strip():
                skipped += 1
                continue

            doc = Document(
                page_content=item["content"],
                metadata={
                    "headline": item["headline"],
                    "ticker": item["ticker"],
                    "source": item["source"],
                    "link": item["link"],
                    "date": item["date"],
                }
            )
            documents.append(doc)
    else:
        logger.error(
            "Invalid JSON format",
            file=str(file_path),
            expected="dict[str, list] or list[dict]",
        )
        return []

    logger.info(
        "Loaded documents",
        total=len(documents),
        skipped=skipped,
        file=str(file_path),
    )

    return documents


def chunk_documents(
    documents: list[Document],
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> list[Document]:
    """Split documents into smaller chunks.

    Args:
        documents: List of documents to chunk.
        chunk_size: Maximum size of each chunk.
        chunk_overlap: Overlap between chunks.

    Returns:
        List of chunked documents.
    """
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunked = splitter.split_documents(documents)

    logger.info(
        "Chunked documents",
        original=len(documents),
        chunked=len(chunked),
    )

    return chunked
