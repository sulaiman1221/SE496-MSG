from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from msg.domain.assets import Unit
from msg.domain.environment import Environment
from msg.domain.mission import Difficulty, Mission, MissionType

Language = Literal["en", "ar"]
ThreatLevel = Literal["low", "moderate", "high", "critical"]
ObjectivePriority = Literal["primary", "secondary"]


class Objective(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    description: str
    priority: ObjectivePriority


class Phase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    order: int = Field(ge=1)
    name: str
    duration_minutes: int = Field(ge=1)
    description: str
    success_criteria: list[str]


class DecisionPoint(BaseModel):
    model_config = ConfigDict(extra="forbid")

    at_phase: int = Field(ge=1)
    description: str
    options: list[str]


class EvaluationMetric(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    target: str
    weight: float = Field(ge=0.0, le=1.0)


class Variant(BaseModel):
    """LLM-produced content for a single scenario variant."""

    model_config = ConfigDict(extra="forbid")

    variant_index: int = Field(ge=0)
    language: Language
    title: str
    summary: str
    mission_type: MissionType
    difficulty: Difficulty
    threat_level: ThreatLevel
    environment: Environment
    objectives: list[Objective]
    phases: list[Phase]
    rules_of_engagement: list[str]
    decision_points: list[DecisionPoint]
    friendly_forces: list[Unit]
    opposing_forces: list[Unit]
    evaluation_metrics: list[EvaluationMetric]


class ValidationVerdict(BaseModel):
    model_config = ConfigDict(extra="forbid")

    passed: bool
    parity_ok: bool
    doctrine_plausible: bool
    issues: list[str]


class GeneratedVariant(BaseModel):
    model_config = ConfigDict(extra="forbid")

    en: Variant
    ar: Variant
    verdict: ValidationVerdict


class ScenarioVariant(BaseModel):
    id: UUID
    scenario_id: UUID
    language: Language
    variant_index: int
    payload: Variant
    validated: bool


class Scenario(BaseModel):
    id: UUID
    created_at: datetime
    mission: Mission
    status: str
    model: str
    image_url: str | None = None
    tactical_map_url: str | None = None
    variants: list[ScenarioVariant] = Field(default_factory=list)
