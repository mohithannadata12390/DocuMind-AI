import uuid
from typing import List, Dict, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.core.config import settings

class ChunkingService:
    def __init__(self, chunk_size: int = settings.CHUNK_SIZE, chunk_overlap: int = settings.CHUNK_OVERLAP):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", " ", ""],
            length_function=len
        )

    def create_chunks(self, pages_data: List[Dict[str, Any]], document_id: str) -> List[Dict[str, Any]]:
        """
        Splits extracted page texts into semantic chunks while maintaining provenance.
        """
        chunks = []
        for page_info in pages_data:
            page_num = page_info["page_number"]
            filename = page_info["filename"]
            raw_text = page_info["text"]
            
            split_texts = self.splitter.split_text(raw_text)
            for chunk_idx, text_segment in enumerate(split_texts):
                chunk_id = f"{document_id}_p{page_num}_c{chunk_idx}_{uuid.uuid4().hex[:6]}"
                chunks.append({
                    "chunk_id": chunk_id,
                    "document_id": document_id,
                    "filename": filename,
                    "page_number": page_num,
                    "text": text_segment
                })
        return chunks
