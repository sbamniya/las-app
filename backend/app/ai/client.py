"""
FuzeBox AEOS — AI Client Abstraction
Supports Anthropic Claude and OpenAI.
"""
import json
from typing import Optional
from app.core.config import settings


class AIClient:
    """Unified AI client supporting Claude and OpenAI."""

    def __init__(self):
        self.provider = settings.AI_PROVIDER
        self.model = settings.AI_MODEL
        self._anthropic = None
        self._openai = None

    async def _get_anthropic(self):
        if not self._anthropic:
            import anthropic
            self._anthropic = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        return self._anthropic

    async def _get_openai(self):
        if not self._openai:
            import openai
            self._openai = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        return self._openai

    async def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ) -> str:
        if self.provider == "anthropic":
            return await self._generate_anthropic(prompt, system, temperature, max_tokens)
        return await self._generate_openai(prompt, system, temperature, max_tokens)

    async def _generate_anthropic(self, prompt: str, system: Optional[str], temperature: float, max_tokens: int) -> str:
        client = await self._get_anthropic()
        kwargs = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system:
            kwargs["system"] = system
        response = await client.messages.create(**kwargs)
        return response.content[0].text

    async def _generate_openai(self, prompt: str, system: Optional[str], temperature: float, max_tokens: int) -> str:
        client = await self._get_openai()
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        response = await client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content

    async def generate_json(self, prompt: str, system: Optional[str] = None) -> dict:
        raw = await self.generate(prompt, system, temperature=0.1)
        # Extract JSON from response
        try:
            start = raw.index("{")
            end = raw.rindex("}") + 1
            return json.loads(raw[start:end])
        except (ValueError, json.JSONDecodeError):
            try:
                start = raw.index("[")
                end = raw.rindex("]") + 1
                return json.loads(raw[start:end])
            except (ValueError, json.JSONDecodeError):
                return {"raw": raw, "error": "Could not parse JSON"}
