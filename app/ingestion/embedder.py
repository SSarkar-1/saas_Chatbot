from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma


def create_vector_store(documents, persist_directory: str = "vector_store/chroma_db"):
    """Create and persist ChromaDB vector store."""
    print("Creating vector store in ChromaDB")

    embeddings_model = OpenAIEmbeddings(model="text-embedding-3-small")

    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embeddings_model,
        persist_directory=persist_directory,
        collection_metadata={"hnsw:space": "cosine"},
    )

    print(f"Vector Store created and saved to {persist_directory}")
    return vectorstore
