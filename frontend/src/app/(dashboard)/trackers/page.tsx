'use client';

import Link from 'next/link';

const trackers = [
  { href: '/dashboard/trackers/mood', label: 'Mood Journal', icon: '😊', desc: 'Log how you feel today', color: 'bg-amber-50 text-amber-800' },
  { href: '/dashboard/trackers/sleep', label: 'Sleep Tracker', icon: '🌙', desc: 'Track your sleep quality', color: 'bg-indigo-50 text-indigo-800' },
  { href: '/dashboard/trackers/activity', label: 'Activity Log', icon: '🏃', desc: 'Record your activities', color: 'bg-green-50 text-green-800' },
  { href: '/dashboard/trackers/social', label: 'Social Check-in', icon: '👥', desc: 'Weekly social engagement', color: 'bg-pink-50 text-pink-800' },
];

export default function TrackersPage() {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-800">Wellness Trackers</h2>
      <p className="text-gray-500">Regular tracking helps us understand your patterns and provide better support.</p>
      <div className="grid md:grid-cols-2 gap-4">
        {trackers.map((t) => (
          <Link key={t.href} href={t.href}
            className={`p-6 rounded-2xl ${t.color} card-hover border border-transparent hover:border-gray-200`}>
            <div className="text-3xl mb-3">{t.icon}</div>
            <h3 className="font-semibold">{t.label}</h3>
            <p className="text-sm mt-1 opacity-75">{t.desc}</p>
          </Link>
        ))}
      </div>
    </div>
  );
}
