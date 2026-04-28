import ReactMarkdown from "react-markdown";
import { WineCard } from "./WineCard";
import type { ChatMessage } from "../types";

interface MessageBubbleProps {
  message: ChatMessage;
}

function ThinkingDots() {
  return (
    <span className="inline-flex items-center gap-1" aria-label="Tänker">
      <span className="h-2 w-2 animate-bounce rounded-full bg-wine [animation-delay:-0.3s]" />
      <span className="h-2 w-2 animate-bounce rounded-full bg-wine [animation-delay:-0.15s]" />
      <span className="h-2 w-2 animate-bounce rounded-full bg-wine" />
    </span>
  );
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";

  if (isUser) {
    return (
      <div className="flex w-full justify-end">
        <div className="max-w-[85%] whitespace-pre-wrap rounded-2xl rounded-br-sm bg-wine px-4 py-3 text-white shadow-sm">
          {message.content}
        </div>
      </div>
    );
  }

  const recommendations = message.recommendations ?? [];
  const hasContent =
    !!message.content || recommendations.length > 0 || (message.notes?.length ?? 0) > 0;

  if (message.isStreaming && !hasContent) {
    return (
      <div className="flex w-full justify-start">
        <div className="rounded-2xl rounded-bl-sm bg-neutral-100 px-4 py-3 shadow-sm">
          <ThinkingDots />
        </div>
      </div>
    );
  }

  if (message.isError) {
    return (
      <div className="flex w-full justify-start">
        <div className="max-w-[85%] rounded-2xl rounded-bl-sm bg-red-100 px-4 py-3 text-red-900 shadow-sm">
          {message.content}
        </div>
      </div>
    );
  }

  return (
    <div className="flex w-full max-w-[95%] flex-col gap-3" role="status">
      {message.content ? (
        <div className="prose-bubble max-w-[85%] rounded-2xl rounded-bl-sm bg-neutral-100 px-4 py-3 text-neutral-900 shadow-sm">
          <ReactMarkdown>{message.content}</ReactMarkdown>
        </div>
      ) : null}

      {recommendations.length > 0 ? (
        <div className="grid gap-3">
          {recommendations.map((rec, idx) => (
            <WineCard
              key={rec.wine.productNumber}
              recommendation={rec}
              index={idx}
            />
          ))}
        </div>
      ) : null}

      {message.matchedWineCount !== undefined && message.matchedWineCount > 0 ? (
        <div className="text-xs text-neutral-500">
          {message.matchedWineCount.toLocaleString("sv-SE")} viner matchade
          dina filter.
        </div>
      ) : null}

      {message.notes && message.notes.length > 0 ? (
        <details className="rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-amber-900">
          <summary className="cursor-pointer font-medium">
            Anmärkningar ({message.notes.length})
          </summary>
          <ul className="mt-1 list-disc space-y-1 pl-5">
            {message.notes.map((note, i) => (
              <li key={i}>{note}</li>
            ))}
          </ul>
        </details>
      ) : null}
    </div>
  );
}
