import { ArrowLeft, AlertTriangle, Download, ImageIcon } from "lucide-react";
import { useMemo } from "react";
import { useTranslation } from "react-i18next";
import { Link, useParams } from "react-router-dom";

import { VariantCard } from "@/components/scenario/VariantCard";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useScenario } from "@/lib/queries";
import type { Language, Scenario, ScenarioVariant } from "@/lib/types";

function selectVariants(
  variants: ScenarioVariant[],
  language: Language,
): ScenarioVariant[] {
  return variants
    .filter((v) => v.language === language)
    .sort((a, b) => a.variant_index - b.variant_index);
}

function formatDate(iso: string, locale: string): string {
  return new Date(iso).toLocaleString(locale, {
    year: "numeric",
    month: "long",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

async function downloadImage(scenario: Scenario): Promise<void> {
  if (!scenario.image_url) return;
  const response = await fetch(scenario.image_url);
  const blob = await response.blob();
  const objectUrl = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = objectUrl;
  link.download = `scenario-${scenario.id.slice(0, 8)}.png`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(objectUrl);
}

export function ScenarioReview() {
  const { t, i18n } = useTranslation();
  const { scenarioId } = useParams<{ scenarioId: string }>();
  const query = useScenario(scenarioId);

  const currentLanguage: Language = i18n.language.startsWith("ar")
    ? "ar"
    : "en";

  const visible = useMemo(() => {
    if (!query.data) return [];
    return selectVariants(query.data.variants, currentLanguage);
  }, [query.data, currentLanguage]);

  if (query.isLoading) {
    return <ScenarioSkeleton />;
  }

  if (query.isError || !query.data) {
    return (
      <div className="flex flex-col items-start gap-4">
        <div className="flex items-center gap-2 text-rose-400">
          <AlertTriangle className="size-5" aria-hidden />
          <span className="text-sm font-medium">
            {t("review.notFound")}
          </span>
        </div>
        <Button asChild variant="ghost" size="sm">
          <Link to="/history">
            <ArrowLeft className="size-4 rtl:-scale-x-100" aria-hidden />
            <span>{t("review.backToHistory")}</span>
          </Link>
        </Button>
      </div>
    );
  }

  const scenario = query.data;

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div className="flex flex-col gap-1">
          <h1 className="text-2xl font-semibold tracking-tight">
            {t("review.heading")}
          </h1>
          <p className="text-sm text-slate-400">
            {t("review.subheading", {
              count: visible.length,
              language:
                currentLanguage === "ar"
                  ? t("common.arabic")
                  : t("common.english"),
            })}
          </p>
        </div>
        <Button asChild variant="ghost" size="sm">
          <Link to="/history">
            <ArrowLeft className="size-4 rtl:-scale-x-100" aria-hidden />
            <span>{t("review.backToHistory")}</span>
          </Link>
        </Button>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <div className="grid grid-cols-2 gap-x-6 gap-y-3">
              <MetaItem
                label={t("review.meta.created")}
                value={formatDate(scenario.created_at, i18n.language)}
              />
              <MetaItem
                label={t("review.meta.missionType")}
                value={t(`enum.missionType.${scenario.mission.mission_type}`)}
              />
              <MetaItem
                label={t("review.meta.difficulty")}
                value={t(`enum.difficulty.${scenario.mission.difficulty}`)}
              />
              <MetaItem
                label={t("review.meta.model")}
                value={scenario.model}
                mono
              />
            </div>
          </CardHeader>
        </Card>

        <Card className="overflow-hidden">
          {scenario.image_url ? (
            <>
              <img
                src={scenario.image_url}
                alt=""
                className="aspect-square w-full object-cover"
              />
              <CardContent className="flex justify-end pt-3">
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={() => {
                    void downloadImage(scenario);
                  }}
                >
                  <Download className="size-4" aria-hidden />
                  <span>{t("review.downloadImage")}</span>
                </Button>
              </CardContent>
            </>
          ) : (
            <div
              className="flex aspect-square w-full items-center justify-center bg-gradient-to-br from-slate-800 to-slate-950"
              aria-hidden
            >
              <ImageIcon className="size-12 text-slate-700" />
            </div>
          )}
        </Card>
      </div>

      {visible.length === 0 ? (
        <Card>
          <CardContent className="py-10 text-center text-sm text-slate-500">
            {t("review.noVariantsInLanguage")}
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {visible.map((entry) => (
            <VariantCard
              key={entry.id}
              variant={entry.payload}
              validated={entry.validated}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function MetaItem({
  label,
  value,
  mono = false,
}: {
  label: string;
  value: string;
  mono?: boolean;
}) {
  return (
    <div className="flex flex-col">
      <span className="text-[10px] uppercase tracking-wider text-slate-500">
        {label}
      </span>
      <span
        className={`mt-1 text-sm text-slate-200 ${mono ? "font-mono text-xs" : ""}`}
      >
        {value}
      </span>
    </div>
  );
}

function ScenarioSkeleton() {
  return (
    <div className="space-y-5">
      <Skeleton className="h-8 w-56" />
      <div className="grid gap-4 lg:grid-cols-2">
        <Skeleton className="h-44 w-full" />
        <Skeleton className="aspect-square w-full" />
      </div>
      {Array.from({ length: 5 }).map((_, i) => (
        <Skeleton key={i} className="h-56 w-full" />
      ))}
    </div>
  );
}
