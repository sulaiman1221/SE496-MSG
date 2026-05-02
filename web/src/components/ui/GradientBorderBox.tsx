import { useMemo, type CSSProperties, type ReactNode } from "react";

export interface GradientStop {
  color: string;
  position: number;
}

interface GradientBorderBoxProps {
  children: ReactNode;
  borderWidth?: number;
  borderRadius?: number;
  gradientStops?: readonly GradientStop[];
  gradientAngle?: number;
  background?: string;
  className?: string;
  style?: CSSProperties;
}

const DEFAULT_STOPS: readonly GradientStop[] = [
  { color: "#3B82F6", position: 0 },
  { color: "#F59E0B", position: 50 },
  { color: "#1E40AF", position: 100 },
];

export function GradientBorderBox({
  children,
  borderWidth = 1,
  borderRadius = 9999,
  gradientStops = DEFAULT_STOPS,
  gradientAngle = 135,
  background = "transparent",
  className,
  style,
}: GradientBorderBoxProps) {
  const gradient = useMemo(() => {
    const sorted = [...gradientStops].sort((a, b) => a.position - b.position);
    const segments = sorted.map((s) => `${s.color} ${s.position}%`);
    return `linear-gradient(${gradientAngle}deg, ${segments.join(", ")})`;
  }, [gradientStops, gradientAngle]);

  return (
    <div
      className={className}
      style={{
        position: "relative",
        background: gradient,
        borderRadius,
        padding: borderWidth,
        boxSizing: "border-box",
        ...style,
      }}
    >
      <div
        style={{
          width: "100%",
          height: "100%",
          background,
          borderRadius: Math.max(0, borderRadius - borderWidth),
          overflow: "hidden",
        }}
      >
        {children}
      </div>
    </div>
  );
}
