import os
import sys
import asyncio
import time
from dotenv import load_dotenv

load_dotenv()

# Add parent directory to path so we can import chronicle without installing
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from chronicle_gist.core import Chronicle

async def main():
    api_key = os.getenv("GROQ_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Please set GROQ_API_KEY or OPENAI_API_KEY")
        return

    chronicle = Chronicle(
        api_key=api_key,
        model_name="groq/llama-3.1-8b-instant",
        token_threshold=50
    )

    session_id = "async_test_user"
    
    history = [
        {"role": "user", "content": "I am testing async support."},
        {"role": "assistant", "content": "That is great! Async is efficient."},
        {"role": "user", "content": "It allows concurrency."},
        {"role": "assistant", "content": "Yes, especially for I/O bound tasks."},
        {"role": "user", "content": "Like calling an LLM API."}
    ]
    
    new_message = {"role": "user", "content": "Exactly. Let's see if this blocks."}
    
    print(f"--- Starting Async Test for {session_id} ---")
    start = time.time()
    
    # This should await the result
    result = await chronicle.process_async(session_id, new_message, history)
    
    duration = time.time() - start
    print(f"Async Process took {duration:.2f}s")
    
    print("\n--- Result Metadata ---")
    print(f"Bloat Detected: {result['meta']['bloat_detected']}")
    print(f"Latency: {result['meta']['latency_ms']}ms")
    print(f"Strategy: {result['meta']['strategy']}")

if __name__ == "__main__":
    asyncio.run(main())
