import { useEffect, useState } from "react";
import { fetchStores } from "../lib/api";
import type { Store } from "../types";

interface State {
  stores: Store[];
  loading: boolean;
  error: string | null;
}

export function useStores(): State {
  const [state, setState] = useState<State>({
    stores: [],
    loading: true,
    error: null,
  });

  useEffect(() => {
    let cancelled = false;
    fetchStores()
      .then((stores) => {
        if (!cancelled) setState({ stores, loading: false, error: null });
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          const message = err instanceof Error ? err.message : "Unknown error";
          setState({ stores: [], loading: false, error: message });
        }
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return state;
}
