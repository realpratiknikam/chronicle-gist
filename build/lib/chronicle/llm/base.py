from abc import ABC, abstractmethod
from typing import List, Dict, Any, Union

class LLMProvider(ABC):
    """
    Abstract Base Class for LLM interaction.
    Handles token counting and completion for the compression worker.
    """

    @abstractmethod
    def count_tokens(self, messages: Union[str, List[Dict[str, str]]], model: str) -> int:
        """
        Count tokens for a given message or list of messages.
        """
        pass

    @abstractmethod
    def completion(self, messages: List[Dict[str, str]], model: str, response_format: str = None) -> str:
        """
        Generate a completion from the LLM.
        """
        pass

    @abstractmethod
    async def acompletion(self, messages: List[Dict[str, str]], model: str, response_format: str = None) -> str:
        """
        Async generate a completion from the LLM.
        """
        pass
