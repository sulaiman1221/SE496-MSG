import base64
import logging

from openai import AsyncOpenAI

from msg.domain import Variant

_log = logging.getLogger(__name__)


def _build_prompt(variant: Variant) -> str:
    env = variant.environment
    return (
        "Cinematic, photorealistic establishing shot of a military training scenario. "
        f"{env.terrain.title()} terrain, {env.weather} weather conditions, {env.time_of_day} lighting. "
        f"{variant.summary[:300]} "
        "Square composition, atmospheric, no text, no UI elements, no on-screen markings, no logos."
    )


async def generate_scenario_image_bytes(
    client: AsyncOpenAI, variant: Variant, model: str
) -> bytes | None:
    try:
        response = await client.images.generate(
            model=model,
            prompt=_build_prompt(variant),
            size="1024x1024",
            quality="low",
            n=1,
        )
        b64 = response.data[0].b64_json
        if not b64:
            _log.warning("image generation returned no data")
            return None
        return base64.b64decode(b64)
    except Exception as exc:
        _log.warning("image generation failed: %s", exc)
        return None
