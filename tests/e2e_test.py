import os
import sys
import unittest
import asyncio
import json
from unittest.mock import patch, MagicMock, AsyncMock
from chronicle_gist import Chronicle

# Ensure we can import the package if running from source
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

class TestChronicleE2E(unittest.TestCase):
    def setUp(self):
        self.api_key = os.getenv("GROQ_API_KEY") or os.getenv("OPENAI_API_KEY")
        self.model_name = "groq/llama-3.1-8b-instant" if os.getenv("GROQ_API_KEY") else "gpt-3.5-turbo"
        
        # If no key, we will rely on mocks
        self.use_mocks = not self.api_key
        if self.use_mocks:
            print("[E2E] No API Key found. Running in MOCK mode.")
            self.api_key = "mock_key"

    def test_e2e_compression(self):
        """
        Test that Chronicle can process a conversation, detect bloat (forced),
        and return a hydrated system prompt with a fact ledger.
        """
        async def run_test():
            chronicle = Chronicle(
                api_key=self.api_key,
                model_name=self.model_name,
                token_threshold=10  # Force compression by setting very low threshold
            )

            history = [
                {"role": "user", "content": "My name is E2E Test User. I am testing the Chronicle library."},
                {"role": "assistant", "content": "Hello! I am ready to be tested."},
                {"role": "user", "content": "I live in the Cloud and my favorite color is #00FF00."},
                {"role": "assistant", "content": "That is a very digital color."},
            ]
            
            new_msg = {"role": "user", "content": "What is my name and favorite color?"}
            
            print(f"\n[E2E] Processing with model: {self.model_name}")

            # Define the mock response for compression
            mock_response_content = json.dumps({
                "summary": "User E2E Test User is testing Chronicle. Lives in Cloud, likes #00FF00.",
                "fact_ledger": {
                    "name": "E2E Test User",
                    "location": "Cloud",
                    "favorite_color": "#00FF00"
                }
            })
            
            # Context manager for mocking
            if self.use_mocks:
                # Mock token counter to ensure bloat detection (return > 10)
                # Mock acompletion to return the JSON above
                with patch("litellm.token_counter", return_value=100) as mock_count, \
                     patch("litellm.acompletion", new_callable=AsyncMock) as mock_completion:
                    
                    # Setup mock completion response structure
                    mock_choice = MagicMock()
                    mock_choice.message.content = mock_response_content
                    mock_response = MagicMock()
                    mock_response.choices = [mock_choice]
                    
                    mock_completion.return_value = mock_response

                    result = await chronicle.process_async("session_e2e_1", new_msg, history)
                    
                    print(f"Mock completion called: {mock_completion.called}")
                    if mock_completion.called:
                        print(f"Mock completion call args: {mock_completion.call_args}")
            else:
                # Real execution
                result = await chronicle.process_async("session_e2e_1", new_msg, history)
            
            print(f"Full Result: {json.dumps(result, indent=2, default=str)}")

            # Validation
            self.assertIn("hydrated_messages", result)
            self.assertIn("meta", result)
            
            meta = result["meta"]
            self.assertTrue(meta.get("bloat_detected"), "Bloat should be detected with low threshold")
            
            # Check for Fact Ledger in system prompt
            system_msgs = [m for m in result["hydrated_messages"] if m["role"] == "system"]
            self.assertTrue(len(system_msgs) > 0, "Should have at least one system message")
            
            # We expect the fact ledger to extract name or color
            fact_ledger = meta.get("fact_ledger", {})
            print(f"[E2E] Fact Ledger Detected: {fact_ledger}")
            
            self.assertIsInstance(fact_ledger, dict)
            if self.use_mocks:
                self.assertEqual(fact_ledger.get("name"), "E2E Test User")

        asyncio.run(run_test())

if __name__ == '__main__':
    unittest.main()
