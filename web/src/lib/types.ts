export type Difficulty = "easy" | "medium" | "hard" | "expert";

export type MissionType = "assault" | "defense" | "ambush";

export type TerrainType = "desert" | "mountain";

export type WeatherType = "clear" | "sandstorm" | "fog";

export type TimeOfDay = "dawn" | "day" | "dusk" | "night";
export type Language = "en" | "ar";
export type ThreatLevel = "low" | "moderate" | "high" | "critical";
export type EnemyThreatLevel = ThreatLevel;
export type ObjectivePriority = "primary" | "secondary";

export type UnitType =
  | "infantry_squad"
  | "mechanized_platoon"
  | "armor_section"
  | "special_forces_team"
  | "support_element";

type WeaponCategory =
  | "rifle"
  | "machine_gun"
  | "pistol"
  | "grenade_launcher"
  | "sniper_rifle"
  | "anti_armor"
  | "artillery"
  | "missile"
  | "other";

type VehicleCategory =
  | "tank"
  | "apc"
  | "jeep"
  | "truck"
  | "helicopter"
  | "drone"
  | "boat"
  | "aircraft"
  | "other";

export interface MissionEnvironmentHints {
  terrain?: string | null;
  weather?: string | null;
  time_of_day?: string | null;
  region?: string | null;
  visibility_pct?: number | null;
}

export interface Mission {
  mission_type: MissionType;
  difficulty?: Difficulty;
  title?: string | null;
  environment?: MissionEnvironmentHints;
  aircraft?: string[];
  friendly_unit_types?: UnitType[];
  enemy_threat_level?: EnemyThreatLevel | null;
  additional_context?: string | null;
  n_variants?: number;
}

export interface Environment {
  terrain: TerrainType;
  weather: WeatherType;
  time_of_day: TimeOfDay;
  region: string;
  visibility: string;
  hazards: string[];
}

export interface Weapon {
  name: string;
  category: WeaponCategory;
  quantity: number;
}

export interface Vehicle {
  name: string;
  category: VehicleCategory;
  quantity: number;
}

export interface Unit {
  designation: string;
  size: number;
  role: string;
  weapons: Weapon[];
  vehicles: Vehicle[];
}

export interface Objective {
  id: string;
  description: string;
  priority: ObjectivePriority;
}

export interface Phase {
  order: number;
  name: string;
  duration_minutes: number;
  description: string;
  success_criteria: string[];
}

export interface DecisionPoint {
  at_phase: number;
  description: string;
  options: string[];
}

export interface EvaluationMetric {
  name: string;
  target: string;
  weight: number;
}

export interface Variant {
  variant_index: number;
  language: Language;
  title: string;
  summary: string;
  mission_type: MissionType;
  difficulty: Difficulty;
  threat_level: ThreatLevel;
  environment: Environment;
  objectives: Objective[];
  phases: Phase[];
  rules_of_engagement: string[];
  decision_points: DecisionPoint[];
  friendly_forces: Unit[];
  opposing_forces: Unit[];
  evaluation_metrics: EvaluationMetric[];
}

export interface ScenarioVariant {
  id: string;
  scenario_id: string;
  language: Language;
  variant_index: number;
  payload: Variant;
  validated: boolean;
}

export interface Scenario {
  id: string;
  created_at: string;
  mission: Mission;
  status: string;
  model: string;
  variants: ScenarioVariant[];
}

export interface ScenarioSummary {
  id: string;
  created_at: string;
  mission_type: string;
  difficulty: string;
  status: string;
}
