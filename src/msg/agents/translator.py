from msg.agents.base import BaseAgent
from msg.domain import Variant


class TranslatorAgent(BaseAgent[Variant]):
    PROMPT_FILE = "translator.md"
    RESPONSE_MODEL = Variant
