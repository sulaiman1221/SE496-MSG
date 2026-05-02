import { type CSSProperties } from "react";

const BASE_DURATION_S = 60;

const clamp = (n: number, min: number, max: number) =>
  Math.min(max, Math.max(min, n));

interface AuraNightSkyProps {
  backgroundColor?: string;
  stripesColor?: string;
  rainbowColors?: readonly [string, string, string, string, string];
  speed?: number;
  stripeWidth?: number;
  fadeEdges?: boolean;
  fadeStrength?: number;
  className?: string;
  style?: CSSProperties;
}

const DEFAULT_RAINBOW: readonly [string, string, string, string, string] = [
  "#60a5fa",
  "#e879f9",
  "#60a5fa",
  "#5eead4",
  "#60a5fa",
];

export function AuraNightSky({
  backgroundColor = "transparent",
  stripesColor = "#ffffff",
  rainbowColors = DEFAULT_RAINBOW,
  speed = 1,
  stripeWidth = 7,
  fadeEdges = true,
  fadeStrength = 50,
  className,
  style,
}: AuraNightSkyProps) {
  const inner = clamp(40 - (fadeStrength - 50) * 0.2, 25, 55);
  const outer = clamp(70 + (fadeStrength - 50) * 0.3, 55, 90);
  const duration = Math.max(1, BASE_DURATION_S / Math.max(0.1, speed));

  const mask = fadeEdges
    ? `radial-gradient(ellipse at 100% 0%, black ${inner}%, transparent ${outer}%)`
    : undefined;

  const auroraStyle: CSSProperties = {
    position: "absolute",
    inset: -10,
    opacity: 0.5,
    filter: "blur(10px) opacity(50%) saturate(200%)",
    maskImage: mask,
    WebkitMaskImage: mask,
    pointerEvents: "none",
    backgroundImage: `repeating-linear-gradient(
        100deg,
        ${stripesColor} 0%,
        ${stripesColor} ${stripeWidth}%,
        transparent ${stripeWidth + 3}%,
        transparent ${stripeWidth + 5}%,
        ${stripesColor} ${stripeWidth + 9}%
      ), repeating-linear-gradient(
        100deg,
        ${rainbowColors[0]} 10%,
        ${rainbowColors[1]} 15%,
        ${rainbowColors[2]} 20%,
        ${rainbowColors[3]} 25%,
        ${rainbowColors[4]} 30%
      )`,
    backgroundSize: "300%, 200%",
    backgroundPosition: "50% 50%, 50% 50%",
    animation: `aura-drift ${duration}s linear infinite`,
  };

  return (
    <div
      aria-hidden
      className={className}
      style={{
        position: "relative",
        width: "100%",
        height: "100%",
        backgroundColor,
        overflow: "hidden",
        ...style,
      }}
    >
      <div style={auroraStyle} />
    </div>
  );
}
