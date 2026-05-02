import { useTranslation } from "react-i18next";

import { FloatingAnimation } from "@/components/ui/FloatingAnimation";
import { Spiral } from "@/components/ui/Spiral";

interface Props {
  title: string;
  subtitle?: string;
}

export function LoadingOverlay({ title, subtitle }: Props) {
  const { t } = useTranslation();
  return (
    <div
      role="status"
      aria-live="polite"
      aria-label={title}
      className="fixed inset-0 z-50 flex flex-col items-center justify-center gap-6 bg-slate-950"
    >
      <div className="pointer-events-none absolute inset-0 opacity-60">
        <FloatingAnimation
          colorStops={["#1E3A8A", "#F59E0B", "#0F172A"]}
          amplitude={1.1}
          blend={0.6}
          speed={0.6}
        />
      </div>
      <div className="relative z-10 size-72 md:size-96">
        <Spiral dotColor="#F8FAFC" />
      </div>
      <div className="relative z-10 flex flex-col items-center gap-1 text-center">
        <p className="text-lg font-semibold tracking-tight text-slate-100">
          {title}
        </p>
        <p className="text-sm text-slate-300">
          {subtitle ?? t("common.loading")}
        </p>
      </div>
    </div>
  );
}
