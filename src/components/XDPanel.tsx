import type { FusedLocation } from '../types';

interface XDPanelProps {
  fusedLocation: FusedLocation | null;
}

export default function XDPanel({ fusedLocation }: XDPanelProps) {
  if (!fusedLocation) {
    // Removed the confusing infinite spinning loader here! It is now a calm idle state.
    return (
      <div className="md:w-[420px] bg-slate-900 flex flex-col items-center justify-center p-8 text-center text-slate-600 transition-all duration-500 h-full">
        <svg className="w-16 h-16 mb-4 text-slate-800" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <p className="font-semibold text-sm tracking-wide uppercase">System Idle</p>
        <p className="text-xs mt-2 text-slate-500">Awaiting incident data stream...</p>
      </div>
    );
  }

  const score = fusedLocation.confidence_score;
  let barColor = 'bg-rose-500 shadow-rose-500/50';
  if (score >= 80) barColor = 'bg-emerald-500 shadow-emerald-500/50';
  else if (score >= 50) barColor = 'bg-amber-400 shadow-amber-400/50';

  const getIgnoredReason = (sourceName: string) => {
    const signal = fusedLocation.input_signals.find(s => s.source === sourceName && s.is_outlier);
    return signal?.outlier_reason || 'Rejected by fusion logic core';
  };

  return (
    <div className="md:w-[420px] min-w-[24rem] h-full bg-slate-900 flex flex-col overflow-y-auto transition-all duration-500 ease-in-out text-slate-200">
      {/* Header Panel */}
      <div className="p-8 bg-slate-800/30 border-b border-slate-800 shrink-0 shadow-sm relative z-10">
        <h3 className="text-lg font-black tracking-tight text-white flex items-center gap-2 mb-8">
          <svg className="w-5 h-5 text-indigo-400 drop-shadow-sm" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
          </svg>
          Decision Explainability
        </h3>

        <div className="mb-3 flex justify-between items-end">
          <span className="text-xs font-black uppercase tracking-widest text-slate-500">Confidence</span>
          <span className="text-4xl font-black text-white leading-none tracking-tighter drop-shadow-sm">{score}%</span>
        </div>
        <div className="w-full bg-slate-800 rounded-full h-3 overflow-hidden shadow-inner flex">
          <div className={`${barColor} h-3 rounded-full transition-all duration-1000 ease-out shadow-[0_0_8px_rgba(0,0,0,0.5)]`} style={{ width: `${score}%` }}></div>
        </div>
      </div>

      <div className="p-8 space-y-10 flex-grow">
        
        {/* Rationale */}
        <section>
          <span className="text-[10px] font-black uppercase text-slate-500 tracking-[0.2em] mb-4 block">Primary Rationale</span>
          <div className="bg-gradient-to-br from-indigo-950/50 to-slate-800/30 border border-indigo-900/50 p-6 rounded-2xl text-indigo-100 text-sm font-semibold leading-relaxed shadow-sm transition-all hover:shadow-md hover:border-indigo-800">
            {fusedLocation.explanation}
          </div>
        </section>

        {/* Aggregated Sources */}
        {fusedLocation.sources_used.length > 0 && (
          <section>
            <span className="text-[10px] font-black uppercase text-emerald-500/70 tracking-[0.2em] mb-4 block">Aggregated Sources</span>
            <ul className="flex flex-col gap-3">
              {fusedLocation.sources_used.map(src => (
                <li key={src} className="group flex items-center gap-4 bg-slate-800/40 p-4 border border-slate-700/50 rounded-2xl shadow-sm hover:shadow-md hover:border-slate-700 hover:-translate-y-0.5 transition-all duration-300">
                  <div className="bg-emerald-950/50 p-2 rounded-full flex-shrink-0 text-emerald-400 shadow-sm group-hover:scale-110 transition-transform">
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <span className="text-sm font-bold tracking-wide text-slate-300 uppercase">{src}</span>
                </li>
              ))}
            </ul>
          </section>
        )}

        {/* Rejected Signals */}
        {fusedLocation.sources_ignored.length > 0 && (
          <section>
            <span className="text-[10px] font-black uppercase text-rose-500/70 tracking-[0.2em] mb-4 block">Rejected Signals</span>
            <ul className="flex flex-col gap-4">
              {fusedLocation.sources_ignored.map(src => (
                <li key={src} className="flex flex-col bg-slate-800/40 p-4 border border-slate-700/50 rounded-2xl shadow-sm hover:shadow-md hover:border-slate-700 hover:-translate-y-0.5 transition-all duration-300 relative overflow-hidden group">
                  <div className="absolute top-0 left-0 w-1.5 h-full bg-rose-900/50 group-hover:bg-rose-600 transition-colors"></div>
                  <div className="flex items-center gap-3 mb-3 pl-2">
                    <div className="bg-rose-950/50 p-1.5 rounded-full flex-shrink-0 text-rose-500 shadow-sm group-hover:scale-110 transition-transform">
                      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </div>
                    <span className="text-sm font-bold tracking-wide text-white uppercase">{src}</span>
                  </div>
                  <div className="pl-12 text-xs font-semibold text-rose-400 leading-relaxed group-hover:text-rose-300 transition-colors">
                    ↳ {getIgnoredReason(src)}
                  </div>
                </li>
              ))}
            </ul>
          </section>
        )}
      </div>
    </div>
  );
}
