'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { ArrowLeft, Download, RefreshCw } from 'lucide-react';
import { Button, Spinner } from '@/components/atoms';
import { StatusBadge } from '@/components/molecules';
import { LeadsTable, LeadDetail } from '@/components/organisms';
import { useSearch, useSearchResults, useRetrySearch, useRescrapeStore, useToast, useWebSocket } from '@/hooks';
import { exportToCSV, exportToJSON } from '@/lib/export';
import type { Store } from '@/types';

export default function SearchResultPage() {
  const params = useParams();
  const router = useRouter();
  const searchId = Number(params.id);
  const toast = useToast();

  const { data: search, isLoading: isLoadingSearch, refetch: refetchSearch } = useSearch(searchId);
  const { data: searchResults, isLoading: isLoadingResults, refetch: refetchResults } = useSearchResults(searchId);
  const retrySearch = useRetrySearch();
  const rescrapeStore = useRescrapeStore();

  const [selectedStore, setSelectedStore] = useState<Store | null>(null);

  // WebSocket for real-time updates
  const { isConnected } = useWebSocket({
    searchId,
    onMessage: (message) => {
      if (message.type === 'search_update') {
        refetchSearch();
        if (message.status === 'COMPLETED') {
          refetchResults();
          toast.success('Search completed', `Found ${message.stores_found} stores`);
        } else if (message.status === 'FAILED') {
          toast.error('Search failed', message.error || 'An error occurred');
        }
      } else if (message.type === 'store_found') {
        // Could add store to list optimistically
        refetchResults();
      }
    },
    onConnect: () => {
      console.log('WebSocket connected');
    },
  });

  const handleExportCSV = () => {
    if (searchResults?.stores) {
      exportToCSV(searchResults.stores, `leads-${search?.niche || 'search'}-${searchId}`);
      toast.success('Export complete', 'CSV file downloaded');
    }
  };

  const handleExportJSON = () => {
    if (searchResults?.stores) {
      exportToJSON(searchResults.stores, `leads-${search?.niche || 'search'}-${searchId}`);
      toast.success('Export complete', 'JSON file downloaded');
    }
  };

  const handleRetry = async () => {
    try {
      await retrySearch.mutateAsync(searchId);
      toast.info('Search restarted', 'The search has been queued for retry');
    } catch (error) {
      toast.error('Retry failed', 'Could not restart the search');
    }
  };

  const handleRescrape = async (storeId: number) => {
    try {
      await rescrapeStore.mutateAsync({ id: storeId, scrapeSocial: true });
      toast.success('Refresh queued', 'Store data will be updated shortly');
    } catch (error) {
      toast.error('Refresh failed', 'Could not refresh store data');
    }
  };

  if (isLoadingSearch) {
    return (
      <div className="flex items-center justify-center py-12">
        <Spinner size="lg" />
      </div>
    );
  }

  if (!search) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Search not found</p>
        <Button variant="outline" className="mt-4" onClick={() => router.push('/')}>
          Go back
        </Button>
      </div>
    );
  }

  const isRunning = search.status === 'RUNNING' || search.status === 'PENDING';

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" onClick={() => router.push('/')}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back
          </Button>
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-bold text-gray-900">
                {search.niche || search.query}
              </h1>
              <StatusBadge status={search.status} />
              {isRunning && isConnected && (
                <span className="flex items-center gap-1.5 text-xs text-green-600">
                  <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                  Live
                </span>
              )}
            </div>
            {search.location && (
              <p className="text-gray-500">{search.location}</p>
            )}
          </div>
        </div>

        <div className="flex items-center gap-2">
          {search.status === 'FAILED' && (
            <Button
              variant="outline"
              onClick={handleRetry}
              isLoading={retrySearch.isPending}
            >
              <RefreshCw className="h-4 w-4 mr-2" />
              Retry
            </Button>
          )}
          {search.status === 'COMPLETED' && searchResults?.stores && searchResults.stores.length > 0 && (
            <>
              <Button variant="outline" onClick={handleExportCSV}>
                <Download className="h-4 w-4 mr-2" />
                CSV
              </Button>
              <Button variant="outline" onClick={handleExportJSON}>
                <Download className="h-4 w-4 mr-2" />
                JSON
              </Button>
            </>
          )}
        </div>
      </div>

      {/* Status message for running searches */}
      {isRunning && (
        <div className="card p-6 text-center">
          <Spinner size="lg" className="mx-auto mb-4" />
          <h2 className="text-lg font-medium text-gray-900">
            {search.status === 'PENDING' ? 'Search queued...' : 'Searching for stores...'}
          </h2>
          <p className="text-gray-500 mt-1">
            This may take a few minutes. The page will update automatically.
          </p>
          {search.stores_found > 0 && (
            <p className="text-primary-600 mt-2 font-medium">
              {search.stores_found} stores found so far
            </p>
          )}
        </div>
      )}

      {/* Error message */}
      {search.status === 'FAILED' && (
        <div className="card p-6 bg-red-50 border-red-200">
          <h2 className="text-lg font-medium text-red-800">Search Failed</h2>
          <p className="text-red-600 mt-1">
            {search.error_message || 'An error occurred while searching. Please try again.'}
          </p>
        </div>
      )}

      {/* Results table */}
      {search.status === 'COMPLETED' && (
        <>
          <div className="flex items-center justify-between">
            <p className="text-gray-500">
              {searchResults?.stores.length || 0} stores found
            </p>
          </div>

          <LeadsTable
            stores={searchResults?.stores || []}
            onRowClick={setSelectedStore}
            isLoading={isLoadingResults}
          />
        </>
      )}

      {/* Store detail modal */}
      <LeadDetail
        store={selectedStore}
        isOpen={!!selectedStore}
        onClose={() => setSelectedStore(null)}
        onRescrape={handleRescrape}
        isRescraping={rescrapeStore.isPending}
      />
    </div>
  );
}
