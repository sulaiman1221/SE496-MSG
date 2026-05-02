from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

import pytest

from msg.domain import GeneratedVariant, ValidationVerdict
from msg.storage import Repository, ScenarioFilters
from tests.conftest import _make_variant


def _build_fake_supabase_client() -> tuple[MagicMock, MagicMock]:
    client = MagicMock()
    builder = MagicMock()
    for method in (
        "select",
        "insert",
        "eq",
        "gte",
        "lte",
        "order",
        "range",
        "maybe_single",
    ):
        getattr(builder, method).return_value = builder
    builder.execute = AsyncMock()
    client.table.return_value = builder
    return client, builder


@pytest.fixture
def supabase_pair():
    return _build_fake_supabase_client()


def _verdict(passed: bool = True) -> ValidationVerdict:
    return ValidationVerdict(
        passed=passed,
        parity_ok=passed,
        doctrine_plausible=passed,
        issues=[] if passed else ["mismatch"],
    )


@pytest.mark.asyncio
async def test_save_scenario_returns_inserted_uuid(supabase_pair, sample_mission):
    client, builder = supabase_pair
    new_id = uuid4()
    builder.execute.return_value = SimpleNamespace(data=[{"id": str(new_id)}])
    repo = Repository(client=client)

    result = await repo.save_scenario(sample_mission, model="gpt-test")

    client.table.assert_called_with("scenarios")
    payload = builder.insert.call_args.args[0]
    assert payload["model"] == "gpt-test"
    assert payload["mission"]["mission_type"] == sample_mission.mission_type
    assert result == new_id


@pytest.mark.asyncio
async def test_save_variants_writes_2n_rows(supabase_pair):
    client, builder = supabase_pair
    builder.execute.return_value = SimpleNamespace(data=[])
    repo = Repository(client=client)

    generated = [
        GeneratedVariant(
            en=_make_variant(variant_index=i, language="en"),
            ar=_make_variant(variant_index=i, language="ar"),
            verdict=_verdict(passed=(i != 1)),
        )
        for i in range(3)
    ]
    scenario_id = uuid4()

    await repo.save_variants(scenario_id=scenario_id, generated=generated)

    client.table.assert_called_with("scenario_variants")
    rows = builder.insert.call_args.args[0]
    assert len(rows) == 6
    en_rows = [r for r in rows if r["language"] == "en"]
    ar_rows = [r for r in rows if r["language"] == "ar"]
    assert len(en_rows) == 3 and len(ar_rows) == 3
    assert {r["variant_index"] for r in rows} == {0, 1, 2}
    failed_row = next(r for r in rows if r["variant_index"] == 1)
    assert failed_row["validated"] is False
    passed_row = next(r for r in rows if r["variant_index"] == 0)
    assert passed_row["validated"] is True


@pytest.mark.asyncio
async def test_log_event_writes_audit_row(supabase_pair):
    client, builder = supabase_pair
    builder.execute.return_value = SimpleNamespace(data=[])
    repo = Repository(client=client)
    scenario_id = uuid4()

    await repo.log_event(
        scenario_id=scenario_id,
        event_type="generated",
        detail={"n_variants": 5, "n_failed": 0},
    )

    client.table.assert_called_with("audit_log")
    row = builder.insert.call_args.args[0]
    assert row["event_type"] == "generated"
    assert row["detail"] == {"n_variants": 5, "n_failed": 0}
    assert row["scenario_id"] == str(scenario_id)


@pytest.mark.asyncio
async def test_log_event_allows_null_scenario_id(supabase_pair):
    client, builder = supabase_pair
    builder.execute.return_value = SimpleNamespace(data=[])
    repo = Repository(client=client)

    await repo.log_event(scenario_id=None, event_type="error", detail={})

    row = builder.insert.call_args.args[0]
    assert row["scenario_id"] is None


@pytest.mark.asyncio
async def test_get_scenario_returns_none_when_missing(supabase_pair):
    client, builder = supabase_pair
    builder.execute.return_value = SimpleNamespace(data=None)
    repo = Repository(client=client)

    result = await repo.get_scenario(uuid4())

    assert result is None


@pytest.mark.asyncio
async def test_get_scenario_hydrates_parent_and_variants(
    supabase_pair, sample_mission
):
    client, builder = supabase_pair
    scenario_id = uuid4()
    en_variant = _make_variant(variant_index=0, language="en")
    ar_variant = _make_variant(variant_index=0, language="ar")

    builder.execute.side_effect = [
        SimpleNamespace(
            data={
                "id": str(scenario_id),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "mission": sample_mission.model_dump(mode="json"),
                "status": "generated",
                "model": "gpt-test",
            }
        ),
        SimpleNamespace(
            data=[
                {
                    "id": str(uuid4()),
                    "scenario_id": str(scenario_id),
                    "language": "en",
                    "variant_index": 0,
                    "payload": en_variant.model_dump(mode="json"),
                    "validated": True,
                },
                {
                    "id": str(uuid4()),
                    "scenario_id": str(scenario_id),
                    "language": "ar",
                    "variant_index": 0,
                    "payload": ar_variant.model_dump(mode="json"),
                    "validated": True,
                },
            ]
        ),
    ]
    repo = Repository(client=client)

    result = await repo.get_scenario(scenario_id)

    assert result is not None
    assert result.id == scenario_id
    assert len(result.variants) == 2
    languages = {v.language for v in result.variants}
    assert languages == {"en", "ar"}


@pytest.mark.asyncio
async def test_list_scenarios_applies_filters(supabase_pair, sample_mission):
    client, builder = supabase_pair
    builder.execute.return_value = SimpleNamespace(
        data=[
            {
                "id": str(uuid4()),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "mission": sample_mission.model_dump(mode="json"),
                "status": "generated",
            }
        ]
    )
    repo = Repository(client=client)
    filters = ScenarioFilters(
        mission_type="assault",
        difficulty="medium",
        date_from=datetime(2026, 1, 1, tzinfo=timezone.utc),
        limit=10,
        offset=5,
    )

    results = await repo.list_scenarios(filters)

    assert len(results) == 1
    assert results[0].mission_type == sample_mission.mission_type
    eq_calls = [c.args for c in builder.eq.call_args_list]
    assert ("mission->>mission_type", "assault") in eq_calls
    assert ("mission->>difficulty", "medium") in eq_calls
    range_call = builder.range.call_args.args
    assert range_call == (5, 14)
