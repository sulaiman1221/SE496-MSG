from functools import cache
from importlib.resources import files
from typing import ClassVar

from openai import AsyncOpenAI
from pydantic import BaseModel

from msg.config import Settings


@cache
def _load_prompt(filename: str) -> str:
    return files("msg").joinpath("prompts", filename).read_text(encoding="utf-8")


class BaseAgent[TResponse: BaseModel]:
    PROMPT_FILE: ClassVar[str] = ""
    RESPONSE_MODEL: ClassVar[type[BaseModel]]

    def __init__(self, client: AsyncOpenAI, settings: Settings) -> None:
        if not self.PROMPT_FILE or not getattr(self, "RESPONSE_MODEL", None):
            raise TypeError(
                f"{type(self).__name__} must set PROMPT_FILE and RESPONSE_MODEL"
            )
        self._client = client
        self._settings = settings
        self._system_prompt = _load_prompt(self.PROMPT_FILE)

    async def _doctrine_context(self, payload: BaseModel) -> str | None:
        """Override to inject retrieved doctrine into the system prompt."""
        return None

    async def run(self, payload: BaseModel) -> TResponse:
        system_prompt = self._system_prompt
        context = await self._doctrine_context(payload)
        if context:
            system_prompt = f"{system_prompt}\n\nDOCTRINE CONTEXT:\n{context}"

        response = await self._client.chat.completions.parse(
            model=self._settings.openai_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": payload.model_dump_json()},
            ],
            response_format=self.RESPONSE_MODEL,
        )
        message = response.choices[0].message
        if message.refusal:
            raise RuntimeError(f"{type(self).__name__} refused: {message.refusal}")
        if message.parsed is None:
            raise RuntimeError(f"{type(self).__name__} returned no parsed content")
        return message.parsed
