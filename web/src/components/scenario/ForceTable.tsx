import { useTranslation } from "react-i18next";

import type { Unit } from "@/lib/types";

export function ForceTable({ units }: { units: Unit[] }) {
  const { t } = useTranslation();

  if (units.length === 0) {
    return (
      <p className="text-sm text-slate-500">{t("variant.noUnits")}</p>
    );
  }

  return (
    <div className="overflow-x-auto rounded-md border border-slate-800">
      <table className="w-full text-sm">
        <thead className="bg-slate-900/60 text-xs uppercase tracking-wide text-slate-400">
          <tr>
            <th className="px-3 py-2 text-start font-medium">
              {t("variant.force.designation")}
            </th>
            <th className="px-3 py-2 text-start font-medium">
              {t("variant.force.size")}
            </th>
            <th className="px-3 py-2 text-start font-medium">
              {t("variant.force.role")}
            </th>
            <th className="px-3 py-2 text-start font-medium">
              {t("variant.force.weapons")}
            </th>
            <th className="px-3 py-2 text-start font-medium">
              {t("variant.force.vehicles")}
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-800">
          {units.map((unit) => (
            <tr key={unit.designation} className="text-slate-200">
              <td className="px-3 py-2 font-medium">{unit.designation}</td>
              <td className="px-3 py-2 font-mono text-slate-300">
                {unit.size}
              </td>
              <td className="px-3 py-2 text-slate-300">{unit.role}</td>
              <td className="px-3 py-2 text-slate-400">
                {unit.weapons
                  .map((w) => `${w.name} ×${w.quantity}`)
                  .join(", ") || "—"}
              </td>
              <td className="px-3 py-2 text-slate-400">
                {unit.vehicles
                  .map((v) => `${v.name} ×${v.quantity}`)
                  .join(", ") || "—"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
