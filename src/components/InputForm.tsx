import { useState } from 'react';
import { locateCaller } from '../api/locate';
import type { FusedLocation } from '../types';

interface InputFormProps {
  onLocationResolved: (data: FusedLocation | null) => void;
}

export default function InputForm({ onLocationResolved }: InputFormProps) {
  const [callerText, setCallerText] = useState('Help, I was in a hit and run! I think I am near the big bridge by the park, not sure what street.');
  const [gps, setGps] = useState('13.0827, 80.2707');
  const [w3w, setW3w] = useState('apples.bridges.cats');
  const [address, setAddress] = useState('Main St & 4th Ave');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    onLocationResolved(null); 

    const payload = {
      caller_text: callerText,
      signals: [
        { type: 'GPS', data: gps },
        { type: 'W3W', data: w3w },
        { type: 'ADDRESS', data: address }
      ].filter(s => s.data.trim() !== '')
    };

    try {
      const result = await locateCaller(payload);
      onLocationResolved(result);
    } catch (err: any) {
      setError(err.message || 'An error occurred while fusing locations.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex flex-col h-full gap-5">
      <div className="mb-2">
        <h3 className="text-xl font-black text-white tracking-tight flex items-center gap-2">
           Incident Ingestion
        </h3>
        <p className="text-xs text-slate-400 mt-1 font-medium leading-relaxed">Multimodal signal fusion engine input.</p>
      </div>

      {error && (
        <div className="bg-rose-950/50 text-rose-400 text-xs p-4 rounded-2xl border border-rose-900/50 font-bold leading-relaxed shadow-sm transition-all animate-in fade-in slide-in-from-top-2">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-5 flex-grow">
        
        <div className="flex flex-col gap-2 lg:col-span-1">
          <label className="text-[10px] uppercase font-black tracking-widest text-slate-500">Caller Transcript</label>
          <textarea 
            rows={3}
            value={callerText}
            onChange={e => setCallerText(e.target.value)}
            placeholder="What is the caller saying?"
            className="w-full h-full bg-slate-800/50 border border-slate-700/50 rounded-2xl p-4 text-sm text-slate-200 shadow-inner focus:bg-slate-800 focus:outline-none focus:border-indigo-500 focus:ring-4 focus:ring-indigo-900/50 transition-all duration-300 placeholder:text-slate-600 resize-none font-medium hover:border-slate-600"
          />
        </div>

        <div className="flex flex-col gap-5 lg:col-span-3">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            <div className="flex flex-col gap-2">
              <label className="text-[10px] uppercase font-black tracking-widest text-slate-500">Raw GPS</label>
              <input 
                type="text"
                value={gps}
                onChange={e => setGps(e.target.value)}
                placeholder="lat, lon"
                className="w-full bg-slate-800/50 border border-slate-700/50 rounded-2xl p-4 text-sm font-mono text-slate-300 shadow-inner focus:bg-slate-800 focus:outline-none focus:border-indigo-500 focus:ring-4 focus:ring-indigo-900/50 transition-all duration-300 placeholder:text-slate-600 hover:border-slate-600"
              />
            </div>
            <div className="flex flex-col gap-2">
              <label className="text-[10px] uppercase font-black tracking-widest text-slate-500">What3Words</label>
              <input 
                type="text"
                value={w3w}
                onChange={e => setW3w(e.target.value)}
                placeholder="word.word.word"
                className="w-full bg-slate-800/50 border border-slate-700/50 rounded-2xl p-4 text-sm font-mono text-slate-300 shadow-inner focus:bg-slate-800 focus:outline-none focus:border-indigo-500 focus:ring-4 focus:ring-indigo-900/50 transition-all duration-300 placeholder:text-slate-600 hover:border-slate-600"
              />
            </div>
            <div className="flex flex-col gap-2">
              <label className="text-[10px] uppercase font-black tracking-widest text-slate-500">Address String</label>
              <input 
                type="text"
                value={address}
                onChange={e => setAddress(e.target.value)}
                placeholder="Street Address"
                className="w-full bg-slate-800/50 border border-slate-700/50 rounded-2xl p-4 text-sm text-slate-200 shadow-inner font-medium focus:bg-slate-800 focus:outline-none focus:border-indigo-500 focus:ring-4 focus:ring-indigo-900/50 transition-all duration-300 placeholder:text-slate-600 hover:border-slate-600"
              />
            </div>
          </div>

          <button 
            type="submit" 
            disabled={isLoading}
            className="mt-auto w-full bg-indigo-600 hover:bg-indigo-500 text-white font-black py-4 rounded-2xl shadow-[0_8px_30px_rgb(79,70,229,0.15)] hover:shadow-[0_8px_30px_rgb(79,70,229,0.3)] hover:-translate-y-0.5 disabled:bg-indigo-900/50 disabled:text-indigo-500/50 disabled:shadow-none disabled:translate-y-0 disabled:cursor-wait transition-all duration-300 uppercase tracking-[0.2em] text-xs flex justify-center items-center gap-3"
          >
            {isLoading ? (
              <>
                <svg className="animate-spin h-5 w-5 text-indigo-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Fusing Signals...
              </>
            ) : (
              'Initiate Localization'
            )}
          </button>
        </div>
      </div>
    </form>
  );
}
