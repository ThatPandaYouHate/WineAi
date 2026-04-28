import { useMemo } from "react";
import { CheckboxList, type CheckboxItem } from "./CheckboxList";
import { RangeSlider } from "./RangeSlider";
import { Section } from "./Section";
import { Toggle } from "./Toggle";
import type { FilterOptions, Range, Store } from "../types";

interface SidebarProps {
  stores: Store[];
  storesLoading: boolean;
  storesError: string | null;
  selectedStores: string[];
  onSelectedStoresChange: (next: string[]) => void;

  filterOptions: FilterOptions;
  filterOptionsLoading: boolean;

  selectedCountries: string[];
  onSelectedCountriesChange: (next: string[]) => void;

  selectedWineTypes: string[];
  onSelectedWineTypesChange: (next: string[]) => void;

  selectedTasteProfiles: string[];
  onSelectedTasteProfilesChange: (next: string[]) => void;

  selectedAssortmentTypes: string[];
  onSelectedAssortmentTypesChange: (next: string[]) => void;

  priceRange: Range;
  onPriceRangeChange: (next: Range) => void;
  volumeRange: Range;
  onVolumeRangeChange: (next: Range) => void;
  alcoholRange: Range;
  onAlcoholRangeChange: (next: Range) => void;

  inStockOnly: boolean;
  onInStockOnlyChange: (next: boolean) => void;

  onResetAll: () => void;
}

export function Sidebar(props: SidebarProps) {
  const {
    stores,
    storesLoading,
    storesError,
    selectedStores,
    onSelectedStoresChange,
    filterOptions,
    filterOptionsLoading,
    selectedCountries,
    onSelectedCountriesChange,
    selectedWineTypes,
    onSelectedWineTypesChange,
    selectedTasteProfiles,
    onSelectedTasteProfilesChange,
    selectedAssortmentTypes,
    onSelectedAssortmentTypesChange,
    priceRange,
    onPriceRangeChange,
    volumeRange,
    onVolumeRangeChange,
    alcoholRange,
    onAlcoholRangeChange,
    inStockOnly,
    onInStockOnlyChange,
    onResetAll,
  } = props;

  const storeItems: CheckboxItem[] = useMemo(
    () =>
      stores.map((s) => {
        const name = s.displayName || s.alias || "Okänd butik";
        const city = s.city || "";
        const label = city ? `${name}, ${city} (${s.siteId})` : `${name} (${s.siteId})`;
        return {
          value: s.siteId,
          label,
          searchText: `${name} ${city} ${s.siteId}`,
        };
      }),
    [stores]
  );

  const countryItems: CheckboxItem[] = useMemo(
    () => filterOptions.countries.map((c) => ({ value: c, label: c })),
    [filterOptions.countries]
  );

  const wineTypeItems: CheckboxItem[] = useMemo(
    () => filterOptions.wineTypes.map((t) => ({ value: t, label: t })),
    [filterOptions.wineTypes]
  );

  const tasteProfileItems: CheckboxItem[] = useMemo(
    () => filterOptions.tasteProfiles.map((t) => ({ value: t, label: t })),
    [filterOptions.tasteProfiles]
  );

  const assortmentTypeItems: CheckboxItem[] = useMemo(
    () => filterOptions.assortmentTypes.map((t) => ({ value: t, label: t })),
    [filterOptions.assortmentTypes]
  );

  return (
    <aside
      className="flex h-full w-full shrink-0 flex-col overflow-y-auto bg-wine-dark p-4 shadow-xl md:w-80"
      aria-label="Filter"
    >
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-white">Filter</h2>
        <button
          type="button"
          onClick={onResetAll}
          className="text-xs text-white/70 underline hover:text-white"
        >
          Återställ alla
        </button>
      </div>

      <div className="space-y-3">
        {storesError ? (
          <div className="rounded bg-red-500/20 p-2 text-sm text-white">
            Kunde inte hämta butiker: {storesError}
          </div>
        ) : null}

        <Section title="Butiker" defaultOpen badge={selectedStores.length || ""}>
          <CheckboxList
            label="Butiker"
            items={storeItems}
            loading={storesLoading}
            selected={selectedStores}
            onChange={onSelectedStoresChange}
            searchPlaceholder="Sök butik eller stad..."
            emptyText="Inga butiker matchar"
          />
        </Section>

        <Section title="Vintyp" defaultOpen badge={selectedWineTypes.length || ""}>
          <CheckboxList
            label="Vintyp"
            items={wineTypeItems}
            loading={filterOptionsLoading}
            selected={selectedWineTypes}
            onChange={onSelectedWineTypesChange}
            searchPlaceholder="Sök vintyp..."
            emptyText="Inga vintyper"
          />
        </Section>

        <Section title="Smakprofil" badge={selectedTasteProfiles.length || ""}>
          <CheckboxList
            label="Smakprofil"
            items={tasteProfileItems}
            loading={filterOptionsLoading}
            selected={selectedTasteProfiles}
            onChange={onSelectedTasteProfilesChange}
            searchPlaceholder="Sök smakprofil..."
            emptyText={
              selectedWineTypes.length === 0
                ? "Välj en vintyp ovan för att se profiler"
                : "Inga smakprofiler"
            }
          />
        </Section>

        <Section title="Land" badge={selectedCountries.length || ""}>
          <CheckboxList
            label="Land"
            items={countryItems}
            loading={filterOptionsLoading}
            selected={selectedCountries}
            onChange={onSelectedCountriesChange}
            searchPlaceholder="Sök land..."
            emptyText="Inga länder"
          />
        </Section>

        <Section
          title="Sortiment"
          badge={selectedAssortmentTypes.length || ""}
        >
          <CheckboxList
            label="Sortiment"
            items={assortmentTypeItems}
            loading={filterOptionsLoading}
            selected={selectedAssortmentTypes}
            onChange={onSelectedAssortmentTypesChange}
            searchPlaceholder="Sök sortiment..."
            emptyText="Inga sortimentstyper"
          />
        </Section>

        <Section title="Pris, volym, alkohol" defaultOpen>
          <RangeSlider
            label="Pris"
            unit="kr"
            min={0}
            max={5000}
            step={50}
            value={priceRange}
            onChange={onPriceRangeChange}
          />
          <RangeSlider
            label="Volym"
            unit="ml"
            min={0}
            max={1500}
            step={50}
            value={volumeRange}
            onChange={onVolumeRangeChange}
          />
          <RangeSlider
            label="Alkohol"
            unit="%"
            min={0}
            max={20}
            step={0.5}
            value={alcoholRange}
            onChange={onAlcoholRangeChange}
          />
        </Section>

        <Section title="Övrigt" defaultOpen>
          <Toggle
            label="Endast tillgängliga"
            description="Dölj viner som är slut eller tillfälligt slut"
            checked={inStockOnly}
            onChange={onInStockOnlyChange}
          />
        </Section>
      </div>
    </aside>
  );
}
