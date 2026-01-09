import type { Store } from '@/types';

export function exportToCSV(stores: Store[], filename = 'leads'): void {
  const headers = [
    'Store Name',
    'Domain',
    'Email',
    'Phone',
    'Country',
    'Niche',
    'Instagram',
    'TikTok',
    'Facebook',
    'Twitter',
    'URL',
  ];

  const rows = stores.map((store) => [
    store.store_name || '',
    store.domain,
    store.email || '',
    store.phone || '',
    store.country || '',
    store.niche || '',
    store.instagram || '',
    store.tiktok || '',
    store.facebook || '',
    store.twitter || '',
    store.url,
  ]);

  const csvContent = [
    headers.join(','),
    ...rows.map((row) =>
      row.map((cell) => `"${String(cell).replace(/"/g, '""')}"`).join(',')
    ),
  ].join('\n');

  downloadFile(csvContent, `${filename}.csv`, 'text/csv');
}

export function exportToJSON(stores: Store[], filename = 'leads'): void {
  const jsonContent = JSON.stringify(stores, null, 2);
  downloadFile(jsonContent, `${filename}.json`, 'application/json');
}

function downloadFile(content: string, filename: string, mimeType: string): void {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}
