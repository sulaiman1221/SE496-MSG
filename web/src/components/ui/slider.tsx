import * as SliderPrimitive from "@radix-ui/react-slider";
import {
  forwardRef,
  type ComponentPropsWithoutRef,
  type ElementRef,
} from "react";

import { cn } from "@/lib/utils";

type SliderProps = ComponentPropsWithoutRef<typeof SliderPrimitive.Root> & {
  thumbAriaLabel?: string;
};

export const Slider = forwardRef<
  ElementRef<typeof SliderPrimitive.Root>,
  SliderProps
>(({ className, thumbAriaLabel, ...props }, ref) => (
  <SliderPrimitive.Root
    ref={ref}
    className={cn(
      "relative flex w-full touch-none select-none items-center",
      className,
    )}
    {...props}
  >
    <SliderPrimitive.Track className="relative h-1.5 w-full grow overflow-hidden rounded-full bg-slate-800">
      <SliderPrimitive.Range className="absolute h-full bg-accent" />
    </SliderPrimitive.Track>
    <SliderPrimitive.Thumb
      className="block size-4 rounded-full border-2 border-accent bg-slate-100 shadow-sm transition-colors focus-ring disabled:pointer-events-none disabled:opacity-50"
      aria-label={thumbAriaLabel}
    />
  </SliderPrimitive.Root>
));
Slider.displayName = "Slider";
