'use client';

import { Select, Button } from '@/components/atoms';
import { FilterChip } from '@/components/molecules';
import { X } from 'lucide-react';
import type { StoreFilters, FilterOptions } from '@/types';

export interface FilterPanelProps {
  filters: StoreFilters;
  filterOptions: FilterOptions;
  onFilterChange: (filters: StoreFilters) => void;
  onClearFilters: () => void;
}

export default function FilterPanel({
  filters,
  filterOptions,
  onFilterChange,
  onClearFilters,
}: FilterPanelProps) {
  const hasActiveFilters =
    filters.niche ||
    filters.country ||
    filters.has_email ||
    filters.has_instagram ||
    filters.has_tiktok;

  const nicheOptions = [
    { value: '', label: 'All Niches' },
    ...filterOptions.niches.map((n) => ({ value: n, label: n })),
  ];

  const countryOptions = [
    { value: '', label: 'All Countries' },
    ...filterOptions.countries.map((c) => ({ value: c, label: c })),
  ];

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-4">
        <div className="w-48">
          <Select
            options={nicheOptions}
            value={filters.niche || ''}
            onChange={(e) => onFilterChange({ ...filters, niche: e.target.value || undefined })}
            placeholder="Select niche"
          />
        </div>

        <div className="w-48">
          <Select
            options={countryOptions}
            value={filters.country || ''}
            onChange={(e) => onFilterChange({ ...filters, country: e.target.value || undefined })}
            placeholder="Select country"
          />
        </div>

        <div className="flex items-center gap-3">
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={filters.has_email || false}
              onChange={(e) =>
                onFilterChange({ ...filters, has_email: e.target.checked || undefined })
              }
              className="h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
            />
            <span className="text-sm text-gray-700">Has Email</span>
          </label>

          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={filters.has_instagram || false}
              onChange={(e) =>
                onFilterChange({ ...filters, has_instagram: e.target.checked || undefined })
              }
              className="h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
            />
            <span className="text-sm text-gray-700">Has Instagram</span>
          </label>

          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={filters.has_tiktok || false}
              onChange={(e) =>
                onFilterChange({ ...filters, has_tiktok: e.target.checked || undefined })
              }
              className="h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
            />
            <span className="text-sm text-gray-700">Has TikTok</span>
          </label>
        </div>

        {hasActiveFilters && (
          <Button variant="ghost" size="sm" onClick={onClearFilters}>
            <X className="h-4 w-4 mr-1" />
            Clear
          </Button>
        )}
      </div>

      {/* Active filter chips */}
      {hasActiveFilters && (
        <div className="flex flex-wrap gap-2">
          {filters.niche && (
            <FilterChip
              label="Niche"
              value={filters.niche}
              onRemove={() => onFilterChange({ ...filters, niche: undefined })}
            />
          )}
          {filters.country && (
            <FilterChip
              label="Country"
              value={filters.country}
              onRemove={() => onFilterChange({ ...filters, country: undefined })}
            />
          )}
          {filters.has_email && (
            <FilterChip
              label="Filter"
              value="Has Email"
              onRemove={() => onFilterChange({ ...filters, has_email: undefined })}
            />
          )}
          {filters.has_instagram && (
            <FilterChip
              label="Filter"
              value="Has Instagram"
              onRemove={() => onFilterChange({ ...filters, has_instagram: undefined })}
            />
          )}
          {filters.has_tiktok && (
            <FilterChip
              label="Filter"
              value="Has TikTok"
              onRemove={() => onFilterChange({ ...filters, has_tiktok: undefined })}
            />
          )}
        </div>
      )}
    </div>
  );
}
