export interface Store {
  siteId: string;
  displayName?: string | null;
  alias?: string | null;
  city?: string | null;
  county?: string | null;
}

export interface Range {
  min: number;
  max: number;
}

export interface AskRequest {
  prompt: string;
  storeIds: string[];
  countries: string[];
  wineTypes: string[];
  tasteProfiles: string[];
  assortmentTypes: string[];
  priceRange: Range;
  volumeRange: Range;
  alcoholRange: Range;
  inStockOnly: boolean;
}

export interface FilterOptions {
  wineTypes: string[];
  tasteProfiles: string[];
  assortmentTypes: string[];
  countries: string[];
}

export interface Wine {
  productNumber: string;
  productNameBold?: string | null;
  productNameThin?: string | null;
  producerName?: string | null;
  vintage?: string | null;
  country?: string | null;
  originLevel1?: string | null;
  categoryLevel2?: string | null;
  categoryLevel3?: string | null;
  assortmentText?: string | null;
  price?: number | null;
  volume?: number | null;
  alcoholPercentage?: number | null;
  productLaunchDate?: string | null;
  isCompletelyOutOfStock?: boolean;
  isTemporaryOutOfStock?: boolean;
}

export interface Recommendation {
  wine: Wine;
  motivation: string;
  systembolagetUrl: string;
}

export interface AskResponse {
  intro: string;
  recommendations: Recommendation[];
  matchedWineCount: number;
  notes: string[];
}

export type Role = "user" | "assistant";

export interface ChatMessage {
  id: string;
  role: Role;
  /** Free text. For user messages this is the prompt; for assistant messages
   *  this can be intro/error text. */
  content: string;
  recommendations?: Recommendation[];
  notes?: string[];
  matchedWineCount?: number;
  isStreaming?: boolean;
  isError?: boolean;
}
