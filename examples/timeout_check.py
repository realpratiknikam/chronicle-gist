import os
import sys
import asyncio
import time
from dotenv import load_dotenv

load_dotenv()

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from chronicle_gist.core import Chronicle

async def main():
    api_key = os.getenv("GROQ_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Please set GROQ_API_KEY or OPENAI_API_KEY")
        return

    # Use a real model but force a timeout
    chronicle = Chronicle(
        api_key=api_key,
        model_name="groq/llama-3.1-8b-instant",
        token_threshold=10 # Force bloat
    )

    session_id = "timeout_test"
    history = [{"role": "user", "content": "A short message."}] * 10 # 50-60 tokens
    new_msg = {"role": "user", "content": "Trigger bloat."}

    print("--- Testing Timeout (1ms) ---")
    # This should timeout immediately
    result = await chronicle.process_async(session_id, new_msg, history, timeout=1)

    print(f"Bloat Detected: {result['meta']['bloat_detected']}")
    print(f"Timed Out: {result['meta']['timed_out']}")
    print(f"Strategy: {result['meta']['strategy']}")
    
    if result['meta']['timed_out']:
        print("✅ SUCCESS: Timeout triggered.")
    else:
        print("❌ FAILURE: Did not timeout.")

if __name__ == "__main__":
    asyncio.run(main())
