export interface RsafAsset {
  id: string;
  name: string;
  type: string;
  role: string;
}

export const RSAF_AIRCRAFT: readonly RsafAsset[] = [
  { id: "f15sa", name: "F-15SA Strike Eagle", type: "Fighter", role: "Multirole" },
  { id: "f15c", name: "F-15C Eagle", type: "Fighter", role: "Air Superiority" },
  { id: "f15d", name: "F-15D Eagle", type: "Fighter", role: "Trainer/Combat" },
  { id: "tornado", name: "Tornado IDS", type: "Fighter", role: "Strike" },
  { id: "typhoon", name: "Typhoon", type: "Fighter", role: "Multirole" },
  { id: "f5", name: "F-5 Tiger II", type: "Fighter", role: "Light Attack" },
  { id: "hawk", name: "BAE Hawk Mk.65", type: "Trainer", role: "Advanced" },
  { id: "pc21", name: "Pilatus PC-21", type: "Trainer", role: "Basic" },
  { id: "apache", name: "AH-64E Apache", type: "Helicopter", role: "Attack" },
  { id: "blackhawk", name: "UH-60 Black Hawk", type: "Helicopter", role: "Utility" },
  { id: "cougar", name: "AS532 Cougar", type: "Helicopter", role: "Utility" },
  { id: "c130", name: "C-130H Hercules", type: "Transport", role: "Tactical" },
  { id: "a330mrtt", name: "A330 MRTT", type: "Tanker", role: "Air Refueling" },
  { id: "e3a", name: "E-3A Sentry", type: "AEW&C", role: "Airborne Command" },
  { id: "ch4b", name: "CH-4B", type: "UAV", role: "Strike" },
  { id: "wingloong", name: "Wing Loong II", type: "UAV", role: "MALE Combat" },
] as const;
