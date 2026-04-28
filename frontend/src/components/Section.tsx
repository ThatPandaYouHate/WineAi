import type { ReactNode } from "react";

interface SectionProps {
  title: string;
  children: ReactNode;
  defaultOpen?: boolean;
  badge?: string | number;
}

/**
 * Collapsible filter section. Uses the native `<details>` element so it
 * remains accessible and keyboard-friendly without extra JS.
 */
export function Section({
  title,
  children,
  defaultOpen = false,
  badge,
}: SectionProps) {
  return (
    <details
      open={defaultOpen}
      className="group rounded-md border border-white/10 bg-white/5 open:bg-white/10"
    >
      <summary className="flex cursor-pointer list-none items-center justify-between px-3 py-2 text-sm font-semibold uppercase tracking-wide text-white">
        <span className="flex items-center gap-2">
          <span
            aria-hidden="true"
            className="text-white/60 transition-transform group-open:rotate-90"
          >
            ▶
          </span>
          {title}
          {badge !== undefined && badge !== "" && badge !== 0 ? (
            <span className="rounded-full bg-white/20 px-2 py-0.5 text-xs font-medium text-white">
              {badge}
            </span>
          ) : null}
        </span>
      </summary>
      <div className="space-y-3 px-3 pb-3 pt-1">{children}</div>
    </details>
  );
}
