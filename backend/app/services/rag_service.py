from typing import List, Dict, Any, AsyncGenerator
from openai import OpenAI
from app.core.config import settings
from app.services.vector_store_service import VectorStoreService
from app.services.tts_service import TTSService
from app.models.schemas import Citation, ChatResponse

SYSTEM_PROMPT = """You are DocuMindAI, a precise and factual Document Intelligence Assistant.
Your task is to answer the user's question using ONLY the provided context snippets.

Strict Grounding Rules:
1. Base your answer strictly on the provided context. Do NOT use prior world knowledge.
2. If the context does not contain enough information to answer the question, state:
   "I am sorry, but the provided documents do not contain sufficient information to answer this question."
3. Always refer to specific facts, numbers, or terms from the context.
4. Keep answers concise, clear, and professional.
"""

class RAGService:
    def __init__(self):
        self.vector_store = VectorStoreService()
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None

    def query(self, message: str, document_id: str = None, enable_tts: bool = False) -> ChatResponse:
        retrieved_chunks = self.vector_store.similarity_search(
            query=message,
            top_k=settings.TOP_K_RETRIEVAL,
            document_id=document_id
        )
        
        context_str = ""
        citations = []
        for c in retrieved_chunks:
            context_str += f"\n--- [Source: {c['filename']} | Page: {c['page_number']}] ---\n{c['text']}\n"
            citations.append(Citation(
                document_name=c["filename"],
                page_number=c["page_number"],
                chunk_id=c["chunk_id"],
                snippet=c["text"][:200] + "...",
                score=c["score"]
            ))
            
        user_prompt = f"Context:\n{context_str}\n\nUser Question: {message}\n\nAnswer:"
        
        if not self.client:
            answer = f"[Mock Mode - Set OPENAI_API_KEY to get real LLM output]\nAnswer based on {len(citations)} chunks retrieved."
        else:
            response = self.client.chat.completions.create(
                model=settings.LLM_MODEL,
                temperature=settings.LLM_TEMPERATURE,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ]
            )
            answer = response.choices[0].message.content
            
        audio_id = None
        if enable_tts:
            audio_id = TTSService.compute_hash(answer)
            
        return ChatResponse(answer=answer, citations=citations, audio_id=audio_id)

    async def stream_query(self, message: str, document_id: str = None) -> AsyncGenerator[str, None]:
        retrieved_chunks = self.vector_store.similarity_search(
            query=message,
            top_k=settings.TOP_K_RETRIEVAL,
            document_id=document_id
        )
        
        context_str = ""
        for c in retrieved_chunks:
            context_str += f"\n--- [Source: {c['filename']} | Page: {c['page_number']}] ---\n{c['text']}\n"
            
        user_prompt = f"Context:\n{context_str}\n\nUser Question: {message}\n\nAnswer:"
        
        if not self.client:
            yield "data: [Mock Mode Stream] Real-time streaming response token 1 2 3...\n\n"
            return

        stream = self.client.chat.completions.create(
            model=settings.LLM_MODEL,
            temperature=settings.LLM_TEMPERATURE,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            stream=True
        )
        for chunk in stream:
            token = chunk.choices[0].delta.content or ""
            if token:
                # SSE formatting
                yield f"data: {token}\n\n"
