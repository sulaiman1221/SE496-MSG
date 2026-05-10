import base64
import logging

from openai import AsyncOpenAI

from msg.domain import Variant

_log = logging.getLogger(__name__)


def _build_atmospheric_prompt(variant: Variant) -> str:
    env = variant.environment
    return (
        "Cinematic, photorealistic establishing shot of a military training scenario. "
        f"{env.terrain.title()} terrain, {env.weather} weather conditions, {env.time_of_day} lighting. "
        f"{variant.summary[:300]} "
        "Square composition, atmospheric, no text, no UI elements, no on-screen markings, no logos."
    )


def _build_tactical_map_prompt(variant: Variant) -> str:
    env = variant.environment
    return (
        "Generate a clean tactical military map of an area inside Saudi Arabia "
        "using NATO symbols. "
        f"{variant.mission_type.title()} operation in {env.terrain} terrain "
        f"around {env.region}. "
        "Show real Saudi cities, roads, and geographic features in that region. "
        "Blue friendly forces on the west, red enemy forces on the east, "
        "sandy parchment background, grid lines, north arrow, legend panel."
    )


async def _generate_image_bytes(
    client: AsyncOpenAI, model: str, prompt: str, label: str
) -> bytes | None:
    try:
        response = await client.images.generate(
            model=model,
            prompt=prompt,
            size="1024x1024",
            quality="low",
            n=1,
        )
        b64 = response.data[0].b64_json
        if not b64:
            _log.warning("%s generation returned no data", label)
            return None
        return base64.b64decode(b64)
    except Exception as exc:
        _log.warning("%s generation failed: %s", label, exc)
        return None


async def generate_scenario_image_bytes(
    client: AsyncOpenAI, variant: Variant, model: str
) -> bytes | None:
    return await _generate_image_bytes(
        client, model, _build_atmospheric_prompt(variant), "atmospheric image"
    )


async def generate_tactical_map_bytes(
    client: AsyncOpenAI, variant: Variant, model: str
) -> bytes | None:
    return await _generate_image_bytes(
        client, model, _build_tactical_map_prompt(variant), "tactical map"
    )
