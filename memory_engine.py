import chromadb
from chromadb.utils import embedding_functions
import re

# Global variables initialized as None
_client = None
_collection = None

def get_memory_collection():
    """Lazy loads the Chroma database safely using the stable default embedder."""
    global _client, _collection
    if _collection is None:
        _client = chromadb.PersistentClient(path="./nexus_memory")
        _collection = _client.get_or_create_collection(
            name="code_logic", 
            metadata={"hnsw:space": "cosine"}
        )
    return _collection

def slice_code(content):
    """
    Advanced Multi-Language Chunker.
    Splits codebase assets across Python declarations and modern JavaScript variables.
    """
    pattern = r'\n(?=async def |def |class |const |let |var |function |export )'
    chunks = re.split(pattern, content)
    
    if len(chunks) <= 1:
        chunks = content.split("\n\n")
        
    return [c.strip() for c in chunks if c.strip()]

def index_project_file(file_path: str, content: str):
    try:
        coll = get_memory_collection()
        chunks = slice_code(content)
        if not chunks:
            return f"Skipped empty file: {file_path}"
            
        ids = [f"{file_path}_chunk_{i}" for i in range(len(chunks))]
        metadatas = [{"source": file_path} for _ in chunks]
        
        coll.upsert(ids=ids, documents=chunks, metadatas=metadatas)
        return f"Successfully indexed {len(chunks)} chunks from {file_path}"
    except Exception as e:
        return f"Index error for {file_path}: {str(e)}"

def search_memory(query: str):
    try:
        coll = get_memory_collection()
        results = coll.query(query_texts=[query], n_results=4) # Bumped context depth limits to 4 for rich text scripts
        
        if not results or not results['documents'] or not results['documents'][0]:
            return "No matching code logic found in memory."
            
        formatted_results = []
        for doc, meta in zip(results['documents'][0], results['metadatas'][0]):
            formatted_results.append(f"--- File: {meta['source']} ---\n{doc}\n")
        return "\n".join(formatted_results)
    except Exception as e:
        return f"Memory search failed: {str(e)}"