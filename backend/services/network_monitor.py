import logging
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict
from core.config import get_settings

logger = logging.getLogger(__name__)

class NetworkMonitor:
    """Monitor network connectivity and service availability"""
    
    def __init__(self):
        self.settings = get_settings()
        self._last_check: Optional[datetime] = None
        self._last_status: Optional[Tuple[bool, bool]] = None  # (online, ollama)
        self._cache_duration = timedelta(seconds=self.settings.CACHE_NETWORK_STATUS)
    
    async def check_online_api(self) -> bool:
        """Check if online API (OpenRouter) is available"""
        if not self.settings.OPENROUTER_API_KEY:
            return False
        
        try:
            timeout = aiohttp.ClientTimeout(total=self.settings.NETWORK_CHECK_TIMEOUT)
            headers = {
                "Authorization": f"Bearer {self.settings.OPENROUTER_API_KEY}",
                "HTTP-Referer": self.settings.SITE_URL,
            }
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(
                    self.settings.NETWORK_CHECK_URL,
                    headers=headers
                ) as response:
                    return response.status == 200
        except Exception as e:
            logger.debug(f"Online API check failed: {e}")
            return False
    
    async def check_ollama(self) -> bool:
        """Check if Ollama is available"""
        try:
            timeout = aiohttp.ClientTimeout(total=self.settings.NETWORK_CHECK_TIMEOUT)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(self.settings.OLLAMA_CHECK_URL) as response:
                    return response.status == 200
        except Exception as e:
            logger.debug(f"Ollama check failed: {e}")
            return False
    
    async def check_services(self, use_cache: bool = True) -> Tuple[bool, bool]:
        """
        Check availability of both services
        Returns: (online_available, ollama_available)
        """
        # Use cache if available and not expired
        if use_cache and self._last_check:
            age = datetime.now() - self._last_check
            if age < self._cache_duration and self._last_status:
                return self._last_status
        
        # Check both services in parallel
        online_available, ollama_available = await asyncio.gather(
            self.check_online_api(),
            self.check_ollama()
        )
        
        # Update cache
        self._last_check = datetime.now()
        self._last_status = (online_available, ollama_available)
        
        return online_available, ollama_available
    
    async def get_best_mode(self) -> str:
        """
        Determine the best mode to use
        Returns: 'online', 'offline', or 'none'
        """
        online_ok, ollama_ok = await self.check_services()
        
        if self.settings.PREFER_ONLINE and online_ok:
            logger.info("✅ Using ONLINE mode (preferred)")
            return "online"
        elif ollama_ok:
            logger.info("⚡ Using OFFLINE mode (Ollama available)")
            return "offline"
        elif online_ok:
            logger.info("🌐 Using ONLINE mode (Ollama unavailable)")
            return "online"
        else:
            logger.error("❌ No LLM services available!")
            return "none"
    
    def invalidate_cache(self):
        """Force a fresh check on next call"""
        self._last_check = None
        self._last_status = None


# Global instance
_network_monitor: Optional[NetworkMonitor] = None

def get_network_monitor() -> NetworkMonitor:
    """Get or create network monitor instance"""
    global _network_monitor
    if _network_monitor is None:
        _network_monitor = NetworkMonitor()
    return _network_monitor