from msg.agents.base import BaseAgent
from msg.domain import ValidationVerdict


class ValidatorAgent(BaseAgent[ValidationVerdict]):
    PROMPT_FILE = "validator.md"
    RESPONSE_MODEL = ValidationVerdict
