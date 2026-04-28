import { useId } from "react";
import type { Range } from "../types";

interface RangeSliderProps {
  label: string;
  unit?: string;
  min: number;
  max: number;
  step?: number;
  value: Range;
  onChange: (next: Range) => void;
}

/**
 * Dual-thumb range slider used for both price and volume filters.
 *
 * Renders two native range inputs stacked on top of each other so the
 * component stays accessible while still letting us draw a custom
 * filled track between the two thumbs.
 */
export function RangeSlider({
  label,
  unit,
  min,
  max,
  step = 1,
  value,
  onChange,
}: RangeSliderProps) {
  const minId = useId();
  const maxId = useId();

  const span = max - min || 1;
  const leftPct = ((value.min - min) / span) * 100;
  const rightPct = ((value.max - min) / span) * 100;

  function setMin(next: number) {
    const clamped = Math.min(Math.max(next, min), value.max);
    onChange({ min: clamped, max: value.max });
  }

  function setMax(next: number) {
    const clamped = Math.max(Math.min(next, max), value.min);
    onChange({ min: value.min, max: clamped });
  }

  return (
    <div className="space-y-2">
      <div className="filter-label">{label}</div>

      <div className="relative h-8">
        <div className="absolute top-1/2 left-0 right-0 h-1 -translate-y-1/2 rounded bg-white/20" />
        <div
          className="absolute top-1/2 h-1 -translate-y-1/2 rounded bg-white/70"
          style={{ left: `${leftPct}%`, right: `${100 - rightPct}%` }}
        />
        <input
          id={minId}
          type="range"
          aria-label={`${label} min`}
          className="range-thumb absolute inset-0 w-full appearance-none bg-transparent"
          min={min}
          max={max}
          step={step}
          value={value.min}
          onChange={(e) => setMin(Number(e.target.value))}
        />
        <input
          id={maxId}
          type="range"
          aria-label={`${label} max`}
          className="range-thumb absolute inset-0 w-full appearance-none bg-transparent"
          min={min}
          max={max}
          step={step}
          value={value.max}
          onChange={(e) => setMax(Number(e.target.value))}
        />
      </div>

      <div className="flex items-center gap-2 text-white">
        <input
          type="number"
          aria-label={`${label} min input`}
          className="input w-24"
          min={min}
          max={max}
          step={step}
          value={value.min}
          onChange={(e) => setMin(Number(e.target.value) || min)}
        />
        <span className="opacity-60">–</span>
        <input
          type="number"
          aria-label={`${label} max input`}
          className="input w-24"
          min={min}
          max={max}
          step={step}
          value={value.max}
          onChange={(e) => setMax(Number(e.target.value) || max)}
        />
        {unit ? <span className="text-sm opacity-70">{unit}</span> : null}
      </div>

      <style>{`
        .range-thumb {
          pointer-events: none;
          z-index: 2;
        }
        .range-thumb::-webkit-slider-thumb {
          pointer-events: auto;
          appearance: none;
          height: 1.1rem;
          width: 1.1rem;
          border-radius: 9999px;
          background: white;
          border: 2px solid #722f37;
          cursor: pointer;
        }
        .range-thumb::-moz-range-thumb {
          pointer-events: auto;
          height: 1.1rem;
          width: 1.1rem;
          border-radius: 9999px;
          background: white;
          border: 2px solid #722f37;
          cursor: pointer;
        }
        .range-thumb::-webkit-slider-runnable-track,
        .range-thumb::-moz-range-track {
          background: transparent;
        }
      `}</style>
    </div>
  );
}
