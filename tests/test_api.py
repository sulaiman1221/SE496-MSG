from datetime import datetime, timezone
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from msg.api import create_app, get_orchestrator, get_repository
from msg.domain import Scenario, ScenarioVariant
from msg.orchestrator import Orchestrator
from msg.storage import Repository, ScenarioSummary
from tests.conftest import _make_variant


def _make_scenario(scenario_id=None, sample_mission=None) -> Scenario:
    sid = scenario_id or uuid4()
    return Scenario(
        id=sid,
        created_at=datetime.now(timezone.utc),
        mission=sample_mission,
        status="generated",
        model="gpt-test",
        variants=[
            ScenarioVariant(
                id=uuid4(),
                scenario_id=sid,
                language="en",
                variant_index=0,
                payload=_make_variant(variant_index=0, language="en"),
                validated=True,
            ),
            ScenarioVariant(
                id=uuid4(),
                scenario_id=sid,
                language="ar",
                variant_index=0,
                payload=_make_variant(variant_index=0, language="ar"),
                validated=True,
            ),
        ],
    )


@pytest.fixture
def fake_orchestrator():
    return AsyncMock(spec=Orchestrator)


@pytest.fixture
def fake_repository():
    return AsyncMock(spec=Repository)


@pytest.fixture
def client(fake_orchestrator, fake_repository):
    app = create_app()
    app.dependency_overrides[get_orchestrator] = lambda: fake_orchestrator
    app.dependency_overrides[get_repository] = lambda: fake_repository
    return TestClient(app)


def test_post_scenarios_runs_orchestrator_and_returns_scenario(
    client, fake_orchestrator, fake_repository, sample_mission
):
    scenario_id = uuid4()
    fake_orchestrator.generate_and_persist.return_value = scenario_id
    fake_repository.get_scenario.return_value = _make_scenario(
        scenario_id, sample_mission
    )

    response = client.post(
        "/api/scenarios", json=sample_mission.model_dump(mode="json")
    )

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == str(scenario_id)
    assert len(body["variants"]) == 2
    fake_orchestrator.generate_and_persist.assert_awaited_once()
    called_mission = fake_orchestrator.generate_and_persist.await_args.args[0]
    assert called_mission.mission_type == sample_mission.mission_type


def test_post_scenarios_500_when_persist_returns_missing(
    client, fake_orchestrator, fake_repository, sample_mission
):
    fake_orchestrator.generate_and_persist.return_value = uuid4()
    fake_repository.get_scenario.return_value = None

    response = client.post(
        "/api/scenarios", json=sample_mission.model_dump(mode="json")
    )

    assert response.status_code == 500


def test_get_scenario_returns_404_when_unknown(client, fake_repository):
    fake_repository.get_scenario.return_value = None

    response = client.get(f"/api/scenarios/{uuid4()}")

    assert response.status_code == 404


def test_get_scenario_returns_body(client, fake_repository, sample_mission):
    scenario_id = uuid4()
    fake_repository.get_scenario.return_value = _make_scenario(
        scenario_id, sample_mission
    )

    response = client.get(f"/api/scenarios/{scenario_id}")

    assert response.status_code == 200
    assert response.json()["id"] == str(scenario_id)


def test_list_scenarios_passes_filters_to_repository(
    client, fake_repository, sample_mission
):
    fake_repository.list_scenarios.return_value = [
        ScenarioSummary(
            id=uuid4(),
            created_at=datetime.now(timezone.utc),
            mission_type=sample_mission.mission_type,
            difficulty=sample_mission.difficulty,
            status="generated",
        )
    ]

    response = client.get(
        "/api/scenarios",
        params={
            "mission_type": sample_mission.mission_type,
            "difficulty": sample_mission.difficulty,
            "limit": 25,
            "offset": 0,
        },
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    filters = fake_repository.list_scenarios.await_args.args[0]
    assert filters.mission_type == sample_mission.mission_type
    assert filters.difficulty == sample_mission.difficulty
    assert filters.limit == 25


def test_list_scenarios_rejects_invalid_mission_type(client):
    response = client.get("/api/scenarios", params={"mission_type": "not-a-type"})
    assert response.status_code == 422


def test_cors_allows_vite_dev_origin(client):
    response = client.options(
        "/api/scenarios",
        headers={
            "origin": "http://localhost:5173",
            "access-control-request-method": "POST",
            "access-control-request-headers": "content-type",
        },
    )
    assert response.status_code == 200
    assert (
        response.headers["access-control-allow-origin"] == "http://localhost:5173"
    )
