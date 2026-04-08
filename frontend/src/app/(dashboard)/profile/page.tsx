'use client';

import { useState, useEffect } from 'react';
import { apiFetch } from '@/lib/api-client';
import { PERSONAS } from '@/lib/constants';

interface UserProfile {
  id: string;
  email: string;
  full_name: string;
  age_group: string;
  persona: string;
  role: string;
  emergency_contact: string | null;
  date_of_birth: string | null;
  created_at: string;
}

export default function ProfilePage() {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [editing, setEditing] = useState(false);
  const [name, setName] = useState('');
  const [emergencyContact, setEmergencyContact] = useState('');
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    apiFetch<UserProfile>('/api/v1/users/me').then((u) => {
      setUser(u);
      setName(u.full_name);
      setEmergencyContact(u.emergency_contact || '');
    }).catch(() => {});
  }, []);

  const save = async () => {
    setSaving(true);
    try {
      const updated = await apiFetch<UserProfile>('/api/v1/users/me', {
        method: 'PATCH',
        body: JSON.stringify({ full_name: name, emergency_contact: emergencyContact || null }),
      });
      setUser(updated);
      setEditing(false);
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch {
      // ignore
    }
    setSaving(false);
  };

  if (!user) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-600" />
      </div>
    );
  }

  const persona = PERSONAS[user.persona as keyof typeof PERSONAS];

  return (
    <div className="space-y-6 max-w-lg mx-auto">
      <h2 className="text-2xl font-bold text-gray-800">Profile</h2>

      {saved && <div className="p-3 bg-emerald-50 text-emerald-700 rounded-xl text-sm">Profile updated!</div>}

      {/* Persona Card */}
      {persona && (
        <div className="rounded-2xl p-5 text-center" style={{ backgroundColor: persona.bg, color: persona.text }}>
          <p className="text-3xl mb-2">{persona.name === 'ManoMitra' ? '🌟' : persona.name === 'ManoSpark' ? '✨' : persona.name === 'ManoSaathi' ? '🤝' : '🌿'}</p>
          <h3 className="text-lg font-bold">{persona.name}</h3>
          <p className="text-sm opacity-75">{persona.description}</p>
          <p className="text-xs mt-1 opacity-60">Age Range: {persona.ageRange}</p>
        </div>
      )}

      {/* User Info */}
      <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100 space-y-4">
        {editing ? (
          <>
            <div>
              <label className="block text-sm font-medium text-gray-600 mb-1">Full Name</label>
              <input value={name} onChange={(e) => setName(e.target.value)}
                className="w-full p-3 rounded-xl border border-gray-200 focus:border-emerald-400 focus:ring-2 focus:ring-emerald-100 outline-none transition" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-600 mb-1">Emergency Contact</label>
              <input value={emergencyContact} onChange={(e) => setEmergencyContact(e.target.value)}
                placeholder="Phone number or email"
                className="w-full p-3 rounded-xl border border-gray-200 focus:border-emerald-400 focus:ring-2 focus:ring-emerald-100 outline-none transition" />
            </div>
            <div className="flex gap-3">
              <button onClick={() => setEditing(false)}
                className="flex-1 py-2.5 border border-gray-200 rounded-xl text-gray-600 hover:bg-gray-50 transition text-sm">
                Cancel
              </button>
              <button onClick={save} disabled={saving}
                className="flex-1 py-2.5 bg-emerald-600 text-white rounded-xl hover:bg-emerald-700 transition text-sm font-medium disabled:opacity-50">
                {saving ? 'Saving...' : 'Save'}
              </button>
            </div>
          </>
        ) : (
          <>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-500">Name</span>
              <span className="font-medium text-gray-800">{user.full_name}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-500">Email</span>
              <span className="font-medium text-gray-800">{user.email}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-500">Role</span>
              <span className="font-medium text-gray-800 capitalize">{user.role}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-500">Age Group</span>
              <span className="font-medium text-gray-800">{user.age_group.replace(/_/g, ' ')}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-500">Emergency Contact</span>
              <span className="font-medium text-gray-800">{user.emergency_contact || 'Not set'}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-500">Member Since</span>
              <span className="font-medium text-gray-800">{new Date(user.created_at).toLocaleDateString()}</span>
            </div>
            <button onClick={() => setEditing(true)}
              className="w-full py-2.5 bg-emerald-600 text-white rounded-xl hover:bg-emerald-700 transition text-sm font-medium mt-2">
              Edit Profile
            </button>
          </>
        )}
      </div>
    </div>
  );
}
