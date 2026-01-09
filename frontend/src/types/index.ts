// Store types
export interface Store {
  id: number;
  url: string;
  domain: string;
  store_name: string | null;
  email: string | null;
  phone: string | null;
  country: string | null;
  niche: string | null;
  description: string | null;
  instagram: string | null;
  tiktok: string | null;
  facebook: string | null;
  twitter: string | null;
  created_at: string;
  updated_at: string;
  last_scraped_at: string | null;
}

export interface StoreListResponse {
  items: Store[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface StoreFilters {
  query?: string;
  niche?: string;
  country?: string;
  has_email?: boolean;
  has_instagram?: boolean;
  has_tiktok?: boolean;
  page?: number;
  page_size?: number;
}

export interface FilterOptions {
  niches: string[];
  countries: string[];
}

// Search types
export type SearchStatus = 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED';

export interface SearchJob {
  id: number;
  query: string;
  niche: string | null;
  location: string | null;
  status: SearchStatus;
  stores_found: number;
  error_message: string | null;
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
}

export interface SearchJobWithResults extends SearchJob {
  stores: Store[];
}

export interface SearchJobListResponse {
  items: SearchJob[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface CreateSearchRequest {
  query: string;
  niche?: string;
  location?: string;
}

// API response types
export interface ApiError {
  detail: string;
}
