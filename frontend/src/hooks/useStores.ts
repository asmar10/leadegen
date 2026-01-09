'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { storesApi } from '@/lib/api';
import type { StoreFilters } from '@/types';

export function useStores(filters: StoreFilters = {}) {
  return useQuery({
    queryKey: ['stores', filters],
    queryFn: () => storesApi.list(filters),
  });
}

export function useStore(id: number) {
  return useQuery({
    queryKey: ['store', id],
    queryFn: () => storesApi.get(id),
    enabled: !!id,
  });
}

export function useFilterOptions() {
  return useQuery({
    queryKey: ['filterOptions'],
    queryFn: () => storesApi.getFilters(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

export function useRescrapeStore() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, scrapeSocial }: { id: number; scrapeSocial?: boolean }) =>
      storesApi.rescrape(id, scrapeSocial),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['store', id] });
      queryClient.invalidateQueries({ queryKey: ['stores'] });
    },
  });
}

export function useDeleteStore() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => storesApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['stores'] });
    },
  });
}
