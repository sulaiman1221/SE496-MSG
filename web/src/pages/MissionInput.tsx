import { zodResolver } from "@hookform/resolvers/zod";
import { Loader2 } from "lucide-react";
import { Controller, useForm } from "react-hook-form";
import { useTranslation } from "react-i18next";
import { useNavigate } from "react-router-dom";
import { z } from "zod";

import { AircraftPicker } from "@/components/mission/AircraftPicker";
import { UnitTypePicker } from "@/components/mission/UnitTypePicker";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { GlassButton } from "@/components/ui/glass-button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { LoadingOverlay } from "@/components/ui/LoadingOverlay";
import {
  Segmented,
  type SegmentedOption,
} from "@/components/ui/segmented";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Slider } from "@/components/ui/slider";
import { Textarea } from "@/components/ui/textarea";
import {
  DEFAULT_THREAT_LEVEL,
  DEFAULT_VARIANT_COUNT,
  DEFAULT_VISIBILITY_PCT,
  ENEMY_THREAT_LEVELS,
  MAX_VARIANT_COUNT,
  MIN_VARIANT_COUNT,
  MISSION_TYPES,
  TERRAIN_TYPES,
  TIMES_OF_DAY,
  WEATHER_TYPES,
} from "@/lib/constants";
import { useCreateScenario } from "@/lib/queries";
import { RSAF_AIRCRAFT } from "@/lib/rsaf-aircraft";
import type { Mission, TimeOfDay, UnitType } from "@/lib/types";

const AUTO = "__auto__";

const schema = z.object({
  mission_type: z.enum(MISSION_TYPES),
  title: z.string().max(120).optional(),
  terrain: z.enum(TERRAIN_TYPES).optional(),
  weather: z.enum(WEATHER_TYPES).optional(),
  time_of_day: z.enum(TIMES_OF_DAY).optional(),
  visibility_pct: z.number().int().min(0).max(100),
  aircraft: z.array(z.string()),
  friendly_unit_types: z.array(
    z.enum([
      "land_forces",
      "air_force",
      "naval_forces",
      "air_defense_forces",
      "strategic_missile_force",
      "medical_support",
    ]),
  ),
  enemy_threat_level: z.enum(ENEMY_THREAT_LEVELS),
  additional_context: z.string().max(2000).optional(),
  n_variants: z
    .number()
    .int()
    .min(MIN_VARIANT_COUNT)
    .max(MAX_VARIANT_COUNT),
});

type FormValues = z.infer<typeof schema>;

function toMission(values: FormValues): Mission {
  return {
    mission_type: values.mission_type,
    title: values.title?.trim() || null,
    environment: {
      terrain: values.terrain ?? null,
      weather: values.weather ?? null,
      time_of_day: values.time_of_day ?? null,
      visibility_pct: values.visibility_pct,
    },
    aircraft: values.aircraft,
    friendly_unit_types: values.friendly_unit_types,
    enemy_threat_level: values.enemy_threat_level,
    additional_context: values.additional_context?.trim() || null,
    n_variants: values.n_variants,
  };
}

export function MissionInput() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const mutation = useCreateScenario();

  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      mission_type: "assault",
      title: "",
      terrain: "desert",
      weather: "clear",
      time_of_day: "day",
      visibility_pct: DEFAULT_VISIBILITY_PCT,
      aircraft: [],
      friendly_unit_types: [],
      enemy_threat_level: DEFAULT_THREAT_LEVEL,
      additional_context: "",
      n_variants: DEFAULT_VARIANT_COUNT,
    },
  });

  const onSubmit = form.handleSubmit(async (values) => {
    try {
      const scenario = await mutation.mutateAsync(toMission(values));
      navigate(`/scenarios/${scenario.id}`);
    } catch {
      // surfaced via mutation.isError below
    }
  });

  const timeOfDayOptions: readonly SegmentedOption<TimeOfDay>[] = [
    { value: "dawn", label: t("enum.timeOfDay.dawn") },
    { value: "day", label: t("enum.timeOfDay.day") },
    { value: "dusk", label: t("enum.timeOfDay.dusk") },
    { value: "night", label: t("enum.timeOfDay.night") },
  ];

  const variantCount = form.watch("n_variants");
  const visibility = form.watch("visibility_pct");

  return (
    <>
    {mutation.isPending ? (
      <LoadingOverlay
        title={t("missionInput.generating")}
        subtitle={t("missionInput.hints.generating", { n: variantCount })}
      />
    ) : null}
    <form onSubmit={onSubmit} className="space-y-5">
      <header>
        <h1 className="text-xl font-semibold tracking-tight">
          {t("missionInput.heading")}
        </h1>
      </header>

      <Accordion
        type="multiple"
        defaultValue={["mission", "environment"]}
        className="space-y-3"
      >
        <AccordionItem value="mission">
          <AccordionTrigger>
            {t("missionInput.sections.mission.title")}
          </AccordionTrigger>
          <AccordionContent className="space-y-4">
            <div className="space-y-1.5">
              <Label htmlFor="mission-type">
                {t("missionInput.fields.missionType")}
              </Label>
              <Controller
                name="mission_type"
                control={form.control}
                render={({ field }) => (
                  <Select value={field.value} onValueChange={field.onChange}>
                    <SelectTrigger id="mission-type">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {MISSION_TYPES.map((type) => (
                        <SelectItem key={type} value={type}>
                          {t(`enum.missionType.${type}`)}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                )}
              />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="title">
                {t("missionInput.fields.title")}
              </Label>
              <Input id="title" {...form.register("title")} />
            </div>
          </AccordionContent>
        </AccordionItem>

        <AccordionItem value="environment">
          <AccordionTrigger>
            {t("missionInput.sections.environment.title")}
          </AccordionTrigger>
          <AccordionContent className="space-y-4">
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              <div className="space-y-1.5">
                <Label htmlFor="terrain">
                  {t("missionInput.fields.terrain")}
                </Label>
                <Controller
                  name="terrain"
                  control={form.control}
                  render={({ field }) => (
                    <Select
                      value={field.value ?? AUTO}
                      onValueChange={(v) =>
                        field.onChange(v === AUTO ? undefined : v)
                      }
                    >
                      <SelectTrigger id="terrain">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
{TERRAIN_TYPES.map((option) => (
                          <SelectItem key={option} value={option}>
                            {t(`enum.terrain.${option}`)}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  )}
                />
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="weather">
                  {t("missionInput.fields.weather")}
                </Label>
                <Controller
                  name="weather"
                  control={form.control}
                  render={({ field }) => (
                    <Select
                      value={field.value ?? AUTO}
                      onValueChange={(v) =>
                        field.onChange(v === AUTO ? undefined : v)
                      }
                    >
                      <SelectTrigger id="weather">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
{WEATHER_TYPES.map((option) => (
                          <SelectItem key={option} value={option}>
                            {t(`enum.weather.${option}`)}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  )}
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label>{t("missionInput.fields.timeOfDay")}</Label>
              <Controller
                name="time_of_day"
                control={form.control}
                render={({ field }) => (
                  <Segmented
                    options={timeOfDayOptions}
                    value={field.value}
                    onChange={field.onChange}
                    aria-label={t("missionInput.fields.timeOfDay")}
                  />
                )}
              />
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label htmlFor="visibility">
                  {t("missionInput.fields.visibility")}
                </Label>
                <span className="font-mono text-xs text-slate-400">
                  {visibility}%
                </span>
              </div>
              <Controller
                name="visibility_pct"
                control={form.control}
                render={({ field }) => (
                  <Slider
                    id="visibility"
                    min={0}
                    max={100}
                    step={5}
                    value={[field.value]}
                    onValueChange={(value) => field.onChange(value[0])}
                    thumbAriaLabel={t("missionInput.fields.visibility")}
                  />
                )}
              />
            </div>
          </AccordionContent>
        </AccordionItem>

        <AccordionItem value="aircraft">
          <AccordionTrigger>
            {t("missionInput.sections.aircraft.title")}
          </AccordionTrigger>
          <AccordionContent className="space-y-2">
            <Label>{t("missionInput.fields.aircraft")}</Label>
            <Controller
              name="aircraft"
              control={form.control}
              render={({ field }) => (
                <AircraftPicker
                  catalog={RSAF_AIRCRAFT}
                  selected={field.value}
                  onChange={field.onChange}
                />
              )}
            />
            <p className="text-xs text-slate-500">
              {t("missionInput.hints.aircraft", {
                n: form.watch("aircraft").length,
              })}
            </p>
          </AccordionContent>
        </AccordionItem>

        <AccordionItem value="forces">
          <AccordionTrigger>
            {t("missionInput.sections.forces.title")}
          </AccordionTrigger>
          <AccordionContent className="space-y-4">
            <div className="space-y-2">
              <Label>{t("missionInput.fields.friendlyUnitTypes")}</Label>
              <Controller
                name="friendly_unit_types"
                control={form.control}
                render={({ field }) => (
                  <UnitTypePicker
                    selected={field.value as UnitType[]}
                    onChange={field.onChange}
                  />
                )}
              />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="enemy-threat">
                {t("missionInput.fields.enemyThreatLevel")}
              </Label>
              <Controller
                name="enemy_threat_level"
                control={form.control}
                render={({ field }) => (
                  <Select value={field.value} onValueChange={field.onChange}>
                    <SelectTrigger id="enemy-threat">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {ENEMY_THREAT_LEVELS.map((level) => (
                        <SelectItem key={level} value={level}>
                          {t(`enum.threatLevel.${level}`)}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                )}
              />
            </div>
          </AccordionContent>
        </AccordionItem>

        <AccordionItem value="generation">
          <AccordionTrigger>
            {t("missionInput.sections.generation.title")}
          </AccordionTrigger>
          <AccordionContent className="space-y-4">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label htmlFor="n-variants">
                  {t("missionInput.fields.nVariants")}
                </Label>
                <span className="font-mono text-xs text-slate-400">
                  {variantCount}
                </span>
              </div>
              <Controller
                name="n_variants"
                control={form.control}
                render={({ field }) => (
                  <Slider
                    id="n-variants"
                    min={MIN_VARIANT_COUNT}
                    max={MAX_VARIANT_COUNT}
                    step={1}
                    value={[field.value]}
                    onValueChange={(value) => field.onChange(value[0])}
                    thumbAriaLabel={t("missionInput.fields.nVariants")}
                  />
                )}
              />
              <p className="text-xs text-slate-500">
                {t("missionInput.hints.nVariants", {
                  min: MIN_VARIANT_COUNT,
                  max: MAX_VARIANT_COUNT,
                })}
              </p>
            </div>

            <div className="rounded-md border border-slate-800 bg-slate-950/40 px-3 py-2 text-xs text-slate-400">
              {t("missionInput.hints.bilingual")}
            </div>

            <div className="space-y-1.5">
              <Label htmlFor="additional-context">
                {t("missionInput.fields.additionalContext")}
              </Label>
              <Textarea
                id="additional-context"
                placeholder={t(
                  "missionInput.placeholders.additionalContext",
                )}
                {...form.register("additional_context")}
              />
            </div>
          </AccordionContent>
        </AccordionItem>
      </Accordion>

      {mutation.isError ? (
        <div className="rounded-md border border-rose-500/30 bg-rose-500/10 px-4 py-3 text-sm text-rose-300">
          {t("missionInput.error")}
        </div>
      ) : null}

      <GlassButton type="submit" disabled={mutation.isPending}>
        {mutation.isPending ? (
          <>
            <Loader2 className="size-4 animate-spin" aria-hidden />
            <span>{t("missionInput.generating")}</span>
          </>
        ) : (
          <span>{t("missionInput.submit", { n: variantCount })}</span>
        )}
      </GlassButton>
    </form>
    </>
  );
}
