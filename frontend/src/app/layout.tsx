import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'ManoVeil — Unveiling the Mind',
  description: 'Universal AI/ML Mental Health Intelligence Platform',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="font-sans antialiased bg-white text-gray-900 min-h-screen">
        {children}
      </body>
    </html>
  );
}
