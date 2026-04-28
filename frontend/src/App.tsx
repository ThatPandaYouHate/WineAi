import { ChatPanel } from "./components/ChatPanel";
import { Sidebar } from "./components/Sidebar";
import { useChat } from "./hooks/useChat";
import { useFilterOptions } from "./hooks/useFilterOptions";
import { usePersistedState } from "./hooks/usePersistedState";
import { useStores } from "./hooks/useStores";
import type { Range } from "./types";

const DEFAULT_PRICE: Range = { min: 0, max: 5000 };
const DEFAULT_VOLUME: Range = { min: 0, max: 1500 };
const DEFAULT_ALCOHOL: Range = { min: 0, max: 20 };

export default function App() {
  const stores = useStores();

  const [selectedStores, setSelectedStores] = usePersistedState<string[]>(
    "wine-ai/selectedStores",
    []
  );
  const [selectedCountries, setSelectedCountries] = usePersistedState<string[]>(
    "wine-ai/selectedCountries",
    []
  );
  const [selectedWineTypes, setSelectedWineTypes] = usePersistedState<string[]>(
    "wine-ai/selectedWineTypes",
    []
  );
  const [selectedTasteProfiles, setSelectedTasteProfiles] = usePersistedState<
    string[]
  >("wine-ai/selectedTasteProfiles", []);
  const [selectedAssortmentTypes, setSelectedAssortmentTypes] =
    usePersistedState<string[]>("wine-ai/selectedAssortmentTypes", []);
  const [priceRange, setPriceRange] = usePersistedState<Range>(
    "wine-ai/priceRange",
    DEFAULT_PRICE
  );
  const [volumeRange, setVolumeRange] = usePersistedState<Range>(
    "wine-ai/volumeRange",
    DEFAULT_VOLUME
  );
  const [alcoholRange, setAlcoholRange] = usePersistedState<Range>(
    "wine-ai/alcoholRange",
    DEFAULT_ALCOHOL
  );
  const [inStockOnly, setInStockOnly] = usePersistedState<boolean>(
    "wine-ai/inStockOnly",
    true
  );

  const filterOptions = useFilterOptions(selectedStores, selectedWineTypes);

  const chat = useChat();

  const noStoresSelected = selectedStores.length === 0;

  function handleSend(prompt: string) {
    if (noStoresSelected) {
      chat.addLocal("Välj minst en butik i sidomenyn först.");
      return;
    }
    void chat.send({
      prompt,
      storeIds: selectedStores,
      countries: selectedCountries,
      wineTypes: selectedWineTypes,
      tasteProfiles: selectedTasteProfiles,
      assortmentTypes: selectedAssortmentTypes,
      priceRange,
      volumeRange,
      alcoholRange,
      inStockOnly,
    });
  }

  function handleResetAll() {
    setSelectedCountries([]);
    setSelectedWineTypes([]);
    setSelectedTasteProfiles([]);
    setSelectedAssortmentTypes([]);
    setPriceRange(DEFAULT_PRICE);
    setVolumeRange(DEFAULT_VOLUME);
    setAlcoholRange(DEFAULT_ALCOHOL);
    setInStockOnly(true);
  }

  const filterChips: string[] = [];
  if (selectedStores.length)
    filterChips.push(
      `${selectedStores.length} butik${selectedStores.length === 1 ? "" : "er"}`
    );
  if (selectedWineTypes.length)
    filterChips.push(`${selectedWineTypes.length} vintyp`);
  if (selectedCountries.length)
    filterChips.push(`${selectedCountries.length} land`);
  if (selectedTasteProfiles.length)
    filterChips.push(`${selectedTasteProfiles.length} smakprofil`);
  if (selectedAssortmentTypes.length)
    filterChips.push(`${selectedAssortmentTypes.length} sortiment`);
  if (inStockOnly) filterChips.push("endast i lager");

  return (
    <div className="flex h-full flex-col md:flex-row">
      <Sidebar
        stores={stores.stores}
        storesLoading={stores.loading}
        storesError={stores.error}
        selectedStores={selectedStores}
        onSelectedStoresChange={setSelectedStores}
        filterOptions={filterOptions.options}
        filterOptionsLoading={filterOptions.loading}
        selectedCountries={selectedCountries}
        onSelectedCountriesChange={setSelectedCountries}
        selectedWineTypes={selectedWineTypes}
        onSelectedWineTypesChange={(next) => {
          setSelectedWineTypes(next);
          // Reset taste profiles when wine types change so we don't keep
          // profiles that no longer apply.
          setSelectedTasteProfiles([]);
        }}
        selectedTasteProfiles={selectedTasteProfiles}
        onSelectedTasteProfilesChange={setSelectedTasteProfiles}
        selectedAssortmentTypes={selectedAssortmentTypes}
        onSelectedAssortmentTypesChange={setSelectedAssortmentTypes}
        priceRange={priceRange}
        onPriceRangeChange={setPriceRange}
        volumeRange={volumeRange}
        onVolumeRangeChange={setVolumeRange}
        alcoholRange={alcoholRange}
        onAlcoholRangeChange={setAlcoholRange}
        inStockOnly={inStockOnly}
        onInStockOnlyChange={setInStockOnly}
        onResetAll={handleResetAll}
      />

      <div className="flex min-h-0 flex-1 flex-col">
        <header className="flex items-center gap-3 border-b bg-white p-3">
          <div className="flex-1">
            <h1 className="text-lg font-semibold text-wine-dark">Wine AI</h1>
            <p className="text-xs text-neutral-500">
              {filterChips.length === 0
                ? "Inga filter aktiva"
                : filterChips.join(" · ")}
            </p>
          </div>
        </header>

        <main className="min-h-0 flex-1">
          <ChatPanel
            messages={chat.messages}
            isStreaming={chat.isStreaming}
            onSend={handleSend}
            onStop={chat.stop}
            disabled={false}
            disabledReason={
              noStoresSelected
                ? "Välj minst en butik i sidomenyn för att få förslag."
                : undefined
            }
          />
        </main>
      </div>
    </div>
  );
}
