import json
import time
import asyncio
from typing import List, Dict, Any, Optional, Union

from .storage.base import Storage
from .storage.memory import InMemoryStorage
from .llm.base import LLMProvider
from .llm.default import LitellmProvider

class Chronicle:
    """
    Chronicle Context Optimization Engine.
    
    Usage:
        query = "Hello world"
        history = [...]
        chronicle = Chronicle(api_key="...")
        optimized_context = chronicle.process(session_id, query, history)
    """

    def __init__(
        self, 
        api_key: Optional[str] = None,
        storage: Optional[Storage] = None,
        llm_provider: Optional[LLMProvider] = None,
        model_name: str = "gpt-3.5-turbo", # Worker model for compression
        token_threshold: int = 1000,
        custom_instructions: Optional[str] = None
    ):
        import os
        # 1. Resolve API Key
        # Order: Param > OPENAI_API_KEY > GROQ_API_KEY > ANTHROPIC_API_KEY
        resolved_key = api_key or os.getenv("OPENAI_API_KEY") or os.getenv("GROQ_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
        
        # 2. Resolve Model
        # Users often set 'LLM_MODEL' or 'MODEL_NAME' in their .env
        self.model_name = os.getenv("LLM_MODEL", model_name)
        
        # 3. Resolve Threshold
        env_threshold = os.getenv("CHRONICLE_THRESHOLD") # Keep namespaced to avoid collision
        self.token_threshold = int(env_threshold) if env_threshold else token_threshold

        self.custom_instructions = custom_instructions
        self.storage = storage or InMemoryStorage()
        self.llm = llm_provider or LitellmProvider(api_key=resolved_key)

    def _estimate_tokens(self, messages: Union[str, List[Dict[str, str]]]) -> int:
        return self.llm.count_tokens(messages, model=self.model_name)

    def _compress_history(self, raw_history: List[Dict], current_summary: str, fact_ledger: Dict) -> Optional[Dict]:
        facts_str = json.dumps(fact_ledger, indent=2)
        history_str = json.dumps(raw_history)
        
        system_prompt = f"""
        You are the "Chronicle" engine. Your job is to compress chat history into a concise summary and a structured Fact Ledger.
        
        Current Summary: {current_summary}
        Current Facts: {facts_str}
        
        New Chat History to Process:
        {history_str}
        
        Output a valid JSON object with two keys:
        1. "summary": Updated narrative summary of the conversation.
        2. "fact_ledger": Updated dictionary of key facts about the user or project.
        
        Do not lose important details. Merge new info with old info.
        """
        
        try:
            content = self.llm.completion(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a precise JSON state manager."},
                    {"role": "user", "content": system_prompt}
                ],
                response_format="json_object"
            )
            return json.loads(content)
        except Exception as e:
            print(f"Chronicle Compression Error: {e}")
            return None

    async def _compress_history_async(self, raw_history: List[Dict], current_summary: str, fact_ledger: Dict) -> Optional[Dict]:
        """
        Async version of history compression.
        """
        facts_str = json.dumps(fact_ledger, indent=2)
        history_str = json.dumps(raw_history)
        
        system_prompt = f"""
        You are the "Chronicle" engine. Your job is to compress chat history into a concise summary and a structured Fact Ledger.
        
        Current Summary: {current_summary}
        Current Facts: {facts_str}
        
        New Chat History to Process:
        {history_str}
        
        Output a valid JSON object with two keys:
        1. "summary": Updated narrative summary of the conversation.
        2. "fact_ledger": Updated dictionary of key facts about the user or project.
        
        Do not lose important details. Merge new info with old info.
        """
        
        try:
            content = await self.llm.acompletion(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a precise JSON state manager."},
                    {"role": "user", "content": system_prompt}
                ],
                response_format="json_object"
            )
            return json.loads(content)
        except Exception as e:
            print(f"Chronicle Async Compression Error: {e}")
            return None

    def process(self, session_id: str, new_message: Dict[str, str], raw_history: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Main entry point. Processes a message and history to return optimized context.
        """
        start_time = time.time()
        
        # 1. Get State
        state = self.storage.get_session(session_id)
        if not state:
            state = {"summary": "", "fact_ledger": {}, "updated_at": time.time()}

        current_summary = state.get("summary", "")
        current_facts = state.get("fact_ledger", {})

        # 2. Check for Bloat
        naive_messages = raw_history + [new_message]
        original_token_count = self._estimate_tokens(naive_messages)
        
        bloat_detected = original_token_count > self.token_threshold
        
        # 3. Process Bloat
        if bloat_detected:
            new_state = self._compress_history(raw_history, current_summary, current_facts)
            if new_state:
                current_summary = new_state.get("summary", current_summary)
                current_facts = new_state.get("fact_ledger", current_facts)
                self.storage.save_session(session_id, current_summary, current_facts)
        
        # 4. Hydrate Prompt
        system_message = f"""
        [MEMORY RECALL]
        Summary: {current_summary}
        
        [FACT LEDGER]
        {json.dumps(current_facts, indent=2)}
        """
        
        hydrated_messages = []
        if bloat_detected:
            # Strict mode: System + New Message
            hydrated_messages = [
                {"role": "system", "content": system_message},
                new_message
            ]
        else:
            # Hybrid mode: System + Sliding Window + New Message
            # Keep last 5 messages for fidelity if under threshold
            recent_messages = raw_history[-5:] if len(raw_history) > 5 else raw_history
            hydrated_messages = [
                {"role": "system", "content": system_message}
            ] + recent_messages + [new_message]

        # 5. Calculate Metrics
        optimized_token_count = self._estimate_tokens(hydrated_messages)
        
        # Best-of-two check
        final_messages = hydrated_messages
        final_token_count = optimized_token_count
        used_strategy = "smart"
        
        if optimized_token_count > original_token_count:
            final_messages = naive_messages
            final_token_count = original_token_count
            used_strategy = "naive"

        return {
            "hydrated_messages": final_messages,
            "meta": {
                "strategy": used_strategy,
                "bloat_detected": bloat_detected,
                "original_tokens": original_token_count,
                "final_tokens": final_token_count,
                "tokens_saved": max(0, original_token_count - final_token_count),
                "latency_ms": round((time.time() - start_time) * 1000, 2),
                "fact_ledger": current_facts
            }
        }

    async def process_async(self, session_id: str, new_message: Dict[str, str], raw_history: List[Dict[str, str]], timeout: int = 10000) -> Dict[str, Any]:
        """
        Async entry point. Processes a message and history to return optimized context without blocking.
        :param timeout: Milliseconds to wait for compression before falling back to previous state. Default: 10000ms (10s).
        """
        start_time = time.time()
        
        # 1. Get State (Async)
        state = await self.storage.aget_session(session_id)
        if not state:
            state = {"summary": "", "fact_ledger": {}, "updated_at": time.time()}

        current_summary = state.get("summary", "")
        current_facts = state.get("fact_ledger", {})

        # 2. Check for Bloat
        naive_messages = raw_history + [new_message]
        original_token_count = self._estimate_tokens(naive_messages)
        
        bloat_detected = original_token_count > self.token_threshold
        timed_out = False
        
        # 3. Process Bloat
        if bloat_detected:
            try:
                # Convert ms to seconds for asyncio
                timeout_seconds = timeout / 1000.0
                new_state = await asyncio.wait_for(
                    self._compress_history_async(raw_history, current_summary, current_facts),
                    timeout=timeout_seconds
                )
                if new_state:
                    current_summary = new_state.get("summary", current_summary)
                    current_facts = new_state.get("fact_ledger", current_facts)
                    await self.storage.asave_session(session_id, current_summary, current_facts)
            except asyncio.TimeoutError:
                print(f"Chronicle Compression Timed Out after {timeout}ms")
                timed_out = True
        
        # 4. Hydrate Prompt
        system_content = f"""
        [MEMORY RECALL]
        Summary: {current_summary}
        
        [FACT LEDGER]
        {json.dumps(current_facts, indent=2)}
        """
        
        if self.custom_instructions:
            system_content = f"{self.custom_instructions}\n\n{system_content}"
        
        hydrated_messages = []
        if bloat_detected:
            # Strict mode: System + New Message
            hydrated_messages = [
                {"role": "system", "content": system_content},
                new_message
            ]
        else:
            # Hybrid mode: System + Sliding Window + New Message
            recent_messages = raw_history[-5:] if len(raw_history) > 5 else raw_history
            hydrated_messages = [
                {"role": "system", "content": system_content}
            ] + recent_messages + [new_message]

        # 5. Calculate Metrics
        optimized_token_count = self._estimate_tokens(hydrated_messages)
        
        # Best-of-two check
        final_messages = hydrated_messages
        final_token_count = optimized_token_count
        used_strategy = "smart"
        
        if optimized_token_count > original_token_count:
            final_messages = naive_messages
            final_token_count = original_token_count
            used_strategy = "naive"

        return {
            "hydrated_messages": final_messages,
            "meta": {
                "strategy": used_strategy,
                "bloat_detected": bloat_detected,
                "timed_out": timed_out,
                "original_tokens": original_token_count,
                "final_tokens": final_token_count,
                "tokens_saved": max(0, original_token_count - final_token_count),
                "latency_ms": round((time.time() - start_time) * 1000, 2),
                "fact_ledger": current_facts
            }
        }
