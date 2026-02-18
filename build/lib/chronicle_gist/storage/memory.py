import time
from typing import Dict, Optional, Any
from .base import Storage

class InMemoryStorage(Storage):
    """
    In-Memory implementation of Storage using a Python dictionary.
    Includes basic TTL (Time To Live) support to clean up old sessions.
    """

    def __init__(self, ttl_seconds: int = 3600):
        self._store: Dict[str, Dict[str, Any]] = {}
        self._ttl = ttl_seconds

    def _is_expired(self, session: Dict[str, Any]) -> bool:
        return (time.time() - session["updated_at"]) > self._ttl

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        session = self._store.get(session_id)
        
        if not session:
            return None
            
        if self._is_expired(session):
            del self._store[session_id]
            return None
            
        return session

    def save_session(self, session_id: str, summary: str, fact_ledger: Dict[str, Any]) -> None:
        self._store[session_id] = {
            "summary": summary,
            "fact_ledger": fact_ledger,
            "updated_at": time.time()
        }

    async def aget_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        return self.get_session(session_id)

    async def asave_session(self, session_id: str, summary: str, fact_ledger: Dict[str, Any]) -> None:
        return self.save_session(session_id, summary, fact_ledger)
