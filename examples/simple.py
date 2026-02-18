import os
import sys

# Add parent directory to path so we can import chronicle without installing
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from chronicle_gist.core import Chronicle

def main():
    # 1. Initialize Chronicle
    # You need an API key for the "Worker LLM" (summarizer)
    # We use Groq by default for speed, but you can change model_name="gpt-4o"
    api_key = os.getenv("GROQ_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Please set GROQ_API_KEY or OPENAI_API_KEY")
        return

    chronicle = Chronicle(
        api_key=api_key,
        model_name="groq/llama-3.1-8b-instant", # Or "gpt-3.5-turbo"
        token_threshold=50 # Low threshold for testing
    )

    session_id = "test_user_1"
    
    # 2. Simulate a conversation
    print(f"--- Starting Session: {session_id} ---")

    history = [
        {"role": "user", "content": "Hi, I'm Alice. I am a software engineer."},
        {"role": "assistant", "content": "Hello Alice! Nice to meet you."},
        {"role": "user", "content": "I like Python and Rust."},
        {"role": "assistant", "content": "Great choices! Both are powerful languages."},
        {"role": "user", "content": "I am building a web app today."}
    ]
    
    # New message to process
    new_message = {"role": "user", "content": "Can you help me with a DB schema?"}
    
    print(f"Processing message: '{new_message['content']}'...")
    
    # 3. Process with Chronicle
    result = chronicle.process(session_id, new_message, history)
    
    # 4. Inspect Result
    print("\n--- Optimized Context ---")
    for msg in result["hydrated_messages"]:
        print(f"[{msg['role'].upper()}]: {msg['content'][:100]}...")
        
    print("\n--- Metadata ---")
    meta = result["meta"]
    print(f"Strategy: {meta.get('strategy')}")
    print(f"Bloat Detected: {meta.get('bloat_detected')}")
    print(f"Tokens Saved: {meta.get('tokens_saved')}")
    
    print("\n--- Fact Ledger ---")
    print(meta.get("fact_ledger"))

if __name__ == "__main__":
    main()
