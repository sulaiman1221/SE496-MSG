import { useTranslation } from "react-i18next";

import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { DIFFICULTIES, MISSION_TYPES } from "@/lib/constants";
import type { ScenarioFilters as Filters } from "@/lib/queries";
import type { Difficulty, MissionType } from "@/lib/types";

const ANY_VALUE = "__any__";

interface Props {
  filters: Filters;
  onChange: (next: Filters) => void;
}

export function ScenarioFiltersPanel({ filters, onChange }: Props) {
  const { t } = useTranslation();

  return (
    <div className="grid grid-cols-1 gap-4 rounded-lg border border-slate-800 bg-slate-900/40 p-4 md:grid-cols-2 lg:grid-cols-4">
      <div className="space-y-1.5">
        <Label htmlFor="filter-mission-type">
          {t("history.filters.missionType")}
        </Label>
        <Select
          value={filters.mission_type ?? ANY_VALUE}
          onValueChange={(value) =>
            onChange({
              ...filters,
              mission_type:
                value === ANY_VALUE ? undefined : (value as MissionType),
            })
          }
        >
          <SelectTrigger id="filter-mission-type">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value={ANY_VALUE}>{t("common.any")}</SelectItem>
            {MISSION_TYPES.map((type) => (
              <SelectItem key={type} value={type}>
                {t(`enum.missionType.${type}`)}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="space-y-1.5">
        <Label htmlFor="filter-difficulty">
          {t("history.filters.difficulty")}
        </Label>
        <Select
          value={filters.difficulty ?? ANY_VALUE}
          onValueChange={(value) =>
            onChange({
              ...filters,
              difficulty:
                value === ANY_VALUE ? undefined : (value as Difficulty),
            })
          }
        >
          <SelectTrigger id="filter-difficulty">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value={ANY_VALUE}>{t("common.any")}</SelectItem>
            {DIFFICULTIES.map((d) => (
              <SelectItem key={d} value={d}>
                {t(`enum.difficulty.${d}`)}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="space-y-1.5">
        <Label htmlFor="filter-date-from">
          {t("history.filters.dateFrom")}
        </Label>
        <Input
          id="filter-date-from"
          type="date"
          value={filters.date_from ?? ""}
          onChange={(e) =>
            onChange({ ...filters, date_from: e.target.value || undefined })
          }
        />
      </div>

      <div className="space-y-1.5">
        <Label htmlFor="filter-date-to">{t("history.filters.dateTo")}</Label>
        <Input
          id="filter-date-to"
          type="date"
          value={filters.date_to ?? ""}
          onChange={(e) =>
            onChange({ ...filters, date_to: e.target.value || undefined })
          }
        />
      </div>
    </div>
  );
}
