from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class MessageRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"

class Citation(BaseModel):
    document_name: str = Field(..., description="Name of the source document")
    page_number: int = Field(..., description="Page number where content was found")
    chunk_id: str = Field(..., description="Unique identifier of the chunk")
    snippet: str = Field(..., description="Extracted text snippet acting as evidence")
    score: float = Field(..., description="Similarity/Relevance score")

class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    total_pages: int
    total_chunks: int
    status: str = "indexed"

class ChatMessage(BaseModel):
    role: MessageRole
    content: str

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User question to query the document base")
    document_id: Optional[str] = Field(None, description="Optional filter to query a single specific document")
    enable_tts: bool = Field(False, description="Whether to synthesize audio response")

class ChatResponse(BaseModel):
    answer: str = Field(..., description="Grounded LLM synthesized response")
    citations: List[Citation] = Field(default_factory=list, description="List of source citations")
    audio_id: Optional[str] = Field(None, description="Cached TTS audio identifier if requested")

class TTSRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=4000)
    voice: str = Field("en-US-JennyNeural", description="Voice ID for synthesis")

class TTSResponse(BaseModel):
    audio_id: str
    audio_url: str
    cached: bool
