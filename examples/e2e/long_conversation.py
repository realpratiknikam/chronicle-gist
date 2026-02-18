import os
import sys
import asyncio
import json
from dotenv import load_dotenv

load_dotenv()

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from chronicle_gist.core import Chronicle

def print_insights(turn_num, result):
    """Prints a clear summary of what Chronicle learned."""
    meta = result["meta"]
    print(f"\n   📊 ADJUSTING MEMORY (Turn {turn_num})")
    print("   " + "-" * 40)
    
    # 1. State Size
    saved = meta.get('tokens_saved', 0)
    if saved > 0:
        print(f"   📉 Tokens Saved:   {saved} (COMPRESSED!)")
    else:
         print(f"   📉 Tokens Saved:   {saved} (Buffer filling...)")

    # 2. Fact Ledger (The "Smart" Part)
    ledger = meta.get("fact_ledger", {})
    if ledger:
        print("\n   🧠 KNOWN FACTS (Source of Truth):")
        # Pretty print JSON with indentation
        ledger_json = json.dumps(ledger, indent=4)
        for line in ledger_json.splitlines():
            print(f"      {line}")
    else:
        print("\n   🧠 KNOWN FACTS: (None yet)")

    print("   " + "-" * 40 + "\n")

async def simulate_turn(chronicle, session_id, turn_num, user_input, history):
    print(f"👤 USER: \"{user_input}\"")
    
    new_msg = {"role": "user", "content": user_input}
    
    # 1. Chronicle optimizes the context
    result = await chronicle.process_async(session_id, new_msg, history)
    
    print_insights(turn_num, result)
    
    hydrated_msgs = result["hydrated_messages"]
    meta = result["meta"]
    ledger = meta.get("fact_ledger", {})

    # 2. Simulate Assistant Response (Mock Logic utilizing the ledger)
    assistant_response = "I can help with that."
    
    if "running" in user_input.lower():
         assistant_response = "That's a great goal! Marathon training requires good support. Let's look at some long-distance runners."
    elif "budget" in user_input.lower():
         assistant_response = f"Understood. We will stick strictly to your ${ledger.get('budget', '150')} limit."
    elif "nike" in user_input.lower():
         assistant_response = "Nike has some excellent options for that usage. I'll filter for that brand."
    elif "red" in user_input.lower():
         assistant_response = f"Bold choice! Looking for Red Nike runners, size {ledger.get('shoe_size', 'N/A')}."
    elif "shipping" in user_input.lower():
        assistant_response = f"I'll prepare shipment to {ledger.get('city', 'your location')}. Standard shipping is free for orders over $100."

    print(f"🤖 AI: \"{assistant_response}\"\n")
    print("=" * 60 + "\n")
    
    # 3. Update History
    history.append(new_msg)
    history.append({"role": "assistant", "content": assistant_response})
    
    return history

async def main():
    api_key = os.getenv("GROQ_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  Please set GROQ_API_KEY or OPENAI_API_KEY in .env file")
        return

    print("\n🚀 Starting Verbose Smart Shopping Demo")
    print("   Scenario: CHATTY User looking for running shoes.")
    print("   Goal: Force 'Tokens Saved' > 0 by filling the buffer.\n")
    print("=" * 60 + "\n")

    # Initialize Chronicle
    # Low threshold + Chatty user = Guaranteed Compression
    chronicle = Chronicle(
        api_key=api_key,
        model_name="groq/llama-3.1-8b-instant", 
        token_threshold=50 
    )

    session_id = "shopper_verbose_1"
    history = []

    # Turn 1: Verbose Intent
    history = await simulate_turn(
        chronicle, session_id, 1,
        "Hi there! I've recently decided to get back into shape after a long hiatus. "
        "I used to run 5ks back in college but stopped for a few years. "
        "Now I want to train for a half-marathon next summer, so I need a really reliable pair of running shoes "
        "that can handle long distances on pavement.", 
        history
    )

    # Turn 2: Budget with Backstory (Fact)
    history = await simulate_turn(
        chronicle, session_id, 2,
        "As for my budget, things are a bit tight right now with the renovations. "
        "I really cannot go over $150. Even $160 would be pushing it too much, "
        "so please keep it strictly under $150 including tax if possible.", 
        history
    )

    # Turn 3: Brand Loyalty (Fact)
    history = await simulate_turn(
        chronicle, session_id, 3,
        "I've always had good luck with Nike in the past. "
        "My last pair was a Pegasus and they lasted forever. "
        "So I'd prefer to stick with Nike if they have something in my price range. "
        "I don't really trust other brands right now.", 
        history
    )
    
    # Turn 4: Size and Specifics (Fact)
    # By this point, history is likely > 50 tokens, so we might see compression kicking in soon.
    history = await simulate_turn(
        chronicle, session_id, 4,
        "Oh, and I have wide feet, so I need a size 10.5 Wide if possible. "
        "Also, I hate boring colors. I really want something bright, maybe Red or Neon Green. "
        "Visibility is important since I run at night.", 
        history
    )

    # Turn 5: Checkout / Location (Fact)
    history = await simulate_turn(
        chronicle, session_id, 5,
        "That sounds perfect. How much is shipping to Springfield, IL? "
        "I need them by next week for a training group starting up.",
        history
    )

    print("✅ Demo Complete.")

if __name__ == "__main__":
    asyncio.run(main())
