'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useAuthStore } from '@/stores/auth-store';
import { PERSONAS } from '@/lib/constants';

const navItems = [
  { href: '/dashboard', label: 'Home', icon: '🏠' },
  { href: '/dashboard/chat', label: 'Chat', icon: '💬' },
  { href: '/dashboard/assessments', label: 'Assessments', icon: '📋' },
  { href: '/dashboard/trackers', label: 'Trackers', icon: '📊' },
  { href: '/dashboard/stress', label: 'Stress Score', icon: '🎯' },
  { href: '/dashboard/interventions', label: 'Wellness', icon: '🧘' },
  { href: '/dashboard/crisis', label: 'Crisis Help', icon: '🆘' },
  { href: '/dashboard/profile', label: 'Profile', icon: '👤' },
];

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { user, isAuthenticated, loadFromStorage, logout } = useAuthStore();
  const pathname = usePathname();
  const router = useRouter();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  useEffect(() => { loadFromStorage(); }, []);
  useEffect(() => {
    if (typeof window !== 'undefined' && !localStorage.getItem('access_token')) {
      router.push('/login');
    }
  }, []);

  const persona = user?.persona as keyof typeof PERSONAS || 'manoveil_core';
  const personaInfo = PERSONAS[persona] || PERSONAS.manoveil_core;

  return (
    <div className="min-h-screen bg-gray-50" data-persona={persona}>
      {/* Mobile header */}
      <div className="lg:hidden flex items-center justify-between p-4 bg-white border-b">
        <button onClick={() => setSidebarOpen(!sidebarOpen)} className="p-2">☰</button>
        <span className="font-semibold" style={{ color: personaInfo.color }}>{personaInfo.name}</span>
        <button onClick={() => { logout(); router.push('/login'); }} className="text-sm text-gray-500">Logout</button>
      </div>

      <div className="flex">
        {/* Sidebar */}
        <aside className={`${sidebarOpen ? 'block' : 'hidden'} lg:block w-64 min-h-screen bg-white border-r shadow-sm fixed lg:sticky top-0 z-40`}>
          <div className="p-6 border-b" style={{ backgroundColor: personaInfo.bg }}>
            <h2 className="text-xl font-bold" style={{ color: personaInfo.text }}>{personaInfo.name}</h2>
            <p className="text-sm mt-1 opacity-75" style={{ color: personaInfo.text }}>{user?.full_name}</p>
          </div>
          <nav className="p-4 space-y-1">
            {navItems.map((item) => (
              <Link key={item.href} href={item.href}
                className={`flex items-center gap-3 px-4 py-3 rounded-xl text-sm transition ${pathname === item.href ? 'bg-emerald-50 text-emerald-800 font-medium' : 'text-gray-600 hover:bg-gray-50'}`}>
                <span>{item.icon}</span>
                {item.label}
              </Link>
            ))}
          </nav>
          <div className="absolute bottom-4 left-4 right-4">
            <button onClick={() => { logout(); router.push('/login'); }}
              className="w-full py-2 text-sm text-gray-500 hover:text-gray-800 transition">
              Sign Out
            </button>
          </div>
        </aside>

        {/* Main content */}
        <main className="flex-1 p-6 lg:p-8 max-w-6xl">
          {children}
        </main>
      </div>

      {/* Floating SOS Button */}
      <Link href="/dashboard/crisis"
        className="fixed bottom-6 right-6 w-14 h-14 bg-red-500 text-white rounded-full flex items-center justify-center text-xl shadow-lg sos-pulse hover:bg-red-600 transition z-50"
        title="Crisis Support">
        🆘
      </Link>
    </div>
  );
}
