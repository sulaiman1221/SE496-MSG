import { useEffect, useRef, type CSSProperties } from "react";

interface SpiralProps {
  totalDots?: number;
  dotRadius?: number;
  duration?: number;
  dotColor?: string;
  backgroundColor?: string;
  margin?: number;
  minOpacity?: number;
  maxOpacity?: number;
  minScale?: number;
  maxScale?: number;
  style?: CSSProperties;
}

const SVG_NS = "http://www.w3.org/2000/svg";
const CANVAS_SIZE = 400;
const GOLDEN_ANGLE = Math.PI * (3 - Math.sqrt(5));

export function Spiral({
  totalDots = 600,
  dotRadius = 2,
  duration = 3,
  dotColor = "#F59E0B",
  backgroundColor = "transparent",
  margin = 2,
  minOpacity = 0.3,
  maxOpacity = 1,
  minScale = 0.5,
  maxScale = 1.5,
  style,
}: SpiralProps) {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    const svg = svgRef.current;
    if (!svg) return;

    const center = CANVAS_SIZE / 2;
    const maxRadius = center - margin - dotRadius;
    svg.replaceChildren();

    for (let i = 0; i < totalDots; i++) {
      const idx = i + 0.5;
      const frac = idx / totalDots;
      const r = Math.sqrt(frac) * maxRadius;
      const theta = idx * GOLDEN_ANGLE;
      const cx = center + r * Math.cos(theta);
      const cy = center + r * Math.sin(theta);
      const begin = `${frac * duration}s`;

      const circle = document.createElementNS(SVG_NS, "circle");
      circle.setAttribute("cx", cx.toString());
      circle.setAttribute("cy", cy.toString());
      circle.setAttribute("r", dotRadius.toString());
      circle.setAttribute("fill", dotColor);
      circle.setAttribute("opacity", "0");

      const animR = document.createElementNS(SVG_NS, "animate");
      animR.setAttribute("attributeName", "r");
      animR.setAttribute(
        "values",
        `${dotRadius * minScale};${dotRadius * maxScale};${dotRadius * minScale}`,
      );
      animR.setAttribute("dur", `${duration}s`);
      animR.setAttribute("begin", begin);
      animR.setAttribute("repeatCount", "indefinite");
      animR.setAttribute("calcMode", "spline");
      animR.setAttribute("keySplines", "0.4 0 0.6 1;0.4 0 0.6 1");
      circle.appendChild(animR);

      const animO = document.createElementNS(SVG_NS, "animate");
      animO.setAttribute("attributeName", "opacity");
      animO.setAttribute(
        "values",
        `${minOpacity};${maxOpacity};${minOpacity}`,
      );
      animO.setAttribute("dur", `${duration}s`);
      animO.setAttribute("begin", begin);
      animO.setAttribute("repeatCount", "indefinite");
      animO.setAttribute("calcMode", "spline");
      animO.setAttribute("keySplines", "0.4 0 0.6 1;0.4 0 0.6 1");
      circle.appendChild(animO);

      svg.appendChild(circle);
    }
  }, [
    totalDots,
    dotRadius,
    duration,
    dotColor,
    margin,
    minOpacity,
    maxOpacity,
    minScale,
    maxScale,
  ]);

  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        backgroundColor,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        overflow: "hidden",
        ...style,
      }}
    >
      <svg
        ref={svgRef}
        width={CANVAS_SIZE}
        height={CANVAS_SIZE}
        viewBox={`0 0 ${CANVAS_SIZE} ${CANVAS_SIZE}`}
        style={{ maxWidth: "100%", maxHeight: "100%" }}
        aria-hidden
      />
    </div>
  );
}
