import { forwardRef, type ButtonHTMLAttributes } from "react";

import { GradientBorderBox } from "@/components/ui/GradientBorderBox";
import { cn } from "@/lib/utils";

export const GlassButton = forwardRef<
  HTMLButtonElement,
  ButtonHTMLAttributes<HTMLButtonElement>
>(({ className, children, disabled, ...props }, ref) => (
  <GradientBorderBox
    borderWidth={1.5}
    borderRadius={9999}
    gradientStops={[
      { color: "#FBBF24", position: 0 },
      { color: "#F59E0B", position: 50 },
      { color: "#B45309", position: 100 },
    ]}
    gradientAngle={135}
    style={disabled ? { opacity: 0.6 } : undefined}
  >
    <button
      ref={ref}
      disabled={disabled}
      className={cn(
        "glass-button-outer group relative flex w-full items-center justify-center rounded-full p-1 transition-transform duration-200 active:scale-[0.99] focus-ring disabled:cursor-not-allowed",
        className,
      )}
      {...props}
    >
      <span className="glass-button-inner flex w-full items-center justify-center gap-2 rounded-full px-6 py-3 text-sm font-semibold tracking-tight text-slate-900">
        {children}
      </span>
    </button>
  </GradientBorderBox>
));
GlassButton.displayName = "GlassButton";
