import asyncio
from uuid import UUID

from msg.agents import (
    PlannerAgent,
    TranslatorAgent,
    ValidatorAgent,
    ValidatorRequest,
    VariantAgent,
    VariantRequest,
    VariantSeed,
)
from msg.config import Settings
from msg.domain import GeneratedVariant, Mission
from msg.storage.repository import Repository


class Orchestrator:
    def __init__(
        self,
        *,
        planner: PlannerAgent,
        variant_agent: VariantAgent,
        translator: TranslatorAgent,
        validator: ValidatorAgent,
        repository: Repository,
        settings: Settings,
    ) -> None:
        self._planner = planner
        self._variant = variant_agent
        self._translator = translator
        self._validator = validator
        self._repository = repository
        self._settings = settings

    async def generate(self, mission: Mission) -> list[GeneratedVariant]:
        plan = await self._planner.run(mission)
        if len(plan.seeds) != mission.n_variants:
            raise ValueError(
                f"planner returned {len(plan.seeds)} seeds, expected {mission.n_variants}"
            )

        first = await asyncio.gather(
            *(self._produce(mission, seed) for seed in plan.seeds)
        )

        retry_indices = [i for i, g in enumerate(first) if not g.verdict.passed]
        if not retry_indices:
            return list(first)

        retries = await asyncio.gather(
            *(self._produce(mission, plan.seeds[i]) for i in retry_indices)
        )

        merged = list(first)
        for index, retried in zip(retry_indices, retries, strict=True):
            merged[index] = retried
        return merged

    async def _produce(
        self, mission: Mission, seed: VariantSeed
    ) -> GeneratedVariant:
        en = await self._variant.run(VariantRequest(mission=mission, seed=seed))
        ar = await self._translator.run(en)
        verdict = await self._validator.run(ValidatorRequest(en=en, ar=ar))
        return GeneratedVariant(en=en, ar=ar, verdict=verdict)

    async def generate_and_persist(self, mission: Mission) -> UUID:
        generated = await self.generate(mission)
        scenario_id = await self._repository.save_scenario(
            mission=mission, model=self._settings.openai_model
        )
        await self._repository.save_variants(
            scenario_id=scenario_id, generated=generated
        )
        await self._repository.log_event(
            scenario_id=scenario_id,
            event_type="generated",
            detail={
                "n_variants": len(generated),
                "n_failed": sum(1 for g in generated if not g.verdict.passed),
            },
        )
        return scenario_id
