'use client';

import { useRouter } from 'next/navigation';
import { SearchHistory } from '@/components/organisms';
import { useSearches, useRetrySearch, useDeleteSearch } from '@/hooks';
import { Spinner } from '@/components/atoms';
import type { SearchJob } from '@/types';

export default function HistoryPage() {
  const router = useRouter();
  const { data: searchesData, isLoading } = useSearches(1, 50);
  const retrySearch = useRetrySearch();
  const deleteSearch = useDeleteSearch();

  const handleViewResults = (search: SearchJob) => {
    router.push(`/search/${search.id}`);
  };

  const handleRetry = (search: SearchJob) => {
    retrySearch.mutate(search.id);
  };

  const handleDelete = (search: SearchJob) => {
    if (confirm('Are you sure you want to delete this search?')) {
      deleteSearch.mutate(search.id);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Search History</h1>
        <p className="text-gray-500">
          {searchesData?.total || 0} total searches
        </p>
      </div>

      {/* Search list */}
      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <Spinner size="lg" />
        </div>
      ) : (
        <SearchHistory
          searches={searchesData?.items || []}
          onViewResults={handleViewResults}
          onRetry={handleRetry}
          onDelete={handleDelete}
        />
      )}
    </div>
  );
}
