import hashlib
from pathlib import Path
import edge_tts
from app.core.config import settings

class TTSService:
    @staticmethod
    def compute_hash(text: str, voice: str = "en-US-JennyNeural") -> str:
        """
        Generates a deterministic SHA-256 fingerprint for the text and voice combination.
        """
        key = f"{voice}:{text.strip()}"
        return hashlib.sha256(key.encode("utf-8")).hexdigest()

    @classmethod
    async def synthesize_or_get_cached(cls, text: str, voice: str = "en-US-JennyNeural") -> tuple[str, bool]:
        """
        Checks if audio already exists in tts_cache. If not, generates it asynchronously.
        Returns: (audio_id, is_cached)
        """
        audio_id = cls.compute_hash(text, voice)
        file_path = settings.TTS_CACHE_DIR / f"{audio_id}.mp3"
        
        if file_path.exists():
            return audio_id, True
            
        # Synthesize via edge-tts
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(str(file_path))
        return audio_id, False

    @staticmethod
    def get_audio_file_path(audio_id: str) -> Path | None:
        file_path = settings.TTS_CACHE_DIR / f"{audio_id}.mp3"
        if file_path.exists():
            return file_path
        return None
