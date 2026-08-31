from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from app.core.config import settings
from app.services.embedding_service import EmbeddingService

class VectorStoreService:
    def __init__(self):
        self.chroma_client = chromadb.PersistentClient(
            path=str(settings.CHROMA_DB_DIR),
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        self.collection = self.chroma_client.get_or_create_collection(
            name="documind_collection",
            metadata={"hnsw:space": "cosine"}
        )
        self.embedding_service = EmbeddingService()

    def add_chunks(self, chunks: List[Dict[str, Any]]):
        if not chunks:
            return
            
        texts = [c["text"] for c in chunks]
        ids = [c["chunk_id"] for c in chunks]
        metadatas = [
            {
                "document_id": c["document_id"],
                "filename": c["filename"],
                "page_number": c["page_number"]
            }
            for c in chunks
        ]
        
        embeddings = self.embedding_service.get_embeddings(texts)
        
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas
        )

    def similarity_search(self, query: str, top_k: int = settings.TOP_K_RETRIEVAL, document_id: Optional[str] = None) -> List[Dict[str, Any]]:
        query_embedding = self.embedding_service.get_query_embedding(query)
        
        where_filter = {"document_id": document_id} if document_id else None
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_filter,
            include=["documents", "metadatas", "distances"]
        )
        
        retrieved_docs = []
        if results and results["documents"] and len(results["documents"][0]) > 0:
            for idx in range(len(results["documents"][0])):
                doc_text = results["documents"][0][idx]
                meta = results["metadatas"][0][idx]
                chunk_id = results["ids"][0][idx]
                distance = results["distances"][0][idx]
                score = 1.0 - distance  # Cosine similarity conversion
                
                retrieved_docs.append({
                    "chunk_id": chunk_id,
                    "text": doc_text,
                    "filename": meta.get("filename", "unknown"),
                    "page_number": meta.get("page_number", 1),
                    "document_id": meta.get("document_id", ""),
                    "score": round(score, 4)
                })
        return retrieved_docs
