import json

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
)
from msg.domain import Variant
from tests.conftest import make_parsed_response


def _call_kwargs(mock_parse):
    assert mock_parse.call_count == 1
    return mock_parse.call_args.kwargs


@pytest.mark.asyncio
async def test_planner_dispatches_structured_parse(
    fake_openai_client, settings, sample_mission, sample_planner_output
):
    fake_openai_client.chat.completions.parse.return_value = make_parsed_response(
        sample_planner_output
    )
    agent = PlannerAgent(client=fake_openai_client, settings=settings)

    result = await agent.run(sample_mission)

    assert result is sample_planner_output
    kwargs = _call_kwargs(fake_openai_client.chat.completions.parse)
    assert kwargs["model"] == "test-model"
    assert kwargs["response_format"] is PlannerOutput
    messages = kwargs["messages"]
    assert messages[0]["role"] == "system"
    assert "scenario planner" in messages[0]["content"].lower()
    assert messages[1]["role"] == "user"
    assert json.loads(messages[1]["content"]) == sample_mission.model_dump(mode="json")


@pytest.mark.asyncio
async def test_variant_forwards_seed_in_user_payload(
    fake_openai_client, settings, sample_mission, sample_seed, sample_variant_en
):
    fake_openai_client.chat.completions.parse.return_value = make_parsed_response(
        sample_variant_en
    )
    agent = VariantAgent(client=fake_openai_client, settings=settings)

    request = VariantRequest(mission=sample_mission, seed=sample_seed)
    result = await agent.run(request)

    assert result is sample_variant_en
    assert result.language == "en"
    kwargs = _call_kwargs(fake_openai_client.chat.completions.parse)
    assert kwargs["response_format"] is Variant
    user_payload = json.loads(kwargs["messages"][1]["content"])
    assert user_payload["seed"]["variant_index"] == sample_seed.variant_index
    assert user_payload["seed"]["theme"] == sample_seed.theme


@pytest.mark.asyncio
async def test_translator_preserves_variant_index_in_prompt(
    fake_openai_client, settings, sample_variant_en, sample_variant_ar
):
    fake_openai_client.chat.completions.parse.return_value = make_parsed_response(
        sample_variant_ar
    )
    agent = TranslatorAgent(client=fake_openai_client, settings=settings)

    result = await agent.run(sample_variant_en)

    assert result is sample_variant_ar
    assert result.language == "ar"
    assert result.variant_index == sample_variant_en.variant_index
    kwargs = _call_kwargs(fake_openai_client.chat.completions.parse)
    assert kwargs["response_format"] is Variant
    user_payload = json.loads(kwargs["messages"][1]["content"])
    assert user_payload["variant_index"] == sample_variant_en.variant_index
    assert "Modern Standard Arabic" in kwargs["messages"][0]["content"]


@pytest.mark.asyncio
async def test_validator_returns_verdict(
    fake_openai_client, settings, sample_variant_en, sample_variant_ar, sample_verdict
):
    fake_openai_client.chat.completions.parse.return_value = make_parsed_response(
        sample_verdict
    )
    agent = ValidatorAgent(client=fake_openai_client, settings=settings)

    request = ValidatorRequest(en=sample_variant_en, ar=sample_variant_ar)
    result = await agent.run(request)

    assert result is sample_verdict
    kwargs = _call_kwargs(fake_openai_client.chat.completions.parse)
    assert kwargs["response_format"] is ValidationVerdict
    user_payload = json.loads(kwargs["messages"][1]["content"])
    assert user_payload["en"]["language"] == "en"
    assert user_payload["ar"]["language"] == "ar"


@pytest.mark.asyncio
async def test_agent_reraises_openai_errors(
    fake_openai_client, settings, sample_mission
):
    fake_openai_client.chat.completions.parse.side_effect = RuntimeError("boom")
    agent = PlannerAgent(client=fake_openai_client, settings=settings)

    with pytest.raises(RuntimeError, match="boom"):
        await agent.run(sample_mission)


@pytest.mark.asyncio
async def test_agent_raises_on_refusal(
    fake_openai_client, settings, sample_mission
):
    fake_openai_client.chat.completions.parse.return_value = make_parsed_response(
        None, refusal="cannot generate restricted content"
    )
    agent = PlannerAgent(client=fake_openai_client, settings=settings)

    with pytest.raises(RuntimeError, match="refused"):
        await agent.run(sample_mission)


@pytest.mark.asyncio
async def test_agent_raises_when_parsed_is_none(
    fake_openai_client, settings, sample_mission
):
    fake_openai_client.chat.completions.parse.return_value = make_parsed_response(None)
    agent = PlannerAgent(client=fake_openai_client, settings=settings)

    with pytest.raises(RuntimeError, match="no parsed content"):
        await agent.run(sample_mission)


def test_base_agent_rejects_missing_class_attrs(fake_openai_client, settings):
    from msg.agents.base import BaseAgent

    class IncompleteAgent(BaseAgent):
        pass

    with pytest.raises(TypeError, match="PROMPT_FILE"):
        IncompleteAgent(client=fake_openai_client, settings=settings)
