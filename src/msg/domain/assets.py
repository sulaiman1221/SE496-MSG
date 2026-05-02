from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

WeaponCategory = Literal[
    "rifle",
    "machine_gun",
    "pistol",
    "grenade_launcher",
    "sniper_rifle",
    "anti_armor",
    "artillery",
    "missile",
    "other",
]

VehicleCategory = Literal[
    "tank",
    "apc",
    "jeep",
    "truck",
    "helicopter",
    "drone",
    "boat",
    "aircraft",
    "other",
]


class Weapon(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    category: WeaponCategory
    quantity: int = Field(ge=1)


class Vehicle(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    category: VehicleCategory
    quantity: int = Field(ge=1)


class Unit(BaseModel):
    model_config = ConfigDict(extra="forbid")

    designation: str
    size: int = Field(ge=1)
    role: str
    weapons: list[Weapon]
    vehicles: list[Vehicle]
