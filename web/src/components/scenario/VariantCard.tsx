import { ChevronRight, Download } from "lucide-react";
import { useTranslation } from "react-i18next";

import { ForceTable } from "@/components/scenario/ForceTable";
import { MetricBar } from "@/components/scenario/MetricBar";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { ThreatLevel, Variant } from "@/lib/types";
import { cn } from "@/lib/utils";

const THREAT_VARIANT: Record<
  ThreatLevel,
  "info" | "success" | "warning" | "danger"
> = {
  low: "success",
  moderate: "info",
  high: "warning",
  critical: "danger",
};

function downloadVariant(variant: Variant) {
  const blob = new Blob([JSON.stringify(variant, null, 2)], {
    type: "application/json",
  });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `variant-${variant.variant_index}-${variant.language}.json`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

function Section({
  title,
  children,
  defaultOpen = false,
}: {
  title: string;
  children: React.ReactNode;
  defaultOpen?: boolean;
}) {
  return (
    <details
      open={defaultOpen}
      className="group rounded-md border border-slate-800 bg-slate-950/40 open:bg-slate-950/60"
    >
      <summary className="flex cursor-pointer select-none items-center justify-between px-4 py-3 text-sm font-medium text-slate-200 transition-colors hover:bg-slate-900/50">
        <span>{title}</span>
        <ChevronRight className="size-4 text-slate-500 transition-transform duration-150 group-open:rotate-90 rtl:rotate-180 rtl:group-open:-rotate-90" />
      </summary>
      <div className="border-t border-slate-800 px-4 py-3 text-sm text-slate-300">
        {children}
      </div>
    </details>
  );
}

export function VariantCard({
  variant,
  validated,
}: {
  variant: Variant;
  validated: boolean;
}) {
  const { t } = useTranslation();

  return (
    <Card>
      <CardHeader className="gap-3">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div className="flex flex-col gap-1">
            <div className="flex items-center gap-2 text-xs text-slate-500">
              <span className="font-mono">
                #{String(variant.variant_index + 1).padStart(2, "0")}
              </span>
              <span>·</span>
              <Badge variant={THREAT_VARIANT[variant.threat_level]}>
                {t(`enum.threatLevel.${variant.threat_level}`)}
              </Badge>
              <Badge variant={validated ? "success" : "warning"}>
                {t(
                  validated
                    ? "variant.status.validated"
                    : "variant.status.needsReview",
                )}
              </Badge>
            </div>
            <CardTitle className="text-lg">{variant.title}</CardTitle>
          </div>
          <Button
            type="button"
            variant="ghost"
            size="sm"
            onClick={() => downloadVariant(variant)}
          >
            <Download className="size-4" aria-hidden />
            <span>{t("common.download")}</span>
          </Button>
        </div>
        <p className="text-sm text-slate-300">{variant.summary}</p>
        <dl
          className={cn(
            "mt-1 grid grid-cols-2 gap-x-6 gap-y-2 text-xs text-slate-400 md:grid-cols-4",
          )}
        >
          <MetaEntry
            label={t("variant.environment.terrain")}
            value={t(`enum.terrain.${variant.environment.terrain}`)}
          />
          <MetaEntry
            label={t("variant.environment.weather")}
            value={t(`enum.weather.${variant.environment.weather}`)}
          />
          <MetaEntry
            label={t("variant.environment.timeOfDay")}
            value={t(`enum.timeOfDay.${variant.environment.time_of_day}`)}
          />
          <MetaEntry
            label={t("variant.environment.region")}
            value={variant.environment.region}
          />
        </dl>
      </CardHeader>
      <CardContent className="space-y-3">
        <Section title={t("variant.sections.objectives")} defaultOpen>
          <ul className="space-y-2">
            {variant.objectives.map((objective) => (
              <li
                key={objective.id}
                className="flex items-start gap-3"
              >
                <Badge
                  variant={
                    objective.priority === "primary" ? "info" : "default"
                  }
                  className="mt-0.5"
                >
                  {t(`enum.priority.${objective.priority}`)}
                </Badge>
                <span>{objective.description}</span>
              </li>
            ))}
          </ul>
        </Section>

        <Section title={t("variant.sections.phases")}>
          <ol className="space-y-3">
            {variant.phases.map((phase) => (
              <li key={phase.order} className="rounded-md bg-slate-900/50 p-3">
                <div className="flex items-baseline justify-between gap-3">
                  <span className="font-medium text-slate-200">
                    {phase.order}. {phase.name}
                  </span>
                  <span className="font-mono text-xs text-slate-500">
                    {phase.duration_minutes} {t("variant.minutes")}
                  </span>
                </div>
                <p className="mt-1 text-slate-400">{phase.description}</p>
                <ul className="mt-2 list-disc space-y-1 ps-5 text-slate-300 marker:text-slate-600">
                  {phase.success_criteria.map((criterion) => (
                    <li key={criterion}>{criterion}</li>
                  ))}
                </ul>
              </li>
            ))}
          </ol>
        </Section>

        <Section title={t("variant.sections.rulesOfEngagement")}>
          <ul className="list-disc space-y-1 ps-5 marker:text-slate-600">
            {variant.rules_of_engagement.map((rule) => (
              <li key={rule}>{rule}</li>
            ))}
          </ul>
        </Section>

        <Section title={t("variant.sections.decisionPoints")}>
          <ul className="space-y-3">
            {variant.decision_points.map((dp) => (
              <li
                key={`${dp.at_phase}:${dp.description}`}
                className="rounded-md bg-slate-900/50 p-3"
              >
                <div className="text-xs text-slate-500">
                  {t("variant.atPhase", { phase: dp.at_phase })}
                </div>
                <p className="mt-1 text-slate-200">{dp.description}</p>
                <ul className="mt-2 flex flex-wrap gap-2">
                  {dp.options.map((option) => (
                    <li
                      key={option}
                      className="rounded-full border border-slate-700 bg-slate-900 px-2.5 py-0.5 text-xs text-slate-300"
                    >
                      {option}
                    </li>
                  ))}
                </ul>
              </li>
            ))}
          </ul>
        </Section>

        <Section title={t("variant.sections.friendlyForces")}>
          <ForceTable units={variant.friendly_forces} />
        </Section>

        <Section title={t("variant.sections.opposingForces")}>
          <ForceTable units={variant.opposing_forces} />
        </Section>

        <Section title={t("variant.sections.evaluationMetrics")}>
          <div className="space-y-4">
            {variant.evaluation_metrics.map((metric) => (
              <MetricBar key={metric.name} metric={metric} />
            ))}
          </div>
        </Section>
      </CardContent>
    </Card>
  );
}

function MetaEntry({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex flex-col">
      <dt className="text-[10px] uppercase tracking-wider text-slate-500">
        {label}
      </dt>
      <dd className="mt-0.5 text-slate-200">{value}</dd>
    </div>
  );
}
