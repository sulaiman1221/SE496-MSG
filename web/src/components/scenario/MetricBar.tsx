import type { EvaluationMetric } from "@/lib/types";

export function MetricBar({ metric }: { metric: EvaluationMetric }) {
  const pct = Math.min(100, Math.max(0, Math.round(metric.weight * 100)));
  return (
    <div className="grid grid-cols-[1fr_auto] items-center gap-x-4 gap-y-1">
      <span className="text-sm font-medium text-slate-200">{metric.name}</span>
      <span className="text-xs font-mono text-slate-400">{pct}%</span>
      <p className="col-span-2 text-sm text-slate-400">{metric.target}</p>
      <div
        className="col-span-2 h-1.5 w-full overflow-hidden rounded-full bg-slate-800"
        role="progressbar"
        aria-valuenow={pct}
        aria-valuemin={0}
        aria-valuemax={100}
      >
        <div
          className="h-full rounded-full bg-brand"
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}
