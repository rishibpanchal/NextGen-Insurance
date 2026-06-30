"use client";
import NeuCard from "@/components/NeuCard";
import { Search } from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { useEffect, useState } from "react";

export default function Home() {
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000"}/dashboard-stats`)
      .then(res => {
        if (!res.ok) throw new Error(`API error: ${res.status}`);
        return res.json();
      })
      .then(setData)
      .catch(err => {
        console.error(err);
        setError(err.message);
      });
  }, []);

  if (error) return <div className="p-10 text-red-500 font-bold tracking-widest text-center mt-20">SYSTEM ERROR: {error}</div>;
  if (!data) return <div className="p-10 text-gray-500 font-bold tracking-widest text-center mt-20">INITIALIZING NEURAL ENGINE...</div>;

  return (
    <div className="flex flex-col gap-10">
      
      {/* Top Bar */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-700 tracking-tight">Risk Analytics</h1>
          <p className="text-gray-500 text-sm mt-1">Evaluate and manage anomalies via secure inference engine.</p>
        </div>
        <div className="flex gap-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
            <input 
              type="text" 
              placeholder="Search IDs, Names..." 
              className="neu-pressed pl-10 pr-4 py-3 rounded-xl bg-transparent outline-none text-gray-600 placeholder-gray-400 text-sm w-64 focus:ring-2 focus:ring-primary/20"
            />
          </div>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-4 gap-8">
        <NeuCard className="flex flex-col justify-center h-32 border-l-4 border-green-500">
          <p className="text-xs font-bold text-gray-500 tracking-wider uppercase">Total Coverage Exposure</p>
          <p className="text-3xl font-extrabold text-primary mt-2">${data.kpis.total_exposure.toLocaleString(undefined, { maximumFractionDigits: 0 })}</p>
        </NeuCard>
        <NeuCard className="flex flex-col justify-center h-32">
          <p className="text-xs font-bold text-gray-500 tracking-wider uppercase">Avg Settlement</p>
          <p className="text-3xl font-extrabold text-gray-700 mt-2">${data.kpis.avg_settlement.toLocaleString(undefined, { maximumFractionDigits: 0 })}</p>
        </NeuCard>
        <NeuCard className="flex flex-col justify-center h-32 border-l-4 border-red-500">
          <p className="text-xs font-bold text-gray-500 tracking-wider uppercase">High Risk Identified</p>
          <p className="text-3xl font-extrabold text-red-500 mt-2">{data.kpis.high_risk}</p>
        </NeuCard>
        <NeuCard className="flex flex-col justify-center h-32 border-l-4 border-yellow-500">
          <p className="text-xs font-bold text-gray-500 tracking-wider uppercase">ML Anomalies Flagged</p>
          <p className="text-3xl font-extrabold text-yellow-500 mt-2">{data.kpis.anomalies}</p>
        </NeuCard>
      </div>

      {/* Main Content Area */}
      <div className="grid grid-cols-3 gap-8 h-96">
        <NeuCard className="col-span-2 flex flex-col">
          <h2 className="text-lg font-bold text-gray-700 mb-6">Exposure by Category</h2>
          <div className="flex-1 w-full h-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.chart_data} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#CBD5E1" />
                <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{fill: '#64748b', fontSize: 12}} dy={10} />
                <YAxis axisLine={false} tickLine={false} tick={{fill: '#64748b', fontSize: 12}} />
                <Tooltip cursor={{fill: '#e0e5ec'}} contentStyle={{borderRadius: '12px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'}}/>
                <Bar dataKey="exposure" fill="#38bdf8" radius={[4, 4, 0, 0]} />
                <Bar dataKey="risk" fill="#ef4444" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </NeuCard>

        <NeuCard className="col-span-1 flex flex-col items-center justify-center">
          <h2 className="text-lg font-bold text-gray-700 w-full text-center mb-8">Data Integrity Score</h2>
          <div className="relative w-48 h-48 rounded-full neu-flat flex items-center justify-center border-4 border-[#e0e5ec]">
            <div className="absolute inset-2 rounded-full neu-pressed flex items-center justify-center border-4 border-green-500 shadow-[0_0_15px_rgba(34,197,94,0.5)]">
              <span className="text-4xl font-extrabold text-gray-700">92%</span>
            </div>
          </div>
          <p className="text-sm text-gray-500 mt-8 text-center px-4">
            Overall portfolio safety based on active ML cohort.
          </p>
        </NeuCard>
      </div>
    </div>
  );
}
