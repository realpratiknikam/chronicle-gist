from typing import List, Dict, Union
import litellm
from .base import LLMProvider

class LitellmProvider(LLMProvider):
    """
    Default implementation using the `litellm` library.
    Supports OpenAI, Anthropic, Groq, etc. out of the box.
    """

    def __init__(self, api_key: str = None):
        # litellm reads from os.environ widely, but we can set it explicitly if needed
        if api_key:
            import os
            # Heuristic: if key starts with sk-, it's likely OpenAI
            # But users might pass Groq keys too. 
            # ideally the user sets env vars, but we can store it here if litellm supports explicit passing in all calls
            pass 

    def count_tokens(self, messages: Union[str, List[Dict[str, str]]], model: str) -> int:
        try:
            if isinstance(messages, str):
                return litellm.token_counter(model=model, messages=[{"role": "user", "content": messages}])
            return litellm.token_counter(model=model, messages=messages)
        except Exception as e:
            # Fallback for minimal robustness
            print(f"Token count error: {e}")
            return len(str(messages)) // 4

    def completion(self, messages: List[Dict[str, str]], model: str, response_format: str = None) -> str:
        kwargs = {}
        if response_format == "json_object":
             kwargs["response_format"] = {"type": "json_object"}

        response = litellm.completion(
            model=model,
            messages=messages,
            **kwargs
        )
        return response.choices[0].message.content

    async def acompletion(self, messages: List[Dict[str, str]], model: str, response_format: str = None) -> str:
        kwargs = {}
        if response_format == "json_object":
             kwargs["response_format"] = {"type": "json_object"}

        response = await litellm.acompletion(
            model=model,
            messages=messages,
            **kwargs
        )
        return response.choices[0].message.content
