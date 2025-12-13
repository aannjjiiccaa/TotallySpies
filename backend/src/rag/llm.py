from abc import ABC, abstractmethod
from functools import lru_cache
from typing import List, Dict

from langchain_groq import ChatGroq

from ..core.config import get_settings


class LLM(ABC):
    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Generate a response from a single prompt"""
        pass

    @abstractmethod
    def chat(self, messages: List[Dict[str, str]]) -> str:
        """Generate a response from chat messages"""
        pass


class GroqLLM(LLM):
    def __init__(self, model: str, temperature: float, api_key: str):
        self._llm = ChatGroq(
            model=model,
            temperature=temperature,
            api_key=api_key
        )

    def generate(self, prompt: str) -> str:
        response = self._llm.invoke(prompt)
        return response.content


    def chat(self, messages: List[Dict[str, str]]) -> str:
        response = self._llm.invoke(messages)
        return response.content



@lru_cache(maxsize=1)
def get_llm() -> LLM:
    settings = get_settings()
    return GroqLLM(
        model=settings.GROQ_MODEL,
        temperature=settings.TEMPERATURE,
        api_key=settings.GROQ_API_KEY
    )
