import { Check } from "lucide-react";

import { type RsafAsset } from "@/lib/rsaf-aircraft";
import { cn } from "@/lib/utils";

interface Props {
  catalog: readonly RsafAsset[];
  selected: string[];
  onChange: (next: string[]) => void;
}

export function AircraftPicker({ catalog, selected, onChange }: Props) {
  const isSelected = (name: string) => selected.includes(name);

  const toggle = (name: string) => {
    if (isSelected(name)) {
      onChange(selected.filter((s) => s !== name));
    } else {
      onChange([...selected, name]);
    }
  };

  return (
    <div className="max-h-72 overflow-y-auto rounded-md border border-slate-800 bg-slate-950/40 p-2">
      <ul className="flex flex-col gap-1.5">
        {catalog.map((asset) => {
          const active = isSelected(asset.name);
          return (
            <li key={asset.id}>
              <button
                type="button"
                role="checkbox"
                aria-checked={active}
                onClick={() => toggle(asset.name)}
                className={cn(
                  "flex w-full items-center justify-between gap-3 rounded-md border px-3 py-2 text-start transition-colors duration-150 focus-ring",
                  active
                    ? "border-accent/40 bg-accent/10"
                    : "border-slate-800 bg-slate-900/60 hover:border-slate-700 hover:bg-slate-900",
                )}
              >
                <div className="flex flex-col gap-0.5">
                  <span
                    className={cn(
                      "text-sm font-medium",
                      active ? "text-accent" : "text-slate-100",
                    )}
                  >
                    {asset.name}
                  </span>
                  <span className="text-xs text-slate-400">
                    {asset.type} <span className="text-accent">•</span>{" "}
                    {asset.role}
                  </span>
                </div>
                {active ? (
                  <Check className="size-4 text-accent" aria-hidden />
                ) : null}
              </button>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
