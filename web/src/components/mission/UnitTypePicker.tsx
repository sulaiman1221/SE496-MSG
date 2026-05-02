import { useTranslation } from "react-i18next";

import { FRIENDLY_UNIT_TYPES } from "@/lib/constants";
import type { UnitType } from "@/lib/types";
import { cn } from "@/lib/utils";

interface Props {
  selected: UnitType[];
  onChange: (next: UnitType[]) => void;
}

export function UnitTypePicker({ selected, onChange }: Props) {
  const { t } = useTranslation();
  const toggle = (value: UnitType) => {
    if (selected.includes(value)) {
      onChange(selected.filter((s) => s !== value));
    } else {
      onChange([...selected, value]);
    }
  };

  return (
    <div className="grid grid-cols-2 gap-2">
      {FRIENDLY_UNIT_TYPES.map((type) => {
        const active = selected.includes(type);
        return (
          <button
            key={type}
            type="button"
            role="checkbox"
            aria-checked={active}
            onClick={() => toggle(type)}
            className={cn(
              "rounded-md border px-3 py-2 text-sm font-medium transition-colors duration-150 focus-ring",
              active
                ? "border-accent/40 bg-accent/10 text-accent"
                : "border-slate-800 bg-slate-900/60 text-slate-200 hover:border-slate-700 hover:bg-slate-900",
            )}
          >
            {t(`enum.unitType.${type}`)}
          </button>
        );
      })}
    </div>
  );
}
