import { Languages } from "lucide-react";
import { useTranslation } from "react-i18next";

import { Button } from "@/components/ui/button";

export function TopBar() {
  const { i18n, t } = useTranslation();
  const nextLang = i18n.language.startsWith("ar") ? "en" : "ar";
  const label =
    nextLang === "ar" ? t("common.arabic") : t("common.english");

  return (
    <header className="flex h-14 items-center justify-end gap-3 border-b border-slate-800 bg-slate-900/30 px-5">
      <Button
        variant="ghost"
        size="sm"
        onClick={() => i18n.changeLanguage(nextLang)}
        aria-label={t("common.language")}
      >
        <Languages className="size-4" aria-hidden />
        <span className="text-xs font-medium tracking-wide">{label}</span>
      </Button>
    </header>
  );
}
