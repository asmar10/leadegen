'use client';

import { useState } from 'react';
import { Search } from 'lucide-react';
import { Button, Input } from '@/components/atoms';

export interface SearchInputProps {
  placeholder?: string;
  onSearch: (query: string) => void;
  isLoading?: boolean;
  defaultValue?: string;
}

export default function SearchInput({
  placeholder = 'Search...',
  onSearch,
  isLoading = false,
  defaultValue = '',
}: SearchInputProps) {
  const [query, setQuery] = useState(defaultValue);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch(query.trim());
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-2">
      <Input
        type="text"
        placeholder={placeholder}
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        leftIcon={<Search className="h-5 w-5" />}
        className="flex-1"
      />
      <Button type="submit" isLoading={isLoading}>
        Search
      </Button>
    </form>
  );
}
