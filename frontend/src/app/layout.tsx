import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import Providers from './providers';
import { DashboardLayout } from '@/components/templates';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'LeadGen - Shopify Store Discovery',
  description: 'Discover and extract Shopify store data for lead generation',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <Providers>
          <DashboardLayout>{children}</DashboardLayout>
        </Providers>
      </body>
    </html>
  );
}
