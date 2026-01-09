'use client';

import { useState } from 'react';
import { Download } from 'lucide-react';
import { Button, Spinner } from '@/components/atoms';
import { SearchInput } from '@/components/molecules';
import { LeadsTable, FilterPanel, LeadDetail } from '@/components/organisms';
import { useStores, useFilterOptions, useRescrapeStore } from '@/hooks';
import { exportToCSV, exportToJSON } from '@/lib/export';
import type { Store, StoreFilters } from '@/types';

export default function LeadsPage() {
  const [filters, setFilters] = useState<StoreFilters>({
    page: 1,
    page_size: 20,
  });
  const [selectedStore, setSelectedStore] = useState<Store | null>(null);

  const { data: storesData, isLoading: isLoadingStores } = useStores(filters);
  const { data: filterOptions, isLoading: isLoadingFilters } = useFilterOptions();
  const rescrapeStore = useRescrapeStore();

  const handleSearch = (query: string) => {
    setFilters((prev) => ({ ...prev, query, page: 1 }));
  };

  const handleFilterChange = (newFilters: StoreFilters) => {
    setFilters((prev) => ({ ...prev, ...newFilters, page: 1 }));
  };

  const handleClearFilters = () => {
    setFilters({ page: 1, page_size: 20 });
  };

  const handleExportCSV = () => {
    if (storesData?.items) {
      exportToCSV(storesData.items, 'all-leads');
    }
  };

  const handleExportJSON = () => {
    if (storesData?.items) {
      exportToJSON(storesData.items, 'all-leads');
    }
  };

  const handleRescrape = (storeId: number) => {
    rescrapeStore.mutate({ id: storeId, scrapeSocial: true });
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">All Leads</h1>
          <p className="text-gray-500">
            {storesData?.total || 0} total stores in database
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={handleExportCSV} disabled={!storesData?.items?.length}>
            <Download className="h-4 w-4 mr-2" />
            CSV
          </Button>
          <Button variant="outline" onClick={handleExportJSON} disabled={!storesData?.items?.length}>
            <Download className="h-4 w-4 mr-2" />
            JSON
          </Button>
        </div>
      </div>

      {/* Search and filters */}
      <div className="card p-4 space-y-4">
        <SearchInput
          placeholder="Search stores by name, domain, or description..."
          onSearch={handleSearch}
          defaultValue={filters.query}
        />

        {!isLoadingFilters && filterOptions && (
          <FilterPanel
            filters={filters}
            filterOptions={filterOptions}
            onFilterChange={handleFilterChange}
            onClearFilters={handleClearFilters}
          />
        )}
      </div>

      {/* Results */}
      {isLoadingStores ? (
        <div className="flex items-center justify-center py-12">
          <Spinner size="lg" />
        </div>
      ) : (
        <LeadsTable
          stores={storesData?.items || []}
          onRowClick={setSelectedStore}
        />
      )}

      {/* Pagination info */}
      {storesData && storesData.pages > 1 && (
        <div className="flex items-center justify-center gap-2">
          <Button
            variant="outline"
            size="sm"
            disabled={filters.page === 1}
            onClick={() => setFilters((prev) => ({ ...prev, page: (prev.page || 1) - 1 }))}
          >
            Previous
          </Button>
          <span className="text-sm text-gray-500">
            Page {filters.page || 1} of {storesData.pages}
          </span>
          <Button
            variant="outline"
            size="sm"
            disabled={filters.page === storesData.pages}
            onClick={() => setFilters((prev) => ({ ...prev, page: (prev.page || 1) + 1 }))}
          >
            Next
          </Button>
        </div>
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
