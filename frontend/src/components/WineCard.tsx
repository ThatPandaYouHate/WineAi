import type { Recommendation } from "../types";

interface WineCardProps {
  recommendation: Recommendation;
  index: number;
}

function formatPrice(price?: number | null): string {
  if (price === null || price === undefined) return "—";
  return `${Number.isInteger(price) ? price : price.toFixed(2)} kr`;
}

function formatVolume(volume?: number | null): string {
  if (volume === null || volume === undefined) return "—";
  if (volume >= 1000) return `${(volume / 1000).toLocaleString("sv-SE")} l`;
  return `${volume} ml`;
}

function formatAlcohol(alcohol?: number | null): string {
  if (alcohol === null || alcohol === undefined) return "—";
  return `${alcohol.toString().replace(".", ",")} %`;
}

function combineName(
  bold?: string | null,
  thin?: string | null
): string {
  return [bold, thin].filter(Boolean).join(" ").trim() || "Okänt vin";
}

export function WineCard({ recommendation, index }: WineCardProps) {
  const { wine, motivation, systembolagetUrl } = recommendation;
  const fullName = combineName(wine.productNameBold, wine.productNameThin);

  const subtitleParts = [
    wine.country,
    wine.originLevel1,
    wine.vintage ? `Årgång ${wine.vintage}` : null,
  ].filter(Boolean) as string[];

  const tags = [
    wine.categoryLevel2,
    wine.categoryLevel3,
    wine.assortmentText,
  ].filter(Boolean) as string[];

  return (
    <article className="overflow-hidden rounded-xl border border-neutral-200 bg-white shadow-sm transition hover:shadow-md">
      <header className="flex items-start gap-3 border-b border-neutral-100 bg-gradient-to-br from-wine/5 to-transparent px-4 py-3">
        <span
          aria-hidden="true"
          className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-wine text-sm font-bold text-white"
        >
          {index + 1}
        </span>
        <div className="min-w-0 flex-1">
          <h3 className="truncate text-base font-semibold text-wine-dark">
            {fullName}
          </h3>
          {subtitleParts.length > 0 ? (
            <p className="truncate text-xs text-neutral-600">
              {subtitleParts.join(" · ")}
            </p>
          ) : null}
        </div>
        {wine.price != null ? (
          <div className="shrink-0 text-right">
            <div className="text-base font-semibold text-wine-dark">
              {formatPrice(wine.price)}
            </div>
            <div className="text-[11px] uppercase tracking-wide text-neutral-500">
              {formatVolume(wine.volume)}
            </div>
          </div>
        ) : null}
      </header>

      {tags.length > 0 ? (
        <div className="flex flex-wrap gap-1.5 px-4 pt-3">
          {tags.map((tag) => (
            <span
              key={tag}
              className="rounded-full bg-neutral-100 px-2 py-0.5 text-xs text-neutral-700"
            >
              {tag}
            </span>
          ))}
        </div>
      ) : null}

      {motivation ? (
        <p className="px-4 pt-3 text-sm leading-relaxed text-neutral-800">
          {motivation}
        </p>
      ) : null}

      <dl className="grid grid-cols-3 gap-2 px-4 py-3 text-xs text-neutral-600">
        <div>
          <dt className="text-[10px] uppercase tracking-wide text-neutral-500">
            Alkohol
          </dt>
          <dd className="font-medium text-neutral-800">
            {formatAlcohol(wine.alcoholPercentage)}
          </dd>
        </div>
        <div>
          <dt className="text-[10px] uppercase tracking-wide text-neutral-500">
            Volym
          </dt>
          <dd className="font-medium text-neutral-800">
            {formatVolume(wine.volume)}
          </dd>
        </div>
        <div>
          <dt className="text-[10px] uppercase tracking-wide text-neutral-500">
            Pris
          </dt>
          <dd className="font-medium text-neutral-800">
            {formatPrice(wine.price)}
          </dd>
        </div>
      </dl>

      <footer className="flex items-center justify-between gap-2 border-t border-neutral-100 bg-neutral-50 px-4 py-2 text-xs">
        <span className="font-mono text-neutral-600">
          Art.nr <span className="font-semibold text-neutral-800">{wine.productNumber}</span>
        </span>
        <a
          href={systembolagetUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="font-medium text-wine hover:text-wine-dark hover:underline"
        >
          Visa på Systembolaget →
        </a>
      </footer>
    </article>
  );
}
