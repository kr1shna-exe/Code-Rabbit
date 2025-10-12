import asyncio
from typing import Optional

import google.generativeai as genai
from groq import Groq
from zai import ZaiClient

from utils.config import settings


class AIClient:
    def __init__(self, provider: Optional[str] = None):
        self.provider = provider or settings.ai_provider
        self._initialize_client()

    def _initialize_client(self):
        """Initialize the appropriate AI client based on provider"""
        if self.provider == "gemini":
            genai.configure(api_key=settings.gemini_api_key)
            self.model_name = "gemini-2.0-flash-exp"
        elif self.provider == "zai":
            self.client = ZaiClient(api_key=settings.zai_api_key)
            self.model_name = "glm-4.6"  # GLM-4.6 model for code review
        elif self.provider == "groq":
            self.client = Groq(api_key=settings.groq_api_key)
            self.model_name = "llama-3.3-70b-versatile"  # Fast and capable
        else:
            raise ValueError(f"Unsupported AI provider: {self.provider}")

    async def generate_content(self, prompt: str) -> str:
        if self.provider == "gemini":
            return await self._generate_gemini(prompt)
        elif self.provider == "zai":
            return await self._generate_zai(prompt)
        elif self.provider == "groq":
            return await self._generate_groq(prompt)

    async def _generate_gemini(self, prompt: str) -> str:
        model = genai.GenerativeModel(self.model_name)
        response = await asyncio.to_thread(model.generate_content, prompt)
        return response.text

    async def _generate_zai(self, prompt: str) -> str:
        response = await asyncio.to_thread(
            self.client.chat.completions.create,
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content

    async def _generate_groq(self, prompt: str) -> str:
        response = await asyncio.to_thread(
            self.client.chat.completions.create,
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content

    def get_provider_info(self) -> dict:
        return {"provider": self.provider, "model": self.model_name}


# Create a singleton instance
ai_client = AIClient()
