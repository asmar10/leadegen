'use client';

import { ExternalLink, Mail, Phone, Globe, Calendar, RefreshCw } from 'lucide-react';
import { Button, Badge, Modal } from '@/components/atoms';
import { SocialLink } from '@/components/molecules';
import { formatDateTime } from '@/lib/utils';
import type { Store } from '@/types';

export interface LeadDetailProps {
  store: Store | null;
  isOpen: boolean;
  onClose: () => void;
  onRescrape?: (id: number) => void;
  isRescraping?: boolean;
}

export default function LeadDetail({
  store,
  isOpen,
  onClose,
  onRescrape,
  isRescraping,
}: LeadDetailProps) {
  if (!store) return null;

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={store.store_name || store.domain} size="lg">
      <div className="px-6 py-4 space-y-6">
        {/* Header info */}
        <div className="flex items-start justify-between">
          <div>
            <a
              href={store.url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-primary-600 hover:text-primary-700 flex items-center gap-1.5 text-sm"
            >
              <Globe className="h-4 w-4" />
              {store.domain}
              <ExternalLink className="h-3.5 w-3.5" />
            </a>
            {store.description && (
              <p className="text-gray-600 mt-2 text-sm">{store.description}</p>
            )}
          </div>
          {store.niche && <Badge>{store.niche}</Badge>}
        </div>

        {/* Contact info */}
        <div className="grid gap-4 md:grid-cols-2">
          <div className="space-y-3">
            <h4 className="text-sm font-medium text-gray-500 uppercase tracking-wide">Contact</h4>
            {store.email ? (
              <a
                href={`mailto:${store.email}`}
                className="flex items-center gap-2 text-gray-900 hover:text-primary-600"
              >
                <Mail className="h-5 w-5 text-gray-400" />
                {store.email}
              </a>
            ) : (
              <p className="flex items-center gap-2 text-gray-400">
                <Mail className="h-5 w-5" />
                No email found
              </p>
            )}
            {store.phone ? (
              <a
                href={`tel:${store.phone}`}
                className="flex items-center gap-2 text-gray-900 hover:text-primary-600"
              >
                <Phone className="h-5 w-5 text-gray-400" />
                {store.phone}
              </a>
            ) : (
              <p className="flex items-center gap-2 text-gray-400">
                <Phone className="h-5 w-5" />
                No phone found
              </p>
            )}
          </div>

          <div className="space-y-3">
            <h4 className="text-sm font-medium text-gray-500 uppercase tracking-wide">Location</h4>
            <p className="text-gray-900">{store.country || 'Unknown'}</p>
          </div>
        </div>

        {/* Social media */}
        <div className="space-y-3">
          <h4 className="text-sm font-medium text-gray-500 uppercase tracking-wide">Social Media</h4>
          <div className="flex flex-wrap gap-2">
            {store.instagram && <SocialLink platform="instagram" handle={store.instagram} />}
            {store.tiktok && <SocialLink platform="tiktok" handle={store.tiktok} />}
            {store.facebook && <SocialLink platform="facebook" handle={store.facebook} />}
            {store.twitter && <SocialLink platform="twitter" handle={store.twitter} />}
            {!store.instagram && !store.tiktok && !store.facebook && !store.twitter && (
              <p className="text-gray-400 text-sm">No social media links found</p>
            )}
          </div>
        </div>

        {/* Metadata */}
        <div className="pt-4 border-t border-gray-200">
          <div className="flex items-center justify-between text-sm text-gray-500">
            <div className="flex items-center gap-4">
              <span className="flex items-center gap-1.5">
                <Calendar className="h-4 w-4" />
                Added {formatDateTime(store.created_at)}
              </span>
              {store.last_scraped_at && (
                <span>Last updated {formatDateTime(store.last_scraped_at)}</span>
              )}
            </div>
            {onRescrape && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => onRescrape(store.id)}
                isLoading={isRescraping}
              >
                <RefreshCw className="h-4 w-4 mr-1.5" />
                Refresh Data
              </Button>
            )}
          </div>
        </div>
      </div>
    </Modal>
  );
}
