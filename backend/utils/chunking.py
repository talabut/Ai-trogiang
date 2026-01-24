# backend/utils/chunking.py

import uuid
from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document


def chunk_text(
    text: str,
    source_file: str,
    page: int = None,
    section: str = None,
    chunk_size: int = 400,
    chunk_overlap: int = 80
) -> List[Document]:
    """
    Chunk text into Documents with full metadata
    """

    doc_id = str(uuid.uuid4())

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ".", " ", ""]
    )

    chunks = splitter.split_text(text)

    documents = []

    for idx, chunk in enumerate(chunks):
        metadata = {
            "doc_id": doc_id,
            "source_file": source_file,
            "page": page,
            "section": section,
            "chunk_id": idx
        }

        documents.append(
            Document(
                page_content=chunk,
                metadata=metadata
            )
        )

    return documents
