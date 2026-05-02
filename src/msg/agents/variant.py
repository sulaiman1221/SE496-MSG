from msg.agents.base import BaseAgent
from msg.domain import Variant


class VariantAgent(BaseAgent[Variant]):
    PROMPT_FILE = "variant.md"
    RESPONSE_MODEL = Variant
