import type { FusedLocation } from '../types';

interface StatusBannerProps {
  fusedLocation: FusedLocation | null;
}

export default function StatusBanner({ fusedLocation }: StatusBannerProps) {
  if (!fusedLocation) return null;

  const status = fusedLocation.dispatch_status;

  let bgColor = 'bg-slate-800';
  let textColor = 'text-white';
  let title = 'WAITING FOR DATA';

  if (status === 'GREEN') {
    bgColor = 'bg-emerald-500';
    title = 'DISPATCH NOW — High confidence location';
  } else if (status === 'YELLOW') {
    bgColor = 'bg-amber-400';
    textColor = 'text-amber-950';
    title = 'VERIFY WITH CALLER — Conflict detected';
  } else if (status === 'RED') {
    bgColor = 'bg-rose-600';
    title = 'SEARCH ZONE — High uncertainty';
  }

  return (
    <div className={`w-full ${bgColor} ${textColor} py-4 px-8 shadow-md transition-all duration-700 ease-in-out z-20`}>
      <div className="max-w-[1920px] mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
        <h2 className="text-xl md:text-2xl font-black uppercase tracking-widest drop-shadow-sm">
          {title}
        </h2>
        
        {fusedLocation.followup_question && (
          <div className="bg-white/10 px-6 py-3 rounded-2xl border border-white/20 shadow-sm backdrop-blur-md text-sm md:text-base font-bold max-w-lg transition-all hover:bg-white/20 hover:scale-[1.02] cursor-default">
            <span className="opacity-80 uppercase text-[10px] tracking-widest block mb-1 font-black">Suggested Question</span>
            <span className="drop-shadow-sm leading-relaxed">{fusedLocation.followup_question}</span>
          </div>
        )}
      </div>
    </div>
  );
}
