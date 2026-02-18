import time
from typing import Dict, Optional, Any
from motor.motor_asyncio import AsyncIOMotorClient
from .base import Storage

class MongoStorage(Storage):
    """
    MongoDB storage adapter using Motor.
    Stores sessions in a collection `sessions` within the specified database.
    """

    def __init__(self, uri: str, db_name: str = "chronicle", collection_name: str = "sessions"):
        self.uri = uri
        self.db_name = db_name
        self.collection_name = collection_name
        self.client = None
        self.db = None
        self.collection = None

    async def connect(self):
        if not self.client:
            self.client = AsyncIOMotorClient(self.uri)
            self.db = self.client[self.db_name]
            self.collection = self.db[self.collection_name]

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        raise NotImplementedError("MongoStorage only supports async methods. Use aget_session.")

    def save_session(self, session_id: str, summary: str, fact_ledger: Dict[str, Any]) -> None:
        raise NotImplementedError("MongoStorage only supports async methods. Use asave_session.")

    async def aget_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        if not self.client:
            await self.connect()
            
        doc = await self.collection.find_one({"_id": session_id})
        if doc:
            return {
                "summary": doc.get("summary", ""),
                "fact_ledger": doc.get("fact_ledger", {}),
                "updated_at": doc.get("updated_at", time.time())
            }
        return None

    async def asave_session(self, session_id: str, summary: str, fact_ledger: Dict[str, Any]) -> None:
        if not self.client:
            await self.connect()
            
        await self.collection.update_one(
            {"_id": session_id},
            {
                "$set": {
                    "summary": summary,
                    "fact_ledger": fact_ledger,
                    "updated_at": time.time()
                }
            },
            upsert=True
        )
