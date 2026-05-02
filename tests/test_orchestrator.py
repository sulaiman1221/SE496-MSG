from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from msg.agents import (
    PlannerAgent,
    PlannerOutput,
    TranslatorAgent,
    ValidationVerdict,
    ValidatorAgent,
    ValidatorRequest,
    VariantAgent,
    VariantRequest,
    VariantSeed,
)
from msg.domain import Mission, Variant
from msg.orchestrator import GeneratedVariant, Orchestrator
from msg.storage.repository import Repository
from tests.conftest import _make_variant


def _seed(i: int) -> VariantSeed:
    return VariantSeed(
        variant_index=i,
        theme=f"theme {i}",
        threat_emphasis="emphasis",
        tactical_twist="twist",
        brief_synopsis="synopsis",
    )


def _verdict(*, passed: bool) -> ValidationVerdict:
    return ValidationVerdict(
        passed=passed,
        parity_ok=passed,
        doctrine_plausible=passed,
        issues=[] if passed else ["mismatch"],
    )


@pytest.fixture
def fake_agents():
    return {
        "planner": AsyncMock(spec=PlannerAgent),
        "variant": AsyncMock(spec=VariantAgent),
        "translator": AsyncMock(spec=TranslatorAgent),
        "validator": AsyncMock(spec=ValidatorAgent),
    }


@pytest.fixture
def fake_repository():
    repo = AsyncMock(spec=Repository)
    repo.save_scenario.return_value = uuid4()
    return repo


@pytest.fixture
def orchestrator(fake_agents, fake_repository, settings):
    return Orchestrator(
        planner=fake_agents["planner"],
        variant_agent=fake_agents["variant"],
        translator=fake_agents["translator"],
        validator=fake_agents["validator"],
        repository=fake_repository,
        settings=settings,
    )


def _wire_plan(fake_agents, n: int) -> list[VariantSeed]:
    seeds = [_seed(i) for i in range(n)]
    fake_agents["planner"].run.return_value = PlannerOutput(seeds=seeds)
    return seeds


def _wire_variants(count: int, language: str, start_index: int = 0):
    return [
        _make_variant(variant_index=start_index + i, language=language)
        for i in range(count)
    ]


@pytest.mark.asyncio
async def test_generate_happy_path_no_retries(
    orchestrator, fake_agents, sample_mission
):
    seeds = _wire_plan(fake_agents, sample_mission.n_variants)
    ens = _wire_variants(len(seeds), "en")
    ars = _wire_variants(len(seeds), "ar")
    fake_agents["variant"].run.side_effect = ens
    fake_agents["translator"].run.side_effect = ars
    fake_agents["validator"].run.side_effect = [_verdict(passed=True) for _ in seeds]

    result = await orchestrator.generate(sample_mission)

    assert len(result) == sample_mission.n_variants
    assert all(isinstance(g, GeneratedVariant) for g in result)
    assert all(g.verdict.passed for g in result)
    assert fake_agents["planner"].run.await_count == 1
    assert fake_agents["variant"].run.await_count == sample_mission.n_variants
    assert fake_agents["translator"].run.await_count == sample_mission.n_variants
    assert fake_agents["validator"].run.await_count == sample_mission.n_variants


@pytest.mark.asyncio
async def test_generate_retries_only_failed_indices(
    orchestrator, fake_agents, sample_mission
):
    seeds = _wire_plan(fake_agents, sample_mission.n_variants)
    first_ens = _wire_variants(len(seeds), "en")
    first_ars = _wire_variants(len(seeds), "ar")
    retry_en = _make_variant(variant_index=2, language="en")
    retry_ar = _make_variant(variant_index=2, language="ar")

    fake_agents["variant"].run.side_effect = [*first_ens, retry_en]
    fake_agents["translator"].run.side_effect = [*first_ars, retry_ar]
    fake_agents["validator"].run.side_effect = [
        _verdict(passed=True),
        _verdict(passed=True),
        _verdict(passed=False),
        _verdict(passed=True),
        _verdict(passed=True),
        _verdict(passed=True),
    ]

    result = await orchestrator.generate(sample_mission)

    assert len(result) == sample_mission.n_variants
    assert all(g.verdict.passed for g in result)
    assert fake_agents["variant"].run.await_count == sample_mission.n_variants + 1
    assert fake_agents["translator"].run.await_count == sample_mission.n_variants + 1
    assert fake_agents["validator"].run.await_count == sample_mission.n_variants + 1


@pytest.mark.asyncio
async def test_stubborn_failure_kept_after_retry(
    orchestrator, fake_agents, sample_mission
):
    seeds = _wire_plan(fake_agents, sample_mission.n_variants)
    first_ens = _wire_variants(len(seeds), "en")
    first_ars = _wire_variants(len(seeds), "ar")
    retry_en = _make_variant(variant_index=0, language="en")
    retry_ar = _make_variant(variant_index=0, language="ar")

    fake_agents["variant"].run.side_effect = [*first_ens, retry_en]
    fake_agents["translator"].run.side_effect = [*first_ars, retry_ar]
    fake_agents["validator"].run.side_effect = [
        _verdict(passed=False),  # index 0 first attempt
        _verdict(passed=True),
        _verdict(passed=True),
        _verdict(passed=True),
        _verdict(passed=True),
        _verdict(passed=False),  # index 0 retry still fails
    ]

    result = await orchestrator.generate(sample_mission)

    assert len(result) == sample_mission.n_variants
    assert result[0].verdict.passed is False
    assert all(g.verdict.passed for g in result[1:])
    assert fake_agents["variant"].run.await_count == sample_mission.n_variants + 1


@pytest.mark.asyncio
async def test_seed_count_drift_raises(orchestrator, fake_agents, sample_mission):
    _wire_plan(fake_agents, sample_mission.n_variants - 1)

    with pytest.raises(ValueError, match="seed"):
        await orchestrator.generate(sample_mission)


@pytest.mark.asyncio
async def test_agent_exception_propagates(orchestrator, fake_agents, sample_mission):
    _wire_plan(fake_agents, sample_mission.n_variants)
    fake_agents["variant"].run.side_effect = RuntimeError("upstream failure")

    with pytest.raises(RuntimeError, match="upstream failure"):
        await orchestrator.generate(sample_mission)


@pytest.mark.asyncio
async def test_generate_and_persist_writes_scenario_variants_and_audit(
    orchestrator, fake_agents, fake_repository, sample_mission, settings
):
    seeds = _wire_plan(fake_agents, sample_mission.n_variants)
    ens = _wire_variants(len(seeds), "en")
    ars = _wire_variants(len(seeds), "ar")
    fake_agents["variant"].run.side_effect = ens
    fake_agents["translator"].run.side_effect = ars
    fake_agents["validator"].run.side_effect = [_verdict(passed=True) for _ in seeds]

    scenario_id = await orchestrator.generate_and_persist(sample_mission)

    fake_repository.save_scenario.assert_awaited_once_with(
        mission=sample_mission, model=settings.openai_model
    )
    fake_repository.save_variants.assert_awaited_once()
    saved_variants = fake_repository.save_variants.await_args.kwargs["generated"]
    assert len(saved_variants) == sample_mission.n_variants
    fake_repository.log_event.assert_awaited_once()
    assert fake_repository.log_event.await_args.kwargs["event_type"] == "generated"
    assert scenario_id == fake_repository.save_scenario.return_value


@pytest.mark.asyncio
async def test_generate_and_persist_logs_failure_counts(
    orchestrator, fake_agents, fake_repository, sample_mission
):
    seeds = _wire_plan(fake_agents, sample_mission.n_variants)
    ens = _wire_variants(len(seeds), "en")
    ars = _wire_variants(len(seeds), "ar")
    retry_en = _make_variant(variant_index=1, language="en")
    retry_ar = _make_variant(variant_index=1, language="ar")

    fake_agents["variant"].run.side_effect = [*ens, retry_en]
    fake_agents["translator"].run.side_effect = [*ars, retry_ar]
    fake_agents["validator"].run.side_effect = [
        _verdict(passed=True),
        _verdict(passed=False),
        _verdict(passed=True),
        _verdict(passed=True),
        _verdict(passed=True),
        _verdict(passed=False),
    ]

    await orchestrator.generate_and_persist(sample_mission)

    detail = fake_repository.log_event.await_args.kwargs["detail"]
    assert detail["n_variants"] == sample_mission.n_variants
    assert detail["n_failed"] == 1
