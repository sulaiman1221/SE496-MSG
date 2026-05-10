from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Difficulty = Literal["easy", "medium", "hard", "expert"]

MissionType = Literal["assault", "defense", "ambush"]

UnitType = Literal[
    "land_forces",
    "air_force",
    "naval_forces",
    "air_defense_forces",
    "strategic_missile_force",
    "medical_support",
]

EnemyThreatLevel = Literal["low", "moderate", "high", "critical"]


class MissionEnvironmentHints(BaseModel):
    model_config = ConfigDict(extra="forbid")

    terrain: str | None = None
    weather: str | None = None
    time_of_day: str | None = None
    region: str | None = None
    visibility_pct: int | None = Field(default=None, ge=0, le=100)


class Mission(BaseModel):
    model_config = ConfigDict(extra="forbid")

    mission_type: MissionType
    difficulty: Difficulty = "medium"
    title: str | None = None
    environment: MissionEnvironmentHints = Field(default_factory=MissionEnvironmentHints)
    aircraft: list[str] = Field(default_factory=list)
    friendly_unit_types: list[UnitType] = Field(default_factory=list)
    enemy_threat_level: EnemyThreatLevel | None = None
    resources: list[str] = Field(default_factory=list)
    training_goals: list[str] = Field(default_factory=list)
    additional_context: str | None = None
    n_variants: int = Field(default=5, ge=1, le=10)
