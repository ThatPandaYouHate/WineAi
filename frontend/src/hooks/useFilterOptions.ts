import { useEffect, useState } from "react";
import { fetchFilterOptions } from "../lib/api";
import type { FilterOptions } from "../types";

interface State {
  options: FilterOptions;
  loading: boolean;
  error: string | null;
}

const EMPTY: FilterOptions = {
  wineTypes: [],
  tasteProfiles: [],
  assortmentTypes: [],
  countries: [],
};

/**
 * Loads the distinct values used for the dropdown-style filters.
 *
 * Re-fetches whenever `storeIds` or `wineTypes` change (debounced) so
 * the available taste profiles narrow as the user picks wine types.
 */
export function useFilterOptions(
  storeIds: string[],
  wineTypes: string[]
): State {
  const [state, setState] = useState<State>({
    options: EMPTY,
    loading: true,
    error: null,
  });

  const storeKey = storeIds.join("|");
  const typeKey = wineTypes.join("|");

  useEffect(() => {
    let cancelled = false;
    setState((prev) => ({ ...prev, loading: true }));

    const handle = window.setTimeout(() => {
      fetchFilterOptions(
        storeIds.length ? storeIds : undefined,
        wineTypes.length ? wineTypes : undefined
      )
        .then((options) => {
          if (!cancelled) setState({ options, loading: false, error: null });
        })
        .catch((err: unknown) => {
          if (!cancelled) {
            const message =
              err instanceof Error ? err.message : "Unknown error";
            setState({ options: EMPTY, loading: false, error: message });
          }
        });
    }, 200);

    return () => {
      cancelled = true;
      window.clearTimeout(handle);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [storeKey, typeKey]);

  return state;
}
