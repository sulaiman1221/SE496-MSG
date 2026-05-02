from msg.agents.base import BaseAgent
from msg.agents.types import PlannerOutput


class PlannerAgent(BaseAgent[PlannerOutput]):
    PROMPT_FILE = "planner.md"
    RESPONSE_MODEL = PlannerOutput
