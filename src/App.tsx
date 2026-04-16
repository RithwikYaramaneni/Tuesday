import { useState } from 'react';
import MapView from './components/MapView';
import StatusBanner from './components/StatusBanner';
import XDPanel from './components/XDPanel';
import InputForm from './components/InputForm';
import type { FusedLocation } from './types';

function App() {
  const [fusedData, setFusedData] = useState<FusedLocation | null>(null);

  return (
    <div className="h-screen bg-slate-950 flex flex-col font-sans overflow-hidden text-slate-200">
      
      {/* 1. TOP: StatusBanner */}
      <div className="flex-shrink-0 z-20 shadow-[0_8px_30px_rgb(0,0,0,0.5)]">
        <StatusBanner fusedLocation={fusedData} />
      </div>
      
      {/* Main Glassy Grid Layout */}
      <div className="flex-grow flex flex-col lg:flex-row p-4 md:p-6 gap-6 overflow-hidden max-w-[1920px] mx-auto w-full transition-all duration-500">
        
        {/* LEFT COLUMN: Map & Input */}
        <div className="flex flex-col gap-6 flex-grow w-full min-w-0">
          
          {/* MAP */}
          <div className="flex-grow bg-slate-900 rounded-[2rem] shadow-[0_8px_30px_rgb(0,0,0,0.4)] border border-slate-800 overflow-hidden relative min-h-[300px] z-0 transition-all hover:shadow-[0_8px_30px_rgb(0,0,0,0.6)] duration-500 group">
            <MapView fusedLocation={fusedData} />
          </div>

          {/* BOTTOM: Input Form */}
          <div className="bg-slate-900 rounded-[2rem] shadow-[0_8px_30px_rgb(0,0,0,0.4)] border border-slate-800 p-6 flex-shrink-0 xl:h-[300px] overflow-y-auto transition-all hover:shadow-[0_8px_30px_rgb(0,0,0,0.6)] duration-500 scrollbar-hide">
             <InputForm onLocationResolved={setFusedData} />
          </div>
          
        </div>

        {/* RIGHT COLUMN: XDPanel */}
        <div className="w-full lg:w-[420px] flex-shrink-0 bg-slate-900 rounded-[2rem] shadow-[0_8px_30px_rgb(0,0,0,0.4)] border border-slate-800 overflow-hidden flex flex-col z-10 transition-all hover:shadow-[0_8px_30px_rgb(0,0,0,0.6)] duration-500">
          <XDPanel fusedLocation={fusedData} />
        </div>
        
      </div>
    </div>
  );
}

export default App;
