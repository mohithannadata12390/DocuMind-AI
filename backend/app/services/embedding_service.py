from typing import List
from openai import OpenAI
from app.core.config import settings

class EmbeddingService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None
        self.model = settings.EMBEDDING_MODEL

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generates vector embeddings for a list of text strings via OpenAI API.
        """
        if not self.client:
            # Fallback zero vectors for local testing without API key
            return [[0.0] * settings.EMBEDDING_DIMENSION for _ in texts]
            
        # Clean text inputs
        sanitized_texts = [t.replace("\n", " ") for t in texts]
        response = self.client.embeddings.create(
            input=sanitized_texts,
            model=self.model
        )
        return [data.embedding for data in response.data]

    def get_query_embedding(self, query: str) -> List[float]:
        return self.get_embeddings([query])[0]