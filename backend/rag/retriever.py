import os
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings


from backend.config import FAISS_INDEX_PATH, EMBEDDING_MODEL, TOP_K

def get_retriever():
    if not os.path.exists(FAISS_INDEX_PATH):
        raise ValueError("Chưa có FAISS index. Hãy upload tài liệu trước.")

    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

    vectorstore = FAISS.load_local(
        FAISS_INDEX_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )

    return vectorstore.as_retriever(search_kwargs={"k": TOP_K})
