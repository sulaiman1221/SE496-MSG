from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from msg.agents.types import PlannerOutput, VariantSeed
from msg.config import Settings
from msg.domain import (
    DecisionPoint,
    Environment,
    EvaluationMetric,
    Mission,
    Objective,
    Phase,
    Unit,
    ValidationVerdict,
    Variant,
    Weapon,
)
from msg.rag import DoctrineRAG


@pytest.fixture
def settings() -> Settings:
    return Settings(
        OPENAI_API_KEY="sk-test-1234567890",
        OPENAI_MODEL="test-model",
        SUPABASE_URL="http://test.local",
        SUPABASE_ANON_KEY="anon-test-1234567890",
        SUPABASE_SERVICE_KEY="service-test-1234567890",
    )


def make_parsed_response(parsed_instance, *, refusal: str | None = None):
    message = SimpleNamespace(parsed=parsed_instance, refusal=refusal)
    return SimpleNamespace(choices=[SimpleNamespace(message=message)])


@pytest.fixture
def fake_openai_client():
    client = MagicMock()
    client.chat.completions.parse = AsyncMock()
    return client


@pytest.fixture
def sample_mission() -> Mission:
    return Mission(
        mission_type="assault",
        difficulty="medium",
        resources=["2 squads"],
        training_goals=["improve concealment", "radio discipline"],
        n_variants=5,
    )


@pytest.fixture
def sample_seed() -> VariantSeed:
    return VariantSeed(
        variant_index=3,
        theme="urban night infiltration",
        threat_emphasis="enemy patrols and surveillance",
        tactical_twist="no-fire rules of engagement",
        brief_synopsis=(
            "A four-person recon element infiltrates a contested urban sector "
            "at night to map enemy patrol patterns without being detected."
        ),
    )


def _make_variant(*, variant_index: int = 0, language: str = "en") -> Variant:
    return Variant(
        variant_index=variant_index,
        language=language,
        title="Operation Night Ledger",
        summary="Two squads reconnoiter a contested urban sector.",
        mission_type="assault",
        difficulty="medium",
        threat_level="moderate",
        environment=Environment(
            terrain="desert",
            weather="clear",
            time_of_day="night",
            region="Sector 7",
            visibility="poor",
            hazards=["broken glass", "loose debris"],
        ),
        objectives=[
            Objective(id="obj-1", description="Map patrol timings", priority="primary"),
            Objective(id="obj-2", description="Avoid contact", priority="secondary"),
        ],
        phases=[
            Phase(
                order=1,
                name="Infiltration",
                duration_minutes=45,
                description="Move to observation post",
                success_criteria=["reach OP undetected"],
            ),
            Phase(
                order=2,
                name="Observation",
                duration_minutes=120,
                description="Log patrol patterns",
                success_criteria=["record 3+ patrol cycles"],
            ),
            Phase(
                order=3,
                name="Exfiltration",
                duration_minutes=45,
                description="Return to friendly lines",
                success_criteria=["return without contact"],
            ),
        ],
        rules_of_engagement=[
            "no engagement unless compromised",
            "positive identification required",
        ],
        decision_points=[
            DecisionPoint(
                at_phase=1,
                description="Unexpected patrol at route",
                options=["reroute", "hide", "abort"],
            ),
            DecisionPoint(
                at_phase=3,
                description="Exfil route blocked",
                options=["alternate route", "hold position"],
            ),
        ],
        friendly_forces=[
            Unit(
                designation="1st Squad, A Company",
                size=9,
                role="recon",
                weapons=[Weapon(name="M4A1", category="rifle", quantity=9)],
                vehicles=[],
            ),
        ],
        opposing_forces=[
            Unit(
                designation="Opposing Patrol Element",
                size=6,
                role="security",
                weapons=[Weapon(name="AK-74", category="rifle", quantity=6)],
                vehicles=[],
            ),
        ],
        evaluation_metrics=[
            EvaluationMetric(name="Stealth", target="no detection", weight=0.6),
            EvaluationMetric(name="Reporting", target="3+ patrol cycles logged", weight=0.4),
        ],
    )


@pytest.fixture
def sample_variant_en() -> Variant:
    return _make_variant(variant_index=3, language="en")


@pytest.fixture
def sample_variant_ar() -> Variant:
    return _make_variant(variant_index=3, language="ar")


@pytest.fixture
def sample_planner_output(sample_seed) -> PlannerOutput:
    return PlannerOutput(seeds=[sample_seed])


@pytest.fixture
def sample_verdict() -> ValidationVerdict:
    return ValidationVerdict(
        passed=True,
        parity_ok=True,
        doctrine_plausible=True,
        issues=[],
    )


@pytest.fixture
def fake_rag():
    rag = MagicMock(spec=DoctrineRAG)
    rag.retrieve.return_value = [
        {
            "source": "ajp-3-2.txt",
            "chunk_index": 0,
            "text": "DOCTRINE A: positive identification before engagement.",
            "score": 0.91,
        },
        {
            "source": "san-remo-roe.txt",
            "chunk_index": 5,
            "text": "DOCTRINE B: proportional response under EoF continuum.",
            "score": 0.87,
        },
    ]
    return rag
