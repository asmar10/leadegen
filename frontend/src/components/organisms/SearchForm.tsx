'use client';

import { useState } from 'react';
import { Search, MapPin, Tag } from 'lucide-react';
import { Button, Input } from '@/components/atoms';
import type { CreateSearchRequest } from '@/types';

export interface SearchFormProps {
  onSubmit: (data: CreateSearchRequest) => void;
  isLoading?: boolean;
}

export default function SearchForm({ onSubmit, isLoading = false }: SearchFormProps) {
  const [niche, setNiche] = useState('');
  const [location, setLocation] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!niche.trim()) return;

    onSubmit({
      query: niche.trim(),
      niche: niche.trim(),
      location: location.trim() || undefined,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="grid gap-4 md:grid-cols-2">
        <Input
          label="Niche / Industry"
          placeholder="e.g., Fitness, Fashion, Home Decor"
          value={niche}
          onChange={(e) => setNiche(e.target.value)}
          leftIcon={<Tag className="h-5 w-5" />}
          required
        />
        <Input
          label="Location (Optional)"
          placeholder="e.g., United States, UK, Canada"
          value={location}
          onChange={(e) => setLocation(e.target.value)}
          leftIcon={<MapPin className="h-5 w-5" />}
        />
      </div>

      <div className="flex justify-end">
        <Button
          type="submit"
          size="lg"
          isLoading={isLoading}
          disabled={!niche.trim()}
        >
          <Search className="h-5 w-5 mr-2" />
          Find Shopify Stores
        </Button>
      </div>
    </form>
  );
}
