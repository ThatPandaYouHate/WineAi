import type {
  AskRequest,
  AskResponse,
  FilterOptions,
  Store,
} from "../types";

async function expectOk(response: Response): Promise<Response> {
  if (!response.ok) {
    const text = await response.text().catch(() => "");
    throw new Error(`HTTP ${response.status}: ${text || response.statusText}`);
  }
  return response;
}

async function readJson<T>(response: Response): Promise<T> {
  const contentType = response.headers.get("content-type") ?? "";
  const raw = await response.text();
  if (!contentType.includes("application/json")) {
    const preview = raw.slice(0, 200).trim();
    throw new Error(
      `Servern returnerade inte JSON (content-type: ${contentType || "saknas"}). ` +
        `Är backend uppdaterad och omstartad? Förhandsvisning: ${preview || "(tomt)"}`
    );
  }
  try {
    return JSON.parse(raw) as T;
  } catch (err) {
    const preview = raw.slice(0, 200).trim();
    throw new Error(
      `Kunde inte tolka svaret som JSON: ${err instanceof Error ? err.message : err}. ` +
        `Förhandsvisning: ${preview || "(tomt)"}`
    );
  }
}

export async function fetchStores(): Promise<Store[]> {
  const r = await fetch("/api/stores");
  await expectOk(r);
  return readJson<Store[]>(r);
}

export async function fetchCountries(storeIds?: string[]): Promise<string[]> {
  const params = new URLSearchParams();
  storeIds?.forEach((id) => params.append("storeIds", id));
  const url = "/api/countries" + (params.size ? `?${params.toString()}` : "");
  const r = await fetch(url);
  await expectOk(r);
  return readJson<string[]>(r);
}

export async function fetchFilterOptions(
  storeIds?: string[],
  wineTypes?: string[]
): Promise<FilterOptions> {
  const params = new URLSearchParams();
  storeIds?.forEach((id) => params.append("storeIds", id));
  wineTypes?.forEach((t) => params.append("wineTypes", t));
  const url =
    "/api/filter-options" + (params.size ? `?${params.toString()}` : "");
  const r = await fetch(url);
  await expectOk(r);
  return readJson<FilterOptions>(r);
}

export async function askForRecommendations(
  body: AskRequest,
  signal?: AbortSignal
): Promise<AskResponse> {
  const r = await fetch("/api/ask", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
    signal,
  });
  await expectOk(r);
  return readJson<AskResponse>(r);
}
