'use client';

import { Instagram, Facebook, Twitter } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface SocialLinkProps {
  platform: 'instagram' | 'tiktok' | 'facebook' | 'twitter';
  handle: string;
  className?: string;
}

const platformConfig = {
  instagram: {
    icon: Instagram,
    color: 'text-pink-600 hover:text-pink-700',
    bgColor: 'bg-pink-50 hover:bg-pink-100',
    baseUrl: 'https://instagram.com/',
  },
  tiktok: {
    icon: () => (
      <svg className="h-4 w-4" viewBox="0 0 24 24" fill="currentColor">
        <path d="M19.59 6.69a4.83 4.83 0 01-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 01-5.2 1.74 2.89 2.89 0 012.31-4.64 2.93 2.93 0 01.88.13V9.4a6.84 6.84 0 00-1-.05A6.33 6.33 0 005 20.1a6.34 6.34 0 0010.86-4.43v-7a8.16 8.16 0 004.77 1.52v-3.4a4.85 4.85 0 01-1-.1z" />
      </svg>
    ),
    color: 'text-gray-900 hover:text-black',
    bgColor: 'bg-gray-100 hover:bg-gray-200',
    baseUrl: 'https://tiktok.com/@',
  },
  facebook: {
    icon: Facebook,
    color: 'text-blue-600 hover:text-blue-700',
    bgColor: 'bg-blue-50 hover:bg-blue-100',
    baseUrl: 'https://facebook.com/',
  },
  twitter: {
    icon: Twitter,
    color: 'text-sky-500 hover:text-sky-600',
    bgColor: 'bg-sky-50 hover:bg-sky-100',
    baseUrl: 'https://twitter.com/',
  },
};

export default function SocialLink({
  platform,
  handle,
  className,
}: SocialLinkProps) {
  const config = platformConfig[platform];
  const Icon = config.icon;
  const cleanHandle = handle.replace('@', '');
  const url = config.baseUrl + cleanHandle;

  return (
    <a
      href={url}
      target="_blank"
      rel="noopener noreferrer"
      className={cn(
        'inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-sm transition-colors',
        config.bgColor,
        config.color,
        className
      )}
    >
      <Icon className="h-4 w-4" />
      <span>{handle}</span>
    </a>
  );
}
