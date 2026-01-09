'use client';

import { Badge, Spinner } from '@/components/atoms';
import type { SearchStatus } from '@/types';

export interface StatusBadgeProps {
  status: SearchStatus;
}

export default function StatusBadge({ status }: StatusBadgeProps) {
  const config: Record<SearchStatus, { variant: 'success' | 'warning' | 'error' | 'info'; label: string }> = {
    COMPLETED: { variant: 'success', label: 'Completed' },
    RUNNING: { variant: 'info', label: 'Running' },
    PENDING: { variant: 'warning', label: 'Pending' },
    FAILED: { variant: 'error', label: 'Failed' },
  };

  const { variant, label } = config[status];

  return (
    <Badge variant={variant} className="inline-flex items-center gap-1.5">
      {status === 'RUNNING' && <Spinner size="sm" className="h-3 w-3" />}
      {label}
    </Badge>
  );
}
