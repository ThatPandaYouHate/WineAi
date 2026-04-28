import { useId } from "react";

interface ToggleProps {
  label: string;
  description?: string;
  checked: boolean;
  onChange: (next: boolean) => void;
}

export function Toggle({ label, description, checked, onChange }: ToggleProps) {
  const id = useId();
  return (
    <label
      htmlFor={id}
      className="flex cursor-pointer items-start gap-3 text-white"
    >
      <span className="relative mt-0.5 inline-flex h-5 w-9 shrink-0 items-center">
        <input
          id={id}
          type="checkbox"
          className="peer sr-only"
          checked={checked}
          onChange={(e) => onChange(e.target.checked)}
        />
        <span
          className="absolute inset-0 rounded-full bg-white/20 transition peer-checked:bg-white/80 peer-focus-visible:ring-2 peer-focus-visible:ring-white"
          aria-hidden="true"
        />
        <span
          className="absolute left-0.5 h-4 w-4 rounded-full bg-white shadow transition-transform peer-checked:translate-x-4"
          aria-hidden="true"
        />
      </span>
      <span className="flex-1">
        <span className="block text-sm font-medium">{label}</span>
        {description ? (
          <span className="block text-xs text-white/70">{description}</span>
        ) : null}
      </span>
    </label>
  );
}
