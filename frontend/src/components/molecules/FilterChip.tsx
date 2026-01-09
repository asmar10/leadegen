'use client';

import { X } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface FilterChipProps {
  label: string;
  value: string;
  onRemove: () => void;
  className?: string;
}

export default function FilterChip({
  label,
  value,
  onRemove,
  className,
}: FilterChipProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 px-3 py-1.5 bg-primary-50 text-primary-700 rounded-full text-sm',
        className
      )}
    >
      <span className="text-primary-500">{label}:</span>
      <span className="font-medium">{value}</span>
      <button
        onClick={onRemove}
        className="ml-0.5 p-0.5 rounded-full hover:bg-primary-100 transition-colors"
      >
        <X className="h-3.5 w-3.5" />
      </button>
    </span>
  );
}
