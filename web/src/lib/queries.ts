import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";

import { api } from "@/lib/api";
import type {
  Difficulty,
  Mission,
  MissionType,
  Scenario,
  ScenarioSummary,
} from "@/lib/types";

export interface ScenarioFilters {
  mission_type?: MissionType;
  difficulty?: Difficulty;
  date_from?: string;
  date_to?: string;
  limit?: number;
  offset?: number;
}

export function useCreateScenario() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (mission: Mission) =>
      api.post<Scenario>("/scenarios", mission),
    onSuccess: (scenario) => {
      queryClient.setQueryData(["scenario", scenario.id], scenario);
      queryClient.invalidateQueries({ queryKey: ["scenarios"] });
    },
  });
}

export function useScenario(id: string | undefined) {
  return useQuery({
    queryKey: ["scenario", id],
    queryFn: () => api.get<Scenario>(`/scenarios/${id}`),
    enabled: Boolean(id),
  });
}

function toQueryString(filters: ScenarioFilters): string {
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(filters)) {
    if (value === undefined || value === null || value === "") continue;
    params.set(key, String(value));
  }
  const qs = params.toString();
  return qs ? `?${qs}` : "";
}

export function useScenarios(filters: ScenarioFilters = {}) {
  return useQuery({
    queryKey: ["scenarios", filters],
    queryFn: () =>
      api.get<ScenarioSummary[]>(`/scenarios${toQueryString(filters)}`),
  });
}
