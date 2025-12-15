import os
import httpx
import logging
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class SpeechService:
    """Speech Service - DISABLED in offline mode"""
    
    def __init__(self):
        logger.warning("⚠️  Speech service DISABLED (offline mode)")
        logger.warning("   ElevenLabs requires internet connection")
        self.enabled = False
    
    async def text_to_speech(self, text: str) -> Optional[bytes]:
        """Text to speech - disabled offline"""
        logger.warning("Speech synthesis not available in offline mode")
        return None
    
    def is_available(self) -> bool:
        """Check if service is available"""
        return False


_speech_service: Optional[SpeechService] = None

def get_speech_service() -> SpeechService:
    global _speech_service
    if _speech_service is None:
        _speech_service = SpeechService()
    return _speech_service