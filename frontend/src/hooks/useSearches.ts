'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { searchesApi } from '@/lib/api';
import type { CreateSearchRequest } from '@/types';

export function useSearches(page = 1, pageSize = 20) {
  return useQuery({
    queryKey: ['searches', page, pageSize],
    queryFn: () => searchesApi.list(page, pageSize),
  });
}

export function useRecentSearches(limit = 10) {
  return useQuery({
    queryKey: ['recentSearches', limit],
    queryFn: () => searchesApi.getRecent(limit),
    refetchInterval: 5000, // Refresh every 5 seconds to update running searches
  });
}

export function useSearch(id: number) {
  return useQuery({
    queryKey: ['search', id],
    queryFn: () => searchesApi.get(id),
    enabled: !!id,
    refetchInterval: (data) => {
      // Keep polling while search is running
      if (data?.status === 'RUNNING' || data?.status === 'PENDING') {
        return 3000;
      }
      return false;
    },
  });
}

export function useSearchResults(id: number) {
  return useQuery({
    queryKey: ['searchResults', id],
    queryFn: () => searchesApi.getResults(id),
    enabled: !!id,
  });
}

export function useCreateSearch() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateSearchRequest) => searchesApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['searches'] });
      queryClient.invalidateQueries({ queryKey: ['recentSearches'] });
    },
  });
}

export function useRetrySearch() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => searchesApi.retry(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: ['search', id] });
      queryClient.invalidateQueries({ queryKey: ['searches'] });
      queryClient.invalidateQueries({ queryKey: ['recentSearches'] });
    },
  });
}

export function useDeleteSearch() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => searchesApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['searches'] });
      queryClient.invalidateQueries({ queryKey: ['recentSearches'] });
    },
  });
}
