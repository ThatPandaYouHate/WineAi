import { useId, useMemo, useState } from "react";

export interface CheckboxItem {
  value: string;
  label: string;
  searchText?: string;
}

interface CheckboxListProps {
  label: string;
  items: CheckboxItem[];
  selected: string[];
  onChange: (next: string[]) => void;
  searchPlaceholder?: string;
  emptyText?: string;
  loading?: boolean;
}

/**
 * Generic searchable, multi-select checkbox list used for both stores
 * and countries. Keeps the user's selection even when filtered items
 * are no longer visible.
 */
export function CheckboxList({
  label,
  items,
  selected,
  onChange,
  searchPlaceholder = "Sök...",
  emptyText = "Inga träffar",
  loading = false,
}: CheckboxListProps) {
  const [query, setQuery] = useState("");
  const inputId = useId();

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return items;
    return items.filter((item) =>
      (item.searchText ?? item.label).toLowerCase().includes(q)
    );
  }, [items, query]);

  function toggle(value: string) {
    if (selected.includes(value)) {
      onChange(selected.filter((v) => v !== value));
    } else {
      onChange([...selected, value]);
    }
  }

  return (
    <div className="space-y-2">
      <div className="flex items-baseline justify-between">
        <label htmlFor={inputId} className="filter-label">
          {label}
        </label>
        {selected.length > 0 && (
          <button
            type="button"
            onClick={() => onChange([])}
            className="text-xs text-white/70 underline hover:text-white"
          >
            Rensa ({selected.length})
          </button>
        )}
      </div>

      <input
        id={inputId}
        type="search"
        className="input"
        placeholder={searchPlaceholder}
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />

      <div
        className="max-h-44 overflow-y-auto rounded-md border border-white/20 bg-white/5"
        role="listbox"
        aria-multiselectable="true"
        aria-label={label}
      >
        {loading ? (
          <div className="p-3 text-sm text-white/70">Laddar...</div>
        ) : filtered.length === 0 ? (
          <div className="p-3 text-sm text-white/70">{emptyText}</div>
        ) : (
          filtered.map((item) => {
            const checked = selected.includes(item.value);
            return (
              <label
                key={item.value}
                className="flex cursor-pointer items-center gap-2 px-3 py-1.5 text-sm text-white hover:bg-white/10"
              >
                <input
                  type="checkbox"
                  className="accent-white"
                  checked={checked}
                  onChange={() => toggle(item.value)}
                />
                <span>{item.label}</span>
              </label>
            );
          })
        )}
      </div>
    </div>
  );
}
