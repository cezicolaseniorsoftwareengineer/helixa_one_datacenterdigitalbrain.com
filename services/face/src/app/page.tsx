'use client';

import React, { useEffect, useState } from 'react';
import Image from 'next/image';
import { Activity, Zap, Thermometer, ShieldCheck, Cpu, Menu, X, ChevronRight, Settings, BarChart3 } from 'lucide-react';
import { supabase } from '@/lib/supabase';
import dynamic from 'next/dynamic';

const DigitalTwin = dynamic(() => import('@/components/DigitalTwin'), { 
  ssr: false,
  loading: () => (
    <div className="flex flex-col items-center justify-center space-y-4">
      <div className="w-12 h-12 border-4 border-accent border-t-transparent rounded-full animate-spin" />
      <p className="text-xs font-mono text-accent animate-pulse">INITIALIZING DIGITAL TWIN ENGINE...</p>
    </div>
  )
});

const NIcon = ({ onClick, isOpen }: { onClick: () => void, isOpen: boolean }) => (
  <button 
    onClick={onClick}
    className="relative group flex items-center justify-center w-12 h-12 rounded-full bg-black border border-white/20 hover:border-accent/50 transition-all duration-300 shadow-[0_0_18px_rgba(0,0,0,0.5)] active:scale-95 z-50"
  >
    <div className={`absolute inset-0 rounded-full bg-accent/5 group-hover:bg-accent/10 transition-colors ${isOpen ? 'bg-accent/20' : ''}`} />
    <div className="relative w-8 h-8 rounded-full overflow-hidden">
      <Image
        src="/img.helixa_one.png"
        alt="Helixa One logo"
        width={720}
        height={720}
        className="absolute inset-0 m-auto object-contain"
        style={{ width: '400%', height: '400%' }}
        aria-hidden={false}
        priority
      />
    </div>
    {isOpen && <div className="absolute -right-1 -top-1 w-3 h-3 bg-accent rounded-full border-2 border-black animate-pulse" />}
  </button>
);

export default function Dashboard() {
  const [latestTelemetry, setLatestTelemetry] = useState<any[]>([]);
  const [pue, setPue] = useState(1.12);
  const [temp, setTemp] = useState(24.5);
  const [currentTime, setCurrentTime] = useState<Date | null>(null);
  const [mode, setMode] = useState<'pc' | 'notebook' | 'datacenter'>('datacenter');
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    setCurrentTime(new Date());
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    // Subscribe to real-time telemetry updates
    const channel = supabase
      .channel('telemetry_updates')
      .on('postgres_changes', { event: 'INSERT', schema: 'public', table: 'telemetry' }, (payload) => {
        const newData = payload.new;
        setLatestTelemetry((prev) => [newData, ...prev].slice(0, 10));
        
        // Auto-detect mode from metadata if available
        if (newData.metadata?.device_type) {
          setMode(newData.metadata.device_type);
        }
        
        if (newData.type === 'temperature') setTemp(newData.value);
        if (newData.type === 'power') {
            // Simple PUE simulation based on power load
            const newPue = 1.0 + (newData.value / 100);
            setPue(parseFloat(newPue.toFixed(2)));
        }
      })
      .subscribe();

    return () => {
      clearInterval(timer);
      supabase.removeChannel(channel);
    };
  }, []);

  return (
    <main className="min-h-full w-full bg-background text-foreground flex flex-col relative font-sans pb-24">
      {/* Retractable Sidebar Menu */}
      <div 
        className={`fixed top-0 left-0 h-full w-72 bg-black/98 backdrop-blur-2xl border-r border-white/10 z-[60] transition-transform duration-500 ease-out shadow-[20px_0_50px_rgba(0,0,0,0.8)] ${
          isMenuOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="p-8 space-y-10">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-accent/10 flex items-center justify-center border border-accent/30 shadow-[0_0_15px_rgba(6,182,212,0.2)]">
                <span className="text-accent font-black text-xl">N</span>
              </div>
              <div>
                <span className="block text-[10px] font-black tracking-[0.3em] text-accent/40 uppercase">Navigation</span>
                <span className="block text-xs font-bold text-foreground/80">CONTROL CENTER</span>
              </div>
            </div>
            <button 
              onClick={() => setIsMenuOpen(false)}
              className="p-2 hover:bg-white/5 rounded-lg transition-colors group"
            >
              <X className="w-5 h-5 text-foreground/40 group-hover:text-accent transition-colors" />
            </button>
          </div>

          <nav className="space-y-6">
            <section>
              <h3 className="text-[9px] font-black text-foreground/20 uppercase tracking-[0.4em] mb-4 ml-1">System Environment</h3>
              <div className="space-y-2">
                {(['notebook', 'pc', 'datacenter'] as const).map((m) => (
                  <button
                    key={m}
                    onClick={() => { setMode(m); setIsMenuOpen(false); }}
                    className={`w-full flex items-center justify-between px-5 py-4 rounded-xl border transition-all duration-300 ${
                      mode === m 
                        ? 'bg-accent/10 border-accent/40 text-accent shadow-[0_0_20px_rgba(6,182,212,0.1)]' 
                        : 'bg-white/[0.02] border-white/5 text-foreground/40 hover:bg-white/[0.05] hover:border-white/10'
                    }`}
                  >
                    <span className="text-[11px] font-black uppercase tracking-widest">{m}</span>
                    {mode === m ? <div className="w-1.5 h-1.5 rounded-full bg-accent animate-pulse" /> : <ChevronRight className="w-4 h-4 opacity-20" />}
                  </button>
                ))}
              </div>
            </section>

            <section>
              <h3 className="text-[9px] font-black text-foreground/20 uppercase tracking-[0.4em] mb-4 ml-1">Operations</h3>
              <div className="grid grid-cols-2 gap-3">
                <button className="p-4 bg-white/[0.02] rounded-xl border border-white/5 hover:border-accent/30 hover:bg-accent/5 transition-all group flex flex-col items-center gap-2">
                  <Settings className="w-5 h-5 text-foreground/20 group-hover:text-accent transition-colors" />
                  <span className="text-[9px] font-black uppercase tracking-tighter">Settings</span>
                </button>
                <button className="p-4 bg-white/[0.02] rounded-xl border border-white/5 hover:border-accent/30 hover:bg-accent/5 transition-all group flex flex-col items-center gap-2">
                  <BarChart3 className="w-5 h-5 text-foreground/20 group-hover:text-accent transition-colors" />
                  <span className="text-[9px] font-black uppercase tracking-tighter">Analytics</span>
                </button>
              </div>
            </section>
          </nav>

          <div className="absolute bottom-10 left-8 right-8">
            <div className="p-5 bg-white/[0.02] rounded-2xl border border-white/5 backdrop-blur-md">
              <div className="flex items-center gap-2 mb-2">
                <div className="w-1.5 h-1.5 rounded-full bg-success animate-pulse" />
                <p className="text-[9px] text-foreground/30 font-black uppercase tracking-widest">System Status</p>
              </div>
              <p className="text-xs font-bold text-foreground/80 mb-1">v2.4.0-STABLE</p>
              <p className="text-[8px] font-mono text-foreground/20">ENCRYPTION: AES-256-GCM</p>
            </div>
          </div>
        </div>
      </div>

      {/* Overlay */}
      {isMenuOpen && (
        <div 
          className="fixed inset-0 bg-black/60 backdrop-blur-md z-[55] transition-opacity duration-500"
          onClick={() => setIsMenuOpen(false)}
        />
      )}

      {/* Header */}
      <header className="px-6 py-5 flex flex-row justify-between items-center border-b border-white/5 bg-black/20 backdrop-blur-md shrink-0 z-50">
        <div className="flex items-center gap-5">
          <NIcon onClick={() => setIsMenuOpen(!isMenuOpen)} isOpen={isMenuOpen} />
          <div className="h-8 w-[1px] bg-white/10 hidden sm:block" />
          <div>
            <h1 className="text-lg md:text-xl font-black tracking-[-0.05em] text-white flex items-center gap-2">
              HELIXA<span className="text-accent">ONE</span>
            </h1>
            <p className="text-[8px] md:text-[9px] text-foreground/30 font-black uppercase tracking-[0.3em] hidden xs:block">Intelligence Interface</p>
          </div>
        </div>
        
        <div className="flex items-center gap-6">
          <div className="hidden lg:flex items-center gap-3 bg-white/[0.03] px-4 py-1.5 rounded-full border border-white/5">
            <div className="w-1.5 h-1.5 bg-success rounded-full shadow-[0_0_8px_#00ff88]" />
            <span className="text-[10px] font-black text-foreground/60 uppercase tracking-widest">Network Secure</span>
          </div>
          <div className="text-right border-l border-white/10 pl-6">
            <p className="text-[10px] font-black text-foreground/40 uppercase tracking-tighter">
              {mounted && currentTime ? currentTime.toLocaleDateString('en-US', { month: 'short', day: '2-digit', year: 'numeric' }) : '--- --, ----'}
            </p>
            <p className="text-[11px] font-mono font-bold text-accent/80">
              {mounted && currentTime ? currentTime.toLocaleTimeString('en-US', { hour12: false }) : '--:--:--'}
            </p>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <div className="flex-1 overflow-y-auto md:overflow-hidden p-4 md:p-6 custom-scrollbar">
        <div className="max-w-[1600px] mx-auto h-full grid grid-cols-1 md:grid-cols-12 gap-4 md:gap-6">
          
          {/* Left Column: Vitals */}
          <div className="col-span-1 md:col-span-3 flex flex-col gap-4 md:gap-6 order-2 md:order-1">
            {/* Power Usage Card */}
            <section className="bg-white/[0.03] p-5 rounded-2xl border border-white/5 backdrop-blur-sm flex flex-col justify-between min-h-[140px]">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2.5">
                  <div className="p-1.5 bg-accent/10 rounded-lg">
                    <Zap className="w-3.5 h-3.5 text-accent" />
                  </div>
                  <h2 className="text-[10px] font-black uppercase tracking-[0.2em] text-foreground/60">Power Usage</h2>
                </div>
                <div className="text-[8px] font-bold text-accent/40 bg-accent/5 px-2 py-0.5 rounded border border-accent/10">LIVE</div>
              </div>
              <div className="space-y-4">
                <div className="flex items-end justify-between">
                  <div>
                    <p className="text-[9px] font-bold text-foreground/30 uppercase mb-1">Current PUE</p>
                    <p className="text-3xl font-mono font-black text-white tracking-tighter">{pue}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-[9px] font-bold text-foreground/30 uppercase mb-1">Efficiency</p>
                    <p className="text-sm font-mono font-bold text-success">{(100/pue).toFixed(1)}%</p>
                  </div>
                </div>
                <div className="relative h-1.5 bg-white/5 rounded-full overflow-hidden">
                  <div 
                    className="absolute inset-y-0 left-0 bg-gradient-to-r from-accent to-accent/40 transition-all duration-1000 ease-out" 
                    style={{ width: `${Math.min(100, (1 / pue) * 100)}%` }} 
                  />
                </div>
              </div>
            </section>

            {/* Thermal Load Card */}
            <section className="bg-white/[0.03] p-5 rounded-2xl border border-white/5 backdrop-blur-sm flex flex-col justify-between min-h-[140px]">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2.5">
                  <div className="p-1.5 bg-danger/10 rounded-lg">
                    <Thermometer className="w-3.5 h-3.5 text-danger" />
                  </div>
                  <h2 className="text-[10px] font-black uppercase tracking-[0.2em] text-foreground/60">Thermal Load</h2>
                </div>
              </div>
              <div className="space-y-4">
                <div className="flex items-end justify-between">
                  <div>
                    <p className="text-[9px] font-bold text-foreground/30 uppercase mb-1">Avg Rack Temp</p>
                    <p className="text-3xl font-mono font-black text-white tracking-tighter">{temp}<span className="text-lg text-danger ml-1">°C</span></p>
                  </div>
                  <div className="flex gap-1 mb-1">
                    {[...Array(6)].map((_, i) => (
                      <div 
                        key={i} 
                        className={`w-1.5 h-3 rounded-full transition-all duration-500 ${
                          i < (temp/10) ? (temp > 28 ? 'bg-danger shadow-[0_0_8px_rgba(255,0,60,0.5)]' : 'bg-accent') : 'bg-white/5'
                        }`} 
                      />
                    ))}
                  </div>
                </div>
                <div className="grid grid-cols-12 gap-1">
                  {[...Array(12)].map((_, i) => (
                    <div key={i} className={`h-1 rounded-full transition-colors duration-700 ${temp > 28 ? 'bg-danger/40' : temp > 24 ? 'bg-yellow-500/40' : 'bg-success/40'}`} />
                  ))}
                </div>
              </div>
            </section>
          </div>

          {/* Center Column: 3D Twin */}
          <div className="col-span-1 md:col-span-6 order-1 md:order-2 min-h-[350px] md:min-h-0">
            <section className="h-full bg-white/[0.02] rounded-3xl border border-white/5 relative overflow-hidden group shadow-inner">
              <div className="absolute top-6 left-6 z-10 flex items-center gap-3">
                <div className="w-2 h-2 bg-accent rounded-full animate-ping" />
                <h2 className="text-[10px] font-black uppercase tracking-[0.3em] text-white/80">Spatial Awareness</h2>
              </div>
              
              <div className="absolute inset-0">
                <DigitalTwin key={mode} temp={temp} mode={mode} />
              </div>

              <div className="absolute bottom-6 left-0 right-0 px-6 z-10 flex justify-between items-end">
                <div className="space-y-1">
                  <p className="text-[8px] font-mono text-white/20 uppercase tracking-widest">Site: DC-ALPHA-01</p>
                  <p className="text-[8px] font-mono text-white/20 uppercase tracking-widest">Node: {mode.toUpperCase()}</p>
                </div>
                <div className="text-right">
                  <p className="text-[8px] font-mono text-accent/40 uppercase tracking-[0.2em] animate-pulse">Streaming Live Data</p>
                </div>
              </div>
            </section>
          </div>

          {/* Right Column: Neural Activity */}
          <div className="col-span-1 md:col-span-3 flex flex-col order-3 min-h-[250px] md:min-h-0">
            <section className="flex-1 bg-white/[0.03] p-5 rounded-2xl border border-white/5 backdrop-blur-sm flex flex-col">
              <div className="flex items-center justify-between mb-5 shrink-0">
                <div className="flex items-center gap-2.5">
                  <div className="p-1.5 bg-success/10 rounded-lg">
                    <ShieldCheck className="w-3.5 h-3.5 text-success" />
                  </div>
                  <h2 className="text-[10px] font-black uppercase tracking-[0.2em] text-foreground/60">Neural Activity</h2>
                </div>
              </div>
              
              <div className="flex-1 font-mono text-[9px] space-y-2.5 overflow-y-auto custom-scrollbar pr-2">
                {latestTelemetry.length === 0 ? (
                  <div className="space-y-2 opacity-40">
                    <p className="text-success/80">&gt;&gt; [OK] Safety Controller: Active</p>
                    <p className="text-accent/80">&gt;&gt; [INFO] Brain: Initializing...</p>
                    <p className="text-white/40">&gt;&gt; [DATA] Awaiting stream...</p>
                  </div>
                ) : (
                  latestTelemetry.map((t, i) => (
                    <div key={i} className="flex gap-2 items-start group">
                      <span className="text-white/20 shrink-0">[{mounted ? new Date(t.created_at || Date.now()).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit', second:'2-digit'}) : '--:--:--'}]</span>
                      <p className={`break-all ${t.value > 30 ? 'text-danger font-bold' : 'text-foreground/70 group-hover:text-foreground transition-colors'}`}>
                        {t.sensor_id}: {t.value}{t.unit}
                      </p>
                    </div>
                  ))
                )}
                <div className="text-accent animate-pulse">_</div>
              </div>

              <div className="mt-6 pt-5 border-t border-white/5 shrink-0">
                <div className="flex justify-between items-end mb-2">
                  <span className="text-[9px] font-black text-foreground/30 uppercase tracking-widest">AI Confidence</span>
                  <span className="text-xs font-mono font-black text-success">98.4%</span>
                </div>
                <div className="h-1 bg-white/5 rounded-full overflow-hidden">
                  <div className="h-full bg-gradient-to-r from-success/40 to-success w-[98%] shadow-[0_0_10px_rgba(0,255,136,0.3)]" />
                </div>
              </div>
            </section>
          </div>
        </div>
      </div>

      {/* Footer Bar */}
      <footer className="px-6 py-4 bg-black/40 border-t border-white/5 backdrop-blur-xl shrink-0 z-50">
        <div className="max-w-[1600px] mx-auto grid grid-cols-2 md:grid-cols-4 gap-4 md:gap-8">
          {[
            { label: 'Active Assets', value: '4,201' },
            { label: 'Network Latency', value: '0.4ms' },
            { label: 'System Uptime', value: '99.9999%' },
            { label: 'AI Decisions/hr', value: '12,450' },
          ].map((stat, i) => (
            <div key={i} className="flex flex-col gap-1">
              <p className="text-[8px] font-black text-foreground/30 uppercase tracking-[0.25em] md:text-[11px] md:text-foreground/40">
                {stat.label}
              </p>
              <p className="text-xs font-mono font-extrabold text-foreground/80 md:text-lg md:tracking-tight md:text-white">
                {stat.value}
              </p>
            </div>
          ))}
        </div>
      </footer>
    </main>
  );
}
