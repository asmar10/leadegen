'use client';

import { useState, useMemo } from 'react';
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  flexRender,
  createColumnHelper,
  type SortingState,
} from '@tanstack/react-table';
import { ChevronUp, ChevronDown, ExternalLink, Mail, Phone, ChevronLeft, ChevronRight } from 'lucide-react';
import { Button, Badge } from '@/components/atoms';
import { SocialLink } from '@/components/molecules';
import { cn, truncate } from '@/lib/utils';
import type { Store } from '@/types';

export interface LeadsTableProps {
  stores: Store[];
  onRowClick?: (store: Store) => void;
  isLoading?: boolean;
}

const columnHelper = createColumnHelper<Store>();

export default function LeadsTable({ stores, onRowClick, isLoading }: LeadsTableProps) {
  const [sorting, setSorting] = useState<SortingState>([]);

  const columns = useMemo(
    () => [
      columnHelper.accessor('store_name', {
        header: 'Store',
        cell: (info) => (
          <div className="flex flex-col">
            <span className="font-medium text-gray-900">
              {info.getValue() || info.row.original.domain}
            </span>
            <a
              href={info.row.original.url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-gray-500 hover:text-primary-600 flex items-center gap-1"
              onClick={(e) => e.stopPropagation()}
            >
              {info.row.original.domain}
              <ExternalLink className="h-3 w-3" />
            </a>
          </div>
        ),
      }),
      columnHelper.accessor('email', {
        header: 'Contact',
        cell: (info) => {
          const email = info.getValue();
          const phone = info.row.original.phone;

          if (!email && !phone) {
            return <span className="text-gray-400">-</span>;
          }

          return (
            <div className="flex flex-col gap-1">
              {email && (
                <a
                  href={`mailto:${email}`}
                  className="text-sm text-gray-600 hover:text-primary-600 flex items-center gap-1"
                  onClick={(e) => e.stopPropagation()}
                >
                  <Mail className="h-3.5 w-3.5" />
                  {truncate(email, 25)}
                </a>
              )}
              {phone && (
                <a
                  href={`tel:${phone}`}
                  className="text-sm text-gray-600 hover:text-primary-600 flex items-center gap-1"
                  onClick={(e) => e.stopPropagation()}
                >
                  <Phone className="h-3.5 w-3.5" />
                  {phone}
                </a>
              )}
            </div>
          );
        },
      }),
      columnHelper.accessor('niche', {
        header: 'Niche',
        cell: (info) => {
          const niche = info.getValue();
          return niche ? (
            <Badge variant="default">{niche}</Badge>
          ) : (
            <span className="text-gray-400">-</span>
          );
        },
      }),
      columnHelper.accessor('country', {
        header: 'Country',
        cell: (info) => info.getValue() || <span className="text-gray-400">-</span>,
      }),
      columnHelper.display({
        id: 'social',
        header: 'Social',
        cell: (info) => {
          const { instagram, tiktok, facebook, twitter } = info.row.original;
          const hasSocial = instagram || tiktok || facebook || twitter;

          if (!hasSocial) {
            return <span className="text-gray-400">-</span>;
          }

          return (
            <div className="flex flex-wrap gap-1" onClick={(e) => e.stopPropagation()}>
              {instagram && <SocialLink platform="instagram" handle={instagram} />}
              {tiktok && <SocialLink platform="tiktok" handle={tiktok} />}
            </div>
          );
        },
      }),
    ],
    []
  );

  const table = useReactTable({
    data: stores,
    columns,
    state: { sorting },
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    initialState: {
      pagination: { pageSize: 20 },
    },
  });

  if (isLoading) {
    return (
      <div className="card overflow-hidden">
        <div className="animate-pulse">
          <div className="h-12 bg-gray-100 border-b" />
          {[...Array(5)].map((_, i) => (
            <div key={i} className="h-16 border-b flex items-center px-6 gap-4">
              <div className="h-4 bg-gray-200 rounded w-1/4" />
              <div className="h-4 bg-gray-200 rounded w-1/4" />
              <div className="h-4 bg-gray-200 rounded w-1/6" />
              <div className="h-4 bg-gray-200 rounded w-1/6" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (stores.length === 0) {
    return (
      <div className="card p-12 text-center">
        <p className="text-gray-500">No stores found</p>
      </div>
    );
  }

  return (
    <div className="card overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50 border-b border-gray-200">
            {table.getHeaderGroups().map((headerGroup) => (
              <tr key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <th
                    key={header.id}
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    {header.isPlaceholder ? null : (
                      <button
                        className={cn(
                          'flex items-center gap-1',
                          header.column.getCanSort() && 'cursor-pointer select-none hover:text-gray-700'
                        )}
                        onClick={header.column.getToggleSortingHandler()}
                      >
                        {flexRender(header.column.columnDef.header, header.getContext())}
                        {{
                          asc: <ChevronUp className="h-4 w-4" />,
                          desc: <ChevronDown className="h-4 w-4" />,
                        }[header.column.getIsSorted() as string] ?? null}
                      </button>
                    )}
                  </th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody className="divide-y divide-gray-200">
            {table.getRowModel().rows.map((row) => (
              <tr
                key={row.id}
                className={cn(
                  'hover:bg-gray-50 transition-colors',
                  onRowClick && 'cursor-pointer'
                )}
                onClick={() => onRowClick?.(row.original)}
              >
                {row.getVisibleCells().map((cell) => (
                  <td key={cell.id} className="px-6 py-4 whitespace-nowrap">
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      <div className="px-6 py-4 border-t border-gray-200 flex items-center justify-between">
        <p className="text-sm text-gray-500">
          Showing {table.getState().pagination.pageIndex * table.getState().pagination.pageSize + 1} to{' '}
          {Math.min(
            (table.getState().pagination.pageIndex + 1) * table.getState().pagination.pageSize,
            stores.length
          )}{' '}
          of {stores.length} results
        </p>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => table.previousPage()}
            disabled={!table.getCanPreviousPage()}
          >
            <ChevronLeft className="h-4 w-4" />
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => table.nextPage()}
            disabled={!table.getCanNextPage()}
          >
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}
