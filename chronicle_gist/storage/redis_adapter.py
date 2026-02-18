import json
import time
from typing import Dict, Optional, Any
import redis.asyncio as redis
from .base import Storage

class RedisStorage(Storage):
    """
    Redis storage adapter using redis-py.
    Models sessions as a JSON string stored under key `chronicle:session:{id}`.
    """

    def __init__(self, url: str, ttl: int = 3600):
        self.url = url
        self.ttl = ttl
        self.client = None

    async def connect(self):
        if not self.client:
            self.client = redis.from_url(self.url)

    async def disconnect(self):
        if self.client:
            await self.client.close()

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        raise NotImplementedError("RedisStorage only supports async methods. Use aget_session.")

    def save_session(self, session_id: str, summary: str, fact_ledger: Dict[str, Any]) -> None:
        raise NotImplementedError("RedisStorage only supports async methods. Use asave_session.")

    async def aget_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        if not self.client:
            await self.connect()
            
        data = await self.client.get(f"chronicle:session:{session_id}")
        if data:
            return json.loads(data)
        return None

    async def asave_session(self, session_id: str, summary: str, fact_ledger: Dict[str, Any]) -> None:
        if not self.client:
            await self.connect()
            
        state = {
            "summary": summary,
            "fact_ledger": fact_ledger,
            "updated_at": time.time()
        }
        await self.client.setex(f"chronicle:session:{session_id}", self.ttl, json.dumps(state))
