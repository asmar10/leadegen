import axios from 'axios';
import type {
  Store,
  StoreListResponse,
  StoreFilters,
  FilterOptions,
  SearchJob,
  SearchJobWithResults,
  SearchJobListResponse,
  CreateSearchRequest,
} from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Stores API
export const storesApi = {
  list: async (filters: StoreFilters = {}): Promise<StoreListResponse> => {
    const params = new URLSearchParams();

    if (filters.query) params.append('query', filters.query);
    if (filters.niche) params.append('niche', filters.niche);
    if (filters.country) params.append('country', filters.country);
    if (filters.has_email !== undefined) params.append('has_email', String(filters.has_email));
    if (filters.has_instagram !== undefined) params.append('has_instagram', String(filters.has_instagram));
    if (filters.has_tiktok !== undefined) params.append('has_tiktok', String(filters.has_tiktok));
    if (filters.page) params.append('page', String(filters.page));
    if (filters.page_size) params.append('page_size', String(filters.page_size));

    const { data } = await api.get<StoreListResponse>(`/stores?${params}`);
    return data;
  },

  get: async (id: number): Promise<Store> => {
    const { data } = await api.get<Store>(`/stores/${id}`);
    return data;
  },

  getFilters: async (): Promise<FilterOptions> => {
    const { data } = await api.get<FilterOptions>('/stores/filters');
    return data;
  },

  rescrape: async (id: number, scrapeSocial = false): Promise<void> => {
    await api.post(`/stores/${id}/rescrape?scrape_social=${scrapeSocial}`);
  },

  delete: async (id: number): Promise<void> => {
    await api.delete(`/stores/${id}`);
  },
};

// Searches API
export const searchesApi = {
  list: async (page = 1, pageSize = 20): Promise<SearchJobListResponse> => {
    const { data } = await api.get<SearchJobListResponse>(
      `/searches?page=${page}&page_size=${pageSize}`
    );
    return data;
  },

  getRecent: async (limit = 10): Promise<SearchJob[]> => {
    const { data } = await api.get<SearchJob[]>(`/searches/recent?limit=${limit}`);
    return data;
  },

  get: async (id: number): Promise<SearchJob> => {
    const { data } = await api.get<SearchJob>(`/searches/${id}`);
    return data;
  },

  getResults: async (id: number): Promise<SearchJobWithResults> => {
    const { data } = await api.get<SearchJobWithResults>(`/searches/${id}/results`);
    return data;
  },

  create: async (request: CreateSearchRequest): Promise<SearchJob> => {
    const { data } = await api.post<SearchJob>('/searches', request);
    return data;
  },

  retry: async (id: number): Promise<SearchJob> => {
    const { data } = await api.post<SearchJob>(`/searches/${id}/retry`);
    return data;
  },

  delete: async (id: number): Promise<void> => {
    await api.delete(`/searches/${id}`);
  },
};

export default api;
