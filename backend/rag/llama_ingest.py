# FILE: backend/rag/llama_ingest.py
import os
import faiss
from typing import List, Set

from llama_index.core import (
    VectorStoreIndex, 
    StorageContext, 
    load_index_from_storage
)
from llama_index.vector_stores.faiss import FaissVectorStore

# Import internal modules
from backend.rag.llama_config import get_embedding_model
from backend.rag.node_parser import convert_chunks_to_nodes

# Path for Index Storage
INDEX_ROOT_DIR = "data/llama_index"

def get_index_path(course_id: str) -> str:
    return os.path.join(INDEX_ROOT_DIR, course_id)

def get_or_create_index(course_id: str, vector_dim: int = 384) -> VectorStoreIndex:
    """
    Load existing index or create new one with FAISS backend.
    """
    persist_dir = get_index_path(course_id)
    
    # 1. Try Loading Existing Index
    if os.path.exists(persist_dir) and os.path.exists(os.path.join(persist_dir, "docstore.json")):
        try:
            vector_store = FaissVectorStore.from_persist_dir(persist_dir)
            storage_context = StorageContext.from_defaults(
                vector_store=vector_store, 
                persist_dir=persist_dir
            )
            index = load_index_from_storage(storage_context, embed_model=get_embedding_model())
            return index
        except Exception as e:
            print(f"⚠️ Error loading index: {e}. Recreating...")
    
    # 2. Create New Index if load failed or not exists
    print(f"🆕 Creating new LlamaIndex for {course_id}...")
    faiss_index = faiss.IndexFlatL2(vector_dim)
    vector_store = FaissVectorStore(faiss_index=faiss_index)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    
    index = VectorStoreIndex(
        nodes=[], 
        storage_context=storage_context, 
        embed_model=get_embedding_model()
    )
    return index

# FIX: Implement get_llama_retriever để module retrieval gọi
def get_llama_retriever(course_id: str, top_k: int = 10):
    """Helper để lấy retriever từ index đã persist"""
    index = get_or_create_index(course_id)
    return index.as_retriever(similarity_top_k=top_k)

def ingest_canonical_chunks(
    chunks: List[dict], 
    course_id: str, 
    file_name: str,
    doc_id: str
):
    """
    Main Pipeline: Chunk -> Node -> Deduplicate -> Index -> Persist
    """
    persist_dir = get_index_path(course_id)

    # 1. Convert to LlamaIndex Nodes
    new_nodes = convert_chunks_to_nodes(chunks, doc_id, file_name)
    
    if not new_nodes:
        print("⚠️ No valid nodes to ingest.")
        return None

    # 2. Initialize/Load Index
    index = get_or_create_index(course_id)
    
    # 3. Deduplication Logic (Strict Check)
    existing_hashes: Set[str] = set()
    try:
        for node_id in index.docstore.docs.keys():
            existing_hashes.add(node_id)
    except Exception:
        pass 

    nodes_to_insert = []
    skipped_count = 0

    for node in new_nodes:
        if node.node_id in existing_hashes:
            skipped_count += 1
            continue
        
        nodes_to_insert.append(node)
        existing_hashes.add(node.node_id) 

    if skipped_count > 0:
        print(f"🔎 Dedup check: Skipped {skipped_count} duplicate chunks.")

    # 4. Insert Nodes & Persist
    if nodes_to_insert:
        index.insert_nodes(nodes_to_insert)
        print(f"✅ Inserted {len(nodes_to_insert)} new nodes.")
        
        if not os.path.exists(persist_dir):
            os.makedirs(persist_dir)
        
        index.storage_context.persist(persist_dir=persist_dir)
        print(f"💾 Index saved to {persist_dir}")
    else:
        print("⏩ No new unique nodes to index.")

    return index