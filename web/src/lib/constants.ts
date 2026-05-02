import type {
  Difficulty,
  EnemyThreatLevel,
  MissionType,
  TerrainType,
  TimeOfDay,
  UnitType,
  WeatherType,
} from "@/lib/types";

export const MISSION_TYPES = [
  "assault",
  "defense",
  "ambush",
] as const satisfies readonly MissionType[];

export const DIFFICULTIES = [
  "easy",
  "medium",
  "hard",
  "expert",
] as const satisfies readonly Difficulty[];

export const TERRAIN_TYPES = [
  "desert",
  "mountain",
] as const satisfies readonly TerrainType[];

export const WEATHER_TYPES = [
  "clear",
  "sandstorm",
  "fog",
] as const satisfies readonly WeatherType[];

export const TIMES_OF_DAY = [
  "dawn",
  "day",
  "dusk",
  "night",
] as const satisfies readonly TimeOfDay[];

export const FRIENDLY_UNIT_TYPES = [
  "infantry_squad",
  "mechanized_platoon",
  "armor_section",
  "special_forces_team",
  "support_element",
] as const satisfies readonly UnitType[];

export const ENEMY_THREAT_LEVELS = [
  "low",
  "moderate",
  "high",
  "critical",
] as const satisfies readonly EnemyThreatLevel[];

export const DEFAULT_VARIANT_COUNT = 5;
export const MAX_VARIANT_COUNT = 10;
export const MIN_VARIANT_COUNT = 1;
export const DEFAULT_VISIBILITY_PCT = 50;
export const DEFAULT_THREAT_LEVEL: EnemyThreatLevel = "moderate";
