import logging
from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, ValidationError
from supabase import AsyncClient

from msg.domain import (
    Difficulty,
    GeneratedVariant,
    Mission,
    MissionType,
    Scenario,
    ScenarioVariant,
    Variant,
)

_log = logging.getLogger(__name__)


class ScenarioFilters(BaseModel):
    model_config = ConfigDict(extra="forbid")

    mission_type: MissionType | None = None
    difficulty: Difficulty | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None
    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)


class ScenarioSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    created_at: datetime
    mission_type: str
    difficulty: str
    status: str


class Repository:
    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def save_scenario(self, mission: Mission, model: str) -> UUID:
        response = (
            await self._client.table("scenarios")
            .insert(
                {
                    "mission": mission.model_dump(mode="json"),
                    "model": model,
                }
            )
            .execute()
        )
        return UUID(response.data[0]["id"])

    async def save_variants(
        self, scenario_id: UUID, generated: list[GeneratedVariant]
    ) -> None:
        rows: list[dict[str, Any]] = []
        for g in generated:
            rows.append(
                {
                    "scenario_id": str(scenario_id),
                    "language": "en",
                    "variant_index": g.en.variant_index,
                    "payload": g.en.model_dump(mode="json"),
                    "validated": g.verdict.passed,
                }
            )
            rows.append(
                {
                    "scenario_id": str(scenario_id),
                    "language": "ar",
                    "variant_index": g.ar.variant_index,
                    "payload": g.ar.model_dump(mode="json"),
                    "validated": g.verdict.passed,
                }
            )
        await self._client.table("scenario_variants").insert(rows).execute()

    async def log_event(
        self,
        scenario_id: UUID | None,
        event_type: str,
        detail: dict[str, Any],
    ) -> None:
        await self._client.table("audit_log").insert(
            {
                "scenario_id": str(scenario_id) if scenario_id else None,
                "event_type": event_type,
                "detail": detail,
            }
        ).execute()

    async def get_scenario(self, scenario_id: UUID) -> Scenario | None:
        scenario_resp = (
            await self._client.table("scenarios")
            .select("*")
            .eq("id", str(scenario_id))
            .maybe_single()
            .execute()
        )
        if not scenario_resp or not scenario_resp.data:
            return None

        variants_resp = (
            await self._client.table("scenario_variants")
            .select("*")
            .eq("scenario_id", str(scenario_id))
            .order("variant_index")
            .order("language")
            .execute()
        )

        row = scenario_resp.data
        return Scenario(
            id=row["id"],
            created_at=row["created_at"],
            mission=Mission(**row["mission"]),
            status=row["status"],
            model=row["model"],
            variants=[
                ScenarioVariant(
                    id=v["id"],
                    scenario_id=v["scenario_id"],
                    language=v["language"],
                    variant_index=v["variant_index"],
                    payload=Variant(**v["payload"]),
                    validated=v["validated"],
                )
                for v in (variants_resp.data or [])
            ],
        )

    async def list_scenarios(
        self, filters: ScenarioFilters
    ) -> list[ScenarioSummary]:
        query = self._client.table("scenarios").select(
            "id, created_at, mission, status"
        )
        if filters.mission_type:
            query = query.eq("mission->>mission_type", filters.mission_type)
        if filters.difficulty:
            query = query.eq("mission->>difficulty", filters.difficulty)
        if filters.date_from:
            query = query.gte("created_at", filters.date_from.isoformat())
        if filters.date_to:
            query = query.lte("created_at", filters.date_to.isoformat())
        response = (
            await query.order("created_at", desc=True)
            .range(filters.offset, filters.offset + filters.limit - 1)
            .execute()
        )
        summaries: list[ScenarioSummary] = []
        for row in response.data or []:
            try:
                summaries.append(
                    ScenarioSummary(
                        id=row["id"],
                        created_at=row["created_at"],
                        mission_type=row["mission"]["mission_type"],
                        difficulty=row["mission"]["difficulty"],
                        status=row["status"],
                    )
                )
            except (KeyError, TypeError, ValidationError) as exc:
                _log.warning(
                    "skipping malformed scenarios row id=%s: %s",
                    row.get("id"),
                    exc,
                )
        return summaries
