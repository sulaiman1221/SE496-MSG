import { useTranslation } from "react-i18next";
import { NavLink } from "react-router-dom";

import { cn } from "@/lib/utils";

export function Sidebar() {
  const { t } = useTranslation();

  const items = [
    { to: "/create", label: t("nav.create") },
    { to: "/history", label: t("nav.history") },
  ];

  return (
    <aside className="hidden md:flex w-64 shrink-0 flex-col border-e border-slate-800 bg-slate-900/50">
      <div className="flex h-14 items-center border-b border-slate-800 px-5">
        <div className="flex flex-col leading-tight">
          <span className="text-sm font-semibold tracking-tight">
            {t("app.title")}
          </span>
          <span className="text-[11px] text-slate-400">
            {t("app.subtitle")}
          </span>
        </div>
      </div>
      <nav className="flex flex-col gap-1 p-3">
        {items.map(({ to, label }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              cn(
                "flex items-center rounded-md px-3 py-2 text-sm transition-colors duration-150",
                isActive
                  ? "bg-slate-800 text-slate-100"
                  : "text-slate-400 hover:bg-slate-800/60 hover:text-slate-100",
              )
            }
          >
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
