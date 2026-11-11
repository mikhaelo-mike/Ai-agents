from pathlib import Path

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter


DEFAULT_KNOWLEDGE_FILE = (
    Path(__file__).resolve().parents[2] / "data" / "company_info.md"
)


def load_documents(
    file_path: Path = DEFAULT_KNOWLEDGE_FILE,
) -> list[Document]:
    if not file_path.is_file():
        raise FileNotFoundError(f"Company knowledge file not found: {file_path}")

    content = file_path.read_text(encoding="utf-8").strip()
    if not content:
        raise ValueError(f"Company knowledge file is empty: {file_path}")

    document = Document(
        page_content=content,
        metadata={"source": file_path.name},
    )
    splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=100)
    return splitter.split_documents([document])


def build_retriever(embeddings: Embeddings):
    documents = load_documents()
    vector_store = InMemoryVectorStore.from_documents(documents, embeddings)
    return vector_store.as_retriever(search_kwargs={"k": 3})
