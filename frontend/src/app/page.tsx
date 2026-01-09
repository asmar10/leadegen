'use client';

import { useRouter } from 'next/navigation';
import { Store, TrendingUp, Search as SearchIcon } from 'lucide-react';
import { SearchForm, SearchHistory } from '@/components/organisms';
import { StatCard } from '@/components/molecules';
import { useCreateSearch, useRecentSearches } from '@/hooks';
import type { CreateSearchRequest, SearchJob } from '@/types';

export default function HomePage() {
  const router = useRouter();
  const { data: recentSearches, isLoading: isLoadingSearches } = useRecentSearches(5);
  const createSearch = useCreateSearch();

  const handleSearch = async (data: CreateSearchRequest) => {
    try {
      const search = await createSearch.mutateAsync(data);
      router.push(`/search/${search.id}`);
    } catch (error) {
      console.error('Failed to create search:', error);
    }
  };

  const handleViewResults = (search: SearchJob) => {
    router.push(`/search/${search.id}`);
  };

  // Calculate stats from recent searches
  const completedSearches = recentSearches?.filter(s => s.status === 'COMPLETED') || [];
  const totalStoresFound = completedSearches.reduce((sum, s) => sum + s.stores_found, 0);

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Find Shopify Stores</h1>
        <p className="text-gray-500 mt-1">
          Discover Shopify stores by niche and location for lead generation
        </p>
      </div>

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-3">
        <StatCard
          label="Total Searches"
          value={recentSearches?.length || 0}
          icon={<SearchIcon className="h-6 w-6" />}
        />
        <StatCard
          label="Stores Found"
          value={totalStoresFound}
          icon={<Store className="h-6 w-6" />}
        />
        <StatCard
          label="Success Rate"
          value={completedSearches.length > 0 ? `${Math.round((completedSearches.length / (recentSearches?.length || 1)) * 100)}%` : '0%'}
          icon={<TrendingUp className="h-6 w-6" />}
        />
      </div>

      {/* Search Form */}
      <div className="card p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">New Search</h2>
        <SearchForm onSubmit={handleSearch} isLoading={createSearch.isPending} />
      </div>

      {/* Recent Searches */}
      <div>
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Searches</h2>
        <SearchHistory
          searches={recentSearches || []}
          onViewResults={handleViewResults}
          isLoading={isLoadingSearches}
        />
      </div>
    </div>
  );
}
