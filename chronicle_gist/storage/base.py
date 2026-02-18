from abc import ABC, abstractmethod
from typing import Dict, Optional, Any

class Storage(ABC):
    """
    Abstract Base Class for Chronicle Storage.
    Manages persistence of Session State (Summary + Facts).
    """

    @abstractmethod
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve session state.
        Returns None if not found.
        Expected return format:
        {
            "summary": str,
            "fact_ledger": dict,
            "updated_at": float
        }
        """
        pass

    @abstractmethod
    def save_session(self, session_id: str, summary: str, fact_ledger: Dict[str, Any]) -> None:
        """
        Save or update session state.
        """
        pass

    @abstractmethod
    async def aget_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Async retrieve session state.
        """
        pass

    @abstractmethod
    async def asave_session(self, session_id: str, summary: str, fact_ledger: Dict[str, Any]) -> None:
        """
        Async save or update session state.
        """
        pass
