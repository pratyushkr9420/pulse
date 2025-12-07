"""Data loader for ingesting news articles."""

import json
from pathlib import Path

from langchain_core.documents import Document

from src.core.logging import get_logger

logger = get_logger(__name__)

REQUIRED_FIELDS = {"headline", "content", "ticker", "source", "link", "date"}


def load_json_data(file_path: str | Path) -> list[Document]:
    """Load news articles from JSON file into LangChain Documents.
    
    Args:
        file_path: Path to JSON file containing news articles.
        
    Returns:
        List of LangChain Document objects.
    """
    file_path = Path(file_path)
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    documents = []
    skipped = 0
    
    for item in data:
        # Validate required fields
        if not REQUIRED_FIELDS.issubset(item.keys()):
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
