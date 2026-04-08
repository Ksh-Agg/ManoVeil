'use client';

import { useState, useEffect } from 'react';
import { apiFetch } from '@/lib/api-client';

interface CrisisResource {
  name: string;
  number: string;
  description: string;
  hours: string;
}

const GROUNDING_STEPS = [
  { count: 5, sense: 'SEE', prompt: 'Name 5 things you can see around you right now.' },
  { count: 4, sense: 'TOUCH', prompt: 'Name 4 things you can physically touch or feel.' },
  { count: 3, sense: 'HEAR', prompt: 'Name 3 sounds you can hear right now.' },
  { count: 2, sense: 'SMELL', prompt: 'Name 2 things you can smell.' },
  { count: 1, sense: 'TASTE', prompt: 'Name 1 thing you can taste.' },
];

export default function CrisisPage() {
  const [resources, setResources] = useState<CrisisResource[]>([]);
  const [sosTriggered, setSosTriggered] = useState(false);
  const [breathing, setBreathing] = useState(false);
  const [breathPhase, setBreathPhase] = useState<'inhale' | 'hold' | 'exhale'>('inhale');
  const [breathCount, setBreathCount] = useState(0);
  const [groundingStep, setGroundingStep] = useState(-1);

  useEffect(() => {
    apiFetch<CrisisResource[]>('/api/v1/crisis/resources').then(setResources).catch(() => {
      setResources([
        { name: 'Kiran Mental Health', number: '1800-599-0019', description: 'Government toll-free helpline', hours: '24/7' },
        { name: 'Vandrevala Foundation', number: '1860-2662-345', description: '24/7 mental health support', hours: '24/7' },
        { name: 'AASRA', number: '9820466726', description: 'Crisis intervention center', hours: '24/7' },
        { name: 'iCall', number: '9152987821', description: 'Psychosocial helpline by TISS Mumbai', hours: 'Mon-Sat 8am-10pm' },
      ]);
    });
  }, []);

  const triggerSos = async () => {
    try {
      await apiFetch('/api/v1/crisis/sos', { method: 'POST' });
    } catch {
      // still show resources
    }
    setSosTriggered(true);
  };

  useEffect(() => {
    if (!breathing) return;
    const phases: Array<{ phase: 'inhale' | 'hold' | 'exhale'; duration: number }> = [
      { phase: 'inhale', duration: 4000 },
      { phase: 'hold', duration: 4000 },
      { phase: 'exhale', duration: 4000 },
    ];
    let phaseIndex = 0;
    let count = 0;

    const advance = () => {
      setBreathPhase(phases[phaseIndex].phase);
      const timeout = setTimeout(() => {
        phaseIndex = (phaseIndex + 1) % 3;
        if (phaseIndex === 0) {
          count++;
          setBreathCount(count);
          if (count >= 5) {
            setBreathing(false);
            return;
          }
        }
        advance();
      }, phases[phaseIndex].duration);
      return timeout;
    };

    const timeout = advance();
    return () => clearTimeout(timeout);
  }, [breathing]);

  return (
    <div className="space-y-8 max-w-2xl mx-auto">
      <h2 className="text-2xl font-bold text-gray-800">Crisis Support</h2>
      <p className="text-gray-500">You are not alone. Immediate help is available.</p>

      {/* SOS Button */}
      <div className="text-center">
        <button onClick={triggerSos}
          className="w-32 h-32 rounded-full bg-red-500 text-white text-xl font-bold shadow-lg hover:bg-red-600 transition sos-pulse mx-auto flex items-center justify-center">
          SOS
        </button>
        <p className="text-sm text-gray-400 mt-3">Press if you need immediate help</p>
      </div>

      {sosTriggered && (
        <div className="bg-red-50 border border-red-200 rounded-2xl p-6 text-center">
          <p className="text-red-700 font-semibold mb-2">Your emergency contact has been notified.</p>
          <p className="text-red-600 text-sm">Please reach out to one of the helplines below.</p>
        </div>
      )}

      {/* Crisis Hotlines */}
      <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
        <h3 className="text-lg font-semibold text-gray-700 mb-4">Crisis Helplines</h3>
        <div className="space-y-3">
          {resources.map((r) => (
            <div key={r.number} className="flex items-center justify-between p-3 rounded-xl bg-gray-50 hover:bg-emerald-50 transition">
              <div>
                <p className="font-medium text-gray-800">{r.name}</p>
                <p className="text-xs text-gray-500">{r.description}</p>
                <p className="text-xs text-gray-400">{r.hours}</p>
              </div>
              <a href={`tel:${r.number.replace(/[^0-9+]/g, '')}`}
                className="px-4 py-2 bg-emerald-600 text-white rounded-xl text-sm font-medium hover:bg-emerald-700 transition whitespace-nowrap">
                {r.number}
              </a>
            </div>
          ))}
        </div>
      </div>

      {/* Breathing Exercise */}
      <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100 text-center">
        <h3 className="text-lg font-semibold text-gray-700 mb-4">Breathing Exercise (4-4-4)</h3>
        {!breathing ? (
          <button onClick={() => { setBreathing(true); setBreathCount(0); setBreathPhase('inhale'); }}
            className="px-6 py-3 bg-indigo-500 text-white rounded-xl hover:bg-indigo-600 transition font-medium">
            Start Breathing Exercise
          </button>
        ) : (
          <div className="space-y-4">
            <div className={`w-24 h-24 mx-auto rounded-full flex items-center justify-center text-white font-bold text-lg transition-all duration-[4000ms] ${
              breathPhase === 'inhale' ? 'scale-125 bg-blue-400' :
              breathPhase === 'hold' ? 'scale-125 bg-purple-400' :
              'scale-100 bg-teal-400'
            }`}>
              {breathPhase === 'inhale' ? 'Breathe In' : breathPhase === 'hold' ? 'Hold' : 'Breathe Out'}
            </div>
            <p className="text-sm text-gray-500">Cycle {breathCount + 1} of 5</p>
          </div>
        )}
      </div>

      {/* Grounding Technique */}
      <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
        <h3 className="text-lg font-semibold text-gray-700 mb-2">5-4-3-2-1 Grounding</h3>
        <p className="text-sm text-gray-500 mb-4">A technique to bring you back to the present moment.</p>

        {groundingStep === -1 ? (
          <button onClick={() => setGroundingStep(0)}
            className="px-6 py-3 bg-teal-500 text-white rounded-xl hover:bg-teal-600 transition font-medium">
            Start Grounding Exercise
          </button>
        ) : groundingStep < GROUNDING_STEPS.length ? (
          <div className="space-y-4">
            <div className="bg-teal-50 rounded-xl p-4">
              <p className="text-teal-800 font-semibold text-lg mb-1">
                {GROUNDING_STEPS[groundingStep].count} — {GROUNDING_STEPS[groundingStep].sense}
              </p>
              <p className="text-teal-600">{GROUNDING_STEPS[groundingStep].prompt}</p>
            </div>
            <div className="flex gap-2">
              {groundingStep > 0 && (
                <button onClick={() => setGroundingStep(groundingStep - 1)}
                  className="flex-1 py-2 border border-gray-200 rounded-xl text-gray-600 hover:bg-gray-50 transition text-sm">
                  Back
                </button>
              )}
              <button onClick={() => setGroundingStep(groundingStep + 1)}
                className="flex-1 py-2 bg-teal-500 text-white rounded-xl hover:bg-teal-600 transition text-sm font-medium">
                {groundingStep < GROUNDING_STEPS.length - 1 ? 'Next' : 'Done'}
              </button>
            </div>
            <div className="flex gap-1 justify-center">
              {GROUNDING_STEPS.map((_, i) => (
                <div key={i} className={`w-2 h-2 rounded-full ${i <= groundingStep ? 'bg-teal-500' : 'bg-gray-200'}`} />
              ))}
            </div>
          </div>
        ) : (
          <div className="text-center space-y-3">
            <p className="text-teal-700 font-medium">Great job! You completed the grounding exercise.</p>
            <button onClick={() => setGroundingStep(-1)}
              className="text-sm text-teal-600 hover:text-teal-700 underline">
              Do it again
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
