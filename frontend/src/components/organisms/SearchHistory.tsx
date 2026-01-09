'use client';

import { Clock, MapPin, Tag, ArrowRight, RefreshCw, Trash2 } from 'lucide-react';
import { Button } from '@/components/atoms';
import { StatusBadge } from '@/components/molecules';
import { formatRelativeTime } from '@/lib/utils';
import type { SearchJob } from '@/types';

export interface SearchHistoryProps {
  searches: SearchJob[];
  onViewResults: (search: SearchJob) => void;
  onRetry?: (search: SearchJob) => void;
  onDelete?: (search: SearchJob) => void;
  isLoading?: boolean;
}

export default function SearchHistory({
  searches,
  onViewResults,
  onRetry,
  onDelete,
  isLoading,
}: SearchHistoryProps) {
  if (isLoading) {
    return (
      <div className="space-y-3">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="card p-4 animate-pulse">
            <div className="flex items-center justify-between">
              <div className="space-y-2">
                <div className="h-4 bg-gray-200 rounded w-40" />
                <div className="h-3 bg-gray-200 rounded w-24" />
              </div>
              <div className="h-6 bg-gray-200 rounded w-20" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (searches.length === 0) {
    return (
      <div className="card p-8 text-center">
        <Clock className="h-12 w-12 text-gray-300 mx-auto mb-3" />
        <p className="text-gray-500">No search history yet</p>
        <p className="text-sm text-gray-400 mt-1">Your searches will appear here</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {searches.map((search) => (
        <div
          key={search.id}
          className="card p-4 hover:shadow-md transition-shadow"
        >
          <div className="flex items-center justify-between">
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-3 mb-1">
                <h4 className="font-medium text-gray-900 truncate">
                  {search.niche || search.query}
                </h4>
                <StatusBadge status={search.status} />
              </div>
              <div className="flex items-center gap-4 text-sm text-gray-500">
                {search.location && (
                  <span className="flex items-center gap-1">
                    <MapPin className="h-3.5 w-3.5" />
                    {search.location}
                  </span>
                )}
                <span className="flex items-center gap-1">
                  <Clock className="h-3.5 w-3.5" />
                  {formatRelativeTime(search.created_at)}
                </span>
                {search.status === 'COMPLETED' && (
                  <span className="flex items-center gap-1">
                    <Tag className="h-3.5 w-3.5" />
                    {search.stores_found} stores found
                  </span>
                )}
              </div>
            </div>

            <div className="flex items-center gap-2 ml-4">
              {search.status === 'FAILED' && onRetry && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => onRetry(search)}
                >
                  <RefreshCw className="h-4 w-4" />
                </Button>
              )}
              {search.status === 'COMPLETED' && search.stores_found > 0 && (
                <Button
                  variant="primary"
                  size="sm"
                  onClick={() => onViewResults(search)}
                >
                  View Results
                  <ArrowRight className="h-4 w-4 ml-1" />
                </Button>
              )}
              {onDelete && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => onDelete(search)}
                  className="text-gray-400 hover:text-red-600"
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
