import { ArrowUpRight, PlusSquare } from "lucide-react";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import { Link, useNavigate } from "react-router-dom";

import { ScenarioFiltersPanel } from "@/components/history/ScenarioFilters";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { useScenarios, type ScenarioFilters } from "@/lib/queries";

function formatDate(iso: string, locale: string): string {
  return new Date(iso).toLocaleString(locale, {
    year: "numeric",
    month: "short",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function History() {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const [filters, setFilters] = useState<ScenarioFilters>({});
  const query = useScenarios(filters);
  const rows = query.data ?? [];

  return (
    <div className="space-y-5">
      <header className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">
            {t("history.heading")}
          </h1>
          <p className="text-sm text-slate-400">{t("history.subheading")}</p>
        </div>
        <Button asChild variant="primary" size="md">
          <Link to="/create">
            <PlusSquare className="size-4" aria-hidden />
            <span>{t("history.new")}</span>
          </Link>
        </Button>
      </header>

      <ScenarioFiltersPanel filters={filters} onChange={setFilters} />

      <div className="overflow-hidden rounded-lg border border-slate-800 bg-slate-900/40">
        <table className="w-full">
          <thead className="bg-slate-900/60 text-xs uppercase tracking-wide text-slate-400">
            <tr>
              <th className="px-4 py-3 text-start font-medium">
                {t("history.columns.date")}
              </th>
              <th className="px-4 py-3 text-start font-medium">
                {t("history.columns.missionType")}
              </th>
              <th className="px-4 py-3 text-start font-medium">
                {t("history.columns.difficulty")}
              </th>
              <th className="px-4 py-3 text-start font-medium">
                {t("history.columns.status")}
              </th>
              <th className="w-10 px-4 py-3" />
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800 text-sm">
            {query.isLoading ? (
              Array.from({ length: 6 }).map((_, i) => (
                <tr key={`skel-${i}`}>
                  <td className="px-4 py-3">
                    <Skeleton className="h-4 w-32" />
                  </td>
                  <td className="px-4 py-3">
                    <Skeleton className="h-4 w-24" />
                  </td>
                  <td className="px-4 py-3">
                    <Skeleton className="h-4 w-16" />
                  </td>
                  <td className="px-4 py-3">
                    <Skeleton className="h-4 w-20" />
                  </td>
                  <td className="px-4 py-3" />
                </tr>
              ))
            ) : rows.length === 0 ? (
              <tr>
                <td
                  colSpan={5}
                  className="px-4 py-16 text-center text-sm text-slate-500"
                >
                  <div className="flex flex-col items-center gap-3">
                    <p>{t("history.empty.title")}</p>
                    <Button asChild variant="primary" size="sm">
                      <Link to="/create">{t("history.empty.cta")}</Link>
                    </Button>
                  </div>
                </td>
              </tr>
            ) : (
              rows.map((row) => (
                <tr
                  key={row.id}
                  tabIndex={0}
                  onClick={() => navigate(`/scenarios/${row.id}`)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") navigate(`/scenarios/${row.id}`);
                  }}
                  className="cursor-pointer text-slate-200 transition-colors duration-150 hover:bg-slate-800/60 focus-ring"
                >
                  <td className="px-4 py-3 font-mono text-xs text-slate-300">
                    {formatDate(row.created_at, i18n.language)}
                  </td>
                  <td className="px-4 py-3">
                    {t(`enum.missionType.${row.mission_type}`)}
                  </td>
                  <td className="px-4 py-3">
                    <Badge>{t(`enum.difficulty.${row.difficulty}`)}</Badge>
                  </td>
                  <td className="px-4 py-3 text-slate-400">{row.status}</td>
                  <td className="px-4 py-3 text-end text-slate-500">
                    <ArrowUpRight
                      className="ms-auto size-4 rtl:-scale-x-100"
                      aria-hidden
                    />
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {query.isError ? (
        <div className="rounded-md border border-rose-500/30 bg-rose-500/10 px-4 py-3 text-sm text-rose-300">
          {t("common.error")}
        </div>
      ) : null}
    </div>
  );
}
