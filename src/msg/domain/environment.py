from typing import Literal

from pydantic import BaseModel, ConfigDict

TimeOfDay = Literal["dawn", "day", "dusk", "night"]

TerrainType = Literal[
    "desert", "mountain", "urban", "coast", "valley", "oasis"
]

WeatherType = Literal[
    "clear", "sandstorm", "fog", "rain", "thunderstorm", "windy"
]


class Environment(BaseModel):
    model_config = ConfigDict(extra="forbid")

    terrain: TerrainType
    weather: WeatherType
    time_of_day: TimeOfDay
    region: str
    visibility: str
    hazards: list[str]
