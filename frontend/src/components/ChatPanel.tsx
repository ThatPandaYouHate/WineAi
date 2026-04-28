import { useEffect, useRef, useState } from "react";
import { MessageBubble } from "./MessageBubble";
import type { ChatMessage } from "../types";

interface ChatPanelProps {
  messages: ChatMessage[];
  isStreaming: boolean;
  onSend: (message: string) => void;
  onStop: () => void;
  disabled?: boolean;
  disabledReason?: string;
}

export function ChatPanel({
  messages,
  isStreaming,
  onSend,
  onStop,
  disabled,
  disabledReason,
}: ChatPanelProps) {
  const [draft, setDraft] = useState("");
  const scrollRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({
      top: scrollRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, [messages]);

  function submit(e?: React.FormEvent) {
    e?.preventDefault();
    const text = draft.trim();
    if (!text || isStreaming || disabled) return;
    onSend(text);
    setDraft("");
    inputRef.current?.focus();
  }

  return (
    <div className="flex h-full flex-col">
      <div ref={scrollRef} className="flex-1 space-y-4 overflow-y-auto px-4 py-6">
        {messages.map((m) => (
          <MessageBubble key={m.id} message={m} />
        ))}
      </div>

      <form
        onSubmit={submit}
        className="border-t bg-white p-3 shadow-[0_-1px_3px_rgba(0,0,0,0.04)]"
      >
        {disabled && disabledReason ? (
          <p className="mb-2 text-sm text-amber-700" role="alert">
            {disabledReason}
          </p>
        ) : null}

        <div className="flex items-center gap-2">
          <input
            ref={inputRef}
            type="text"
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            placeholder="Vad lagar du? T.ex. 'kvällsmys med pizza' eller 'pasta carbonara'"
            className="flex-1 rounded-full border border-neutral-300 bg-white px-4 py-2 outline-none focus:border-wine focus:ring-2 focus:ring-wine/30"
            disabled={isStreaming || disabled}
          />
          {isStreaming ? (
            <button
              type="button"
              onClick={onStop}
              className="btn-primary !bg-neutral-700 hover:!bg-neutral-800"
            >
              Stoppa
            </button>
          ) : (
            <button
              type="submit"
              className="btn-primary"
              disabled={!draft.trim() || disabled}
            >
              Skicka
            </button>
          )}
        </div>
      </form>
    </div>
  );
}
