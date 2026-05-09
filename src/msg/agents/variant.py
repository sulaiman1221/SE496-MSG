import asyncio
import logging
from typing import TYPE_CHECKING

from openai import AsyncOpenAI

from msg.agents.base import BaseAgent
from msg.agents.types import VariantRequest
from msg.config import Settings
from msg.domain import Variant

if TYPE_CHECKING:
    from msg.rag import DoctrineRAG

_log = logging.getLogger(__name__)


class VariantAgent(BaseAgent[Variant]):
    PROMPT_FILE = "variant.md"
    RESPONSE_MODEL = Variant

    def __init__(
        self,
        client: AsyncOpenAI,
        settings: Settings,
        rag: "DoctrineRAG | None" = None,
    ) -> None:
        super().__init__(client, settings)
        self._rag = rag

    async def _doctrine_context(self, payload: VariantRequest) -> str | None:
        if not self._rag:
            return None
        query = (
            f"{payload.mission.mission_type} {payload.seed.theme} "
            f"{payload.seed.tactical_twist}"
        )
        chunks = await asyncio.to_thread(self._rag.retrieve, query, 3)
        sources = ", ".join(sorted({c["source"] for c in chunks}))
        _log.info(
            "VariantAgent: retrieved %d doctrine chunks from %s",
            len(chunks),
            sources,
        )
        return "\n\n---\n\n".join(c["text"] for c in chunks)
