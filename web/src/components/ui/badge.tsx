import { forwardRef, type HTMLAttributes } from "react";

import { cn } from "@/lib/utils";

export interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {}

export const Badge = forwardRef<HTMLSpanElement, BadgeProps>(
  ({ className, ...props }, ref) => (
    <span
      ref={ref}
      className={cn(
        "inline-flex items-center rounded border border-slate-700 px-2 py-0.5 text-[11px] font-medium uppercase tracking-wide text-slate-400",
        className,
      )}
      {...props}
    />
  ),
);
Badge.displayName = "Badge";
