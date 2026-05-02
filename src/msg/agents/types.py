from pydantic import BaseModel, ConfigDict, Field

from msg.domain import Mission, Variant


class VariantSeed(BaseModel):
    model_config = ConfigDict(extra="forbid")

    variant_index: int = Field(ge=0)
    theme: str
    threat_emphasis: str
    tactical_twist: str
    brief_synopsis: str


class PlannerOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    seeds: list[VariantSeed] = Field(min_length=1, max_length=10)


class VariantRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    mission: Mission
    seed: VariantSeed


class ValidatorRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    en: Variant
    ar: Variant
