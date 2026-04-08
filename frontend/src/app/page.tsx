'use client';

import Link from 'next/link';

const features = [
  { title: 'Age-Adaptive Support', desc: 'Tailored mental health support for every life stage — children to seniors', icon: '🌱' },
  { title: 'AI-Powered Assessment', desc: 'Clinically validated instruments (DASS-21, GAD-7, PHQ-9) with intelligent scoring', icon: '🧠' },
  { title: 'Conversational Companion', desc: 'Empathetic chatbot with CBT techniques, adapted to your persona', icon: '💬' },
  { title: 'Privacy-First Architecture', desc: 'Blockchain-anchored federated learning — your data never leaves your device', icon: '🔒' },
  { title: 'Real-Time Crisis Support', desc: 'Immediate escalation to verified helplines when you need it most', icon: '🆘' },
  { title: 'Clinical Dashboard', desc: 'Therapist tools for patient timeline, AI summaries, and collaborative notes', icon: '📊' },
];

const personas = [
  { name: 'ManoMitra', age: '5-12', color: 'bg-amber-100 text-amber-800 border-amber-300' },
  { name: 'ManoSpark', age: '13-17', color: 'bg-pink-100 text-pink-800 border-pink-300' },
  { name: 'ManoVeil Core', age: '18-24', color: 'bg-emerald-100 text-emerald-800 border-emerald-300' },
  { name: 'ManoBalance', age: '25-59', color: 'bg-blue-100 text-blue-800 border-blue-300' },
  { name: 'ManoSaathi', age: '60+', color: 'bg-violet-100 text-violet-800 border-violet-300' },
  { name: 'ManoConnect', age: 'Clinical', color: 'bg-teal-100 text-teal-800 border-teal-300' },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-soothing">
      {/* Header */}
      <header className="py-6 px-8 flex justify-between items-center max-w-7xl mx-auto">
        <h1 className="text-2xl font-bold bg-gradient-to-r from-emerald-600 to-teal-600 bg-clip-text text-transparent">
          ManoVeil
        </h1>
        <div className="flex gap-4">
          <Link href="/login" className="px-6 py-2 text-emerald-700 hover:text-emerald-900 transition">
            Sign In
          </Link>
          <Link href="/register" className="px-6 py-2 bg-emerald-600 text-white rounded-2xl hover:bg-emerald-700 transition shadow-md">
            Get Started
          </Link>
        </div>
      </header>

      {/* Hero */}
      <section className="py-20 px-8 text-center max-w-4xl mx-auto">
        <h2 className="text-5xl font-bold text-gray-900 leading-tight mb-6">
          Unveiling the Mind,<br />
          <span className="bg-gradient-to-r from-emerald-500 to-teal-500 bg-clip-text text-transparent">
            One Gentle Step at a Time
          </span>
        </h2>
        <p className="text-xl text-gray-600 mb-10 max-w-2xl mx-auto leading-relaxed">
          A universal, lifespan-aware mental health intelligence platform.
          Clinically validated assessments, empathetic AI companions, and
          privacy-first technology — for everyone, at every age.
        </p>
        <Link href="/register" className="inline-block px-10 py-4 bg-emerald-600 text-white text-lg rounded-3xl hover:bg-emerald-700 transition shadow-lg hover:shadow-xl">
          Start Your Journey
        </Link>
      </section>

      {/* Personas */}
      <section className="py-16 px-8 max-w-6xl mx-auto">
        <h3 className="text-3xl font-bold text-center mb-12 text-gray-800">For Every Stage of Life</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {personas.map((p) => (
            <div key={p.name} className={`p-4 rounded-2xl border-2 text-center card-hover ${p.color}`}>
              <div className="text-sm font-semibold">{p.name}</div>
              <div className="text-xs mt-1 opacity-75">{p.age}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section className="py-16 px-8 max-w-6xl mx-auto">
        <h3 className="text-3xl font-bold text-center mb-12 text-gray-800">How ManoVeil Helps</h3>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((f) => (
            <div key={f.title} className="bg-white/80 backdrop-blur p-8 rounded-3xl shadow-sm border border-gray-100 card-hover">
              <div className="text-4xl mb-4">{f.icon}</div>
              <h4 className="text-lg font-semibold text-gray-800 mb-2">{f.title}</h4>
              <p className="text-gray-600 text-sm leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 px-8 text-center text-gray-500 text-sm border-t border-gray-200 mt-16">
        <p>ManoVeil — Unveiling the Mind. Built with care for mental health accessibility.</p>
        <p className="mt-2">Crisis? Call Kiran Mental Health: 1800-599-0019 (24/7, toll-free)</p>
      </footer>
    </div>
  );
}
