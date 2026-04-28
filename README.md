# Wine AI

En lokal vinrekommendationsapp som kombinerar **Systembolagets sortimentdata** med en **lokal LLM via Ollama** för att föreslå viner som passar till maten du lagar — filtrerat på de butiker du har nära dig.

```mermaid
flowchart LR
    User[Browser] -->|POST /api/ask| FastAPI
    FastAPI -->|filter| Cache[(In-memory<br/>assortment)]
    FastAPI -->|stream prompt| Ollama
    Ollama -->|tokens| FastAPI
    FastAPI -->|StreamingResponse| User
    JSON[assortments/*.json] -.->|lazy load| Cache
```

## Innehåll

- `backend/` — FastAPI-backend (Python 3.11+)
- `frontend/` — React + TypeScript + Tailwind (Vite)
- `assortments/` — JSON-export av Systembolagets sortiment per butik
  **(~1.5 GB — inte committad, se `assortments/README.md` för hur du fyller den)**
- `scripts/` — datauppdateringsverktyg (`update_data.py`)
- `legacy/` — original-prototypen (Flask + en stor `index.html`)

## Komma igång

### Förutsättningar

- Python 3.11 eller senare
- Node.js 18+ och npm (för frontend)
- [Ollama](https://ollama.ai) installerat och körande lokalt
- En modell hämtad i Ollama, t.ex.:
  ```sh
  ollama pull mistral
  ```

### 1. Backend

```sh
cd backend
python -m venv .venv
.\.venv\Scripts\activate          # PowerShell
# eller: source .venv/bin/activate  # macOS/Linux

pip install -r requirements.txt

copy .env.example .env             # Windows
# eller: cp .env.example .env

uvicorn app.main:app --reload --port 5000
```

Backend lyssnar nu på `http://localhost:5000`. Hälsokoll: <http://localhost:5000/api/health>.

Kör testerna med:

```sh
python -m pytest
```

### 2. Frontend

```sh
cd frontend
npm install
npm run dev
```

Frontend startar på <http://localhost:5173> och proxar `/api/*` till backend automatiskt.

### 3. Använd appen

1. Öppna sidan i webbläsaren.
2. Klicka på menyknappen och välj minst en butik.
3. Justera filter (länder, pris, volym) om du vill.
4. Skriv vad du lagar — t.ex. *"pizza med skinka och svamp"* — och tryck **Skicka**.
5. Svaret strömmas in tecken för tecken från din lokala LLM.

## Konfiguration

Alla inställningar läses från `backend/.env` (eller miljövariabler):

| Variabel           | Default                  | Beskrivning                                                |
| ------------------ | ------------------------ | ---------------------------------------------------------- |
| `OLLAMA_URL`       | `http://localhost:11434` | Var Ollama lyssnar                                         |
| `OLLAMA_MODEL`     | `mistral`                | Modellnamn                                                 |
| `ASSORTMENTS_DIR`  | `../assortments`         | Mapp med sortiments-JSON                                   |
| `MAX_WINES_TO_LLM` | `80`                     | Maxantal viner som skickas i prompten                      |
| `CORS_ORIGINS`     | `http://localhost:5173`  | Tillåtna frontend-origins (kommaseparerade)                |
| `LOG_LEVEL`        | `INFO`                   | `DEBUG`, `INFO`, `WARNING`, `ERROR`                        |
| `HOST` / `PORT`    | `0.0.0.0` / `5000`       | Bind-adress (om du kör `python -m app.main` direkt)        |

## API

| Metod | Path             | Beskrivning                                       |
| ----- | ---------------- | ------------------------------------------------- |
| GET   | `/api/health`    | Hälsokoll                                         |
| GET   | `/api/stores`    | Alla icke-agent-butiker                           |
| GET   | `/api/countries` | Distinkta länder (filtrera via `?storeIds=...`)   |
| POST  | `/api/ask`       | **Streamar** ett vinförslag (text/plain)          |

`POST /api/ask` body:

```json
{
  "prompt": "pasta bolognese",
  "storeIds": ["0106"],
  "countries": ["Italien"],
  "priceRange": { "min": 0, "max": 500 },
  "volumeRange": { "min": 0, "max": 1500 }
}
```

Svaret returneras som strömmad UTF-8-text (`text/plain; charset=utf-8`), markdown-formaterad.

## Uppdatera sortimentsdatan

`scripts/update_data.py` anropar en remote Systembolags-API-binär över SSH och skriver om `assortments/*.json`. Det kräver att du har den miljön uppsatt — för de flesta räcker det att använda redan committad data.

## Vad har förbättrats jämfört med originalet (`legacy/`)

- **Backend**:
  - FastAPI + Pydantic istället för Flask + handrullad validering
  - Async streaming från Ollama → svar visas tecken för tecken i UI
  - In-memory cache + O(1) deduplicering (gamla koden var O(n²))
  - Strukturerad logging, miljö-config, riktig felhantering
  - 11 enhetstester
- **Frontend**:
  - React + TypeScript + Tailwind, uppdelat i komponenter och hooks
  - Markdown-rendering av AI-svaren
  - localStorage-persistens av filterval
  - Dynamisk landlista från sortimentet (inte hårdkodad)
  - Tillgängliga ARIA-labels, fokus-stilar, ESC-tangent stänger sidomenyn
  - Mobilvänlig responsiv layout
- **Övrigt**:
  - Top-level-koden i `callAPIinC.py` (som körde varje gång modulen importerades) är borta
  - Stavfel som `promtAI`/`awnser` rättade
  - Död kod (`store-selector.js`) borttagen
