import { useEffect, useRef, useState } from "react";

/**
 * useState-like hook that persists its value to localStorage.
 *
 * On first render it tries to read the existing value; on every change it
 * writes it back. SSR-safe (`window` is checked).
 */
export function usePersistedState<T>(
  key: string,
  initial: T
): [T, React.Dispatch<React.SetStateAction<T>>] {
  const [value, setValue] = useState<T>(() => {
    if (typeof window === "undefined") return initial;
    try {
      const raw = window.localStorage.getItem(key);
      return raw === null ? initial : (JSON.parse(raw) as T);
    } catch {
      return initial;
    }
  });

  const isFirst = useRef(true);
  useEffect(() => {
    if (isFirst.current) {
      isFirst.current = false;
      return;
    }
    try {
      window.localStorage.setItem(key, JSON.stringify(value));
    } catch {
      /* quota or serialisation issues are not fatal */
    }
  }, [key, value]);

  return [value, setValue];
}
