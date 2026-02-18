import json
import time
from typing import Dict, Optional, Any
import asyncpg
from .base import Storage

class PostgresStorage(Storage):
    """
    PostgreSQL storage adapter using asyncpg.
    Requires a table `chronicle_sessions` with columns:
    - id (TEXT PRIMARY KEY)
    - summary (TEXT)
    - fact_ledger (JSONB)
    - updated_at (FLOAT)
    """

    def __init__(self, dsn: str):
        self.dsn = dsn
        self.pool = None

    async def connect(self):
        if not self.pool:
            self.pool = await asyncpg.create_pool(self.dsn)
            # Ensure table exists
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS chronicle_sessions (
                        id TEXT PRIMARY KEY,
                        summary TEXT,
                        fact_ledger JSONB,
                        updated_at FLOAT
                    );
                """)

    async def disconnect(self):
        if self.pool:
            await self.pool.close()

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        raise NotImplementedError("PostgresStorage only supports async methods. Use aget_session.")

    def save_session(self, session_id: str, summary: str, fact_ledger: Dict[str, Any]) -> None:
        raise NotImplementedError("PostgresStorage only supports async methods. Use asave_session.")

    async def aget_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        if not self.pool:
            await self.connect()
            
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("SELECT summary, fact_ledger, updated_at FROM chronicle_sessions WHERE id = $1", session_id)
            if row:
                return {
                    "summary": row["summary"],
                    "fact_ledger": json.loads(row["fact_ledger"]) if isinstance(row["fact_ledger"], str) else row["fact_ledger"],
                    "updated_at": row["updated_at"]
                }
            return None

    async def asave_session(self, session_id: str, summary: str, fact_ledger: Dict[str, Any]) -> None:
        if not self.pool:
            await self.connect()
            
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO chronicle_sessions (id, summary, fact_ledger, updated_at)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (id) DO UPDATE 
                SET summary = $2, fact_ledger = $3, updated_at = $4
            """, session_id, summary, json.dumps(fact_ledger), time.time())
