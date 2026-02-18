import os
import sys
import asyncio
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()


# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from chronicle_gist.core import Chronicle
from chronicle_gist.storage.postgres import PostgresStorage
from chronicle_gist.storage.redis_adapter import RedisStorage
from chronicle_gist.storage.mongo import MongoStorage

async def test_postgres(api_key: str):
    print("\n--- Testing Postgres Adapter ---")
    # You need a running Postgres instance
    try:
        dsn = "postgresql://chronicle:password@localhost:5432/chronicle_db"
        storage = PostgresStorage(dsn)
        await storage.connect()
        
        chronicle = Chronicle(api_key=api_key, storage=storage, token_threshold=50)
        result = await chronicle.process_async(
            "postgres_user", 
            {"role": "user", "content": "I store my memories in SQL."},
            [{"role": "assistant", "content": "Relational data is solid."}]
        )
        print(f"Postgres Result: {result['meta']['bloat_detected']}")
        await storage.disconnect()
    except Exception as e:
        print(f"Skipping Postgres test (DB likely not up): {e}")

async def test_redis(api_key: str):
    print("\n--- Testing Redis Adapter ---")
    try:
        url = "redis://localhost:6379/0"
        storage = RedisStorage(url)
        await storage.connect()
        
        chronicle = Chronicle(api_key=api_key, storage=storage, token_threshold=50)
        result = await chronicle.process_async(
            "redis_user", 
            {"role": "user", "content": "I am fast like cache."},
            [{"role": "assistant", "content": "Speed is key."}]
        )
        print(f"Redis Result: {result['meta']['bloat_detected']}")
        await storage.disconnect()
    except Exception as e:
        print(f"Skipping Redis test: {e}")

async def test_mongo(api_key: str):
    print("\n--- Testing Mongo Adapter ---")
    try:
        uri = "mongodb://localhost:27017"
        storage = MongoStorage(uri)
        await storage.connect()
        
        chronicle = Chronicle(api_key=api_key, storage=storage, token_threshold=50)
        result = await chronicle.process_async(
            "mongo_user", 
            {"role": "user", "content": "I am web scale."},
            [{"role": "assistant", "content": "Documents are flexible."}]
        )
        print(f"Mongo Result: {result['meta']['bloat_detected']}")
    except Exception as e:
        print(f"Skipping Mongo test: {e}")

async def main():
    api_key = os.getenv("GROQ_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Please set GROQ_API_KEY")
        return

    await test_postgres(api_key)
    await test_redis(api_key)
    # await test_mongo(api_key) # Uncomment if Mongo is running

if __name__ == "__main__":
    asyncio.run(main())
