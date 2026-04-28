import { useCallback, useRef, useState } from "react";
import { askForRecommendations } from "../lib/api";
import type { AskRequest, ChatMessage } from "../types";

const initialMessage: ChatMessage = {
  id: "welcome",
  role: "assistant",
  content:
    "Hej! Jag är din vinassistent. Berätta vad du lagar eller vilken typ av vin du letar efter, så ger jag förslag baserat på sortimentet i butikerna du valt.",
};

function uid(): string {
  return Math.random().toString(36).slice(2, 11);
}

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([initialMessage]);
  const [isLoading, setIsLoading] = useState(false);
  const abortRef = useRef<AbortController | null>(null);

  const stop = useCallback(() => {
    abortRef.current?.abort();
    abortRef.current = null;
  }, []);

  const send = useCallback(async (request: AskRequest) => {
    const userMessage: ChatMessage = {
      id: uid(),
      role: "user",
      content: request.prompt,
    };
    const botId = uid();
    setMessages((prev) => [
      ...prev,
      userMessage,
      { id: botId, role: "assistant", content: "", isStreaming: true },
    ]);
    setIsLoading(true);

    const controller = new AbortController();
    abortRef.current = controller;

    try {
      const result = await askForRecommendations(request, controller.signal);
      setMessages((prev) =>
        prev.map((m) =>
          m.id === botId
            ? {
                ...m,
                isStreaming: false,
                content: result.intro,
                recommendations: result.recommendations,
                notes: result.notes,
                matchedWineCount: result.matchedWineCount,
              }
            : m
        )
      );
    } catch (err) {
      if (controller.signal.aborted) {
        setMessages((prev) =>
          prev.map((m) =>
            m.id === botId
              ? { ...m, isStreaming: false, content: "_(avbruten)_" }
              : m
          )
        );
      } else {
        const message = err instanceof Error ? err.message : "Okänt fel";
        setMessages((prev) =>
          prev.map((m) =>
            m.id === botId
              ? {
                  ...m,
                  isStreaming: false,
                  isError: true,
                  content: `Något gick fel: ${message}`,
                }
              : m
          )
        );
      }
    } finally {
      setIsLoading(false);
      abortRef.current = null;
    }
  }, []);

  const addLocal = useCallback((content: string) => {
    setMessages((prev) => [
      ...prev,
      { id: uid(), role: "assistant", content, isError: true },
    ]);
  }, []);

  return { messages, send, stop, isStreaming: isLoading, addLocal };
}
