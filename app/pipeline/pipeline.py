import sys
from pathlib import Path

# Ensure project root is on sys.path when run as a script
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.ingestion.loader import partition_document
from app.ingestion.chunker import chunk_elements_by_title, summarise_chunks
from app.ingestion.embedder import create_vector_store


def run_complete_ingestion_pipeline(pdf_path: str, persist_directory: str = "vector_store/chroma_db"):
    """Run the complete RAG ingestion pipeline and return a persisted Chroma DB."""
    print("Starting RAG Ingestion Pipeline")
    print("=" * 50)

    elements = partition_document(pdf_path)
    chunks = chunk_elements_by_title(elements)
    summarised_chunks = summarise_chunks(chunks)

    db = create_vector_store(summarised_chunks, persist_directory=persist_directory)

    print("Pipeline completed successfully!")
    return db


if __name__ == "__main__":
    db=run_complete_ingestion_pipeline("data/attention-is-all-you-need.pdf")
