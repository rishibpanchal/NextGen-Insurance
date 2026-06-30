"use client";
import NeuCard from "@/components/NeuCard";
import clsx from "clsx";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Search } from "lucide-react";

export default function Database() {
  const [claims, setClaims] = useState<any[]>([]);
  const [search, setSearch] = useState("");
  const router = useRouter();

  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000"}/claims?limit=10`)
      .then(res => res.json())
      .then(data => setClaims(data.claims || []))
      .catch(console.error);
  }, []);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (search.trim()) {
      router.push(`/analyzer?claimId=${search.trim()}`);
    }
  };

  if (claims.length === 0) return <div className="p-10 text-gray-500 font-bold tracking-widest text-center mt-20">CONNECTING TO LEDGER...</div>;

  return (
    <div className="flex flex-col gap-10 h-full">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold text-gray-700 tracking-tight">Full Database Ledger</h1>
          <p className="text-gray-500 text-sm mt-1">Explore and search the raw structured database (Showing latest 10).</p>
        </div>
        <form onSubmit={handleSearch} className="flex gap-2">
          <input 
            type="text" 
            placeholder="Search Claim ID (e.g. CX-998A)" 
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="neu-pressed px-4 py-3 rounded-full text-sm outline-none w-64"
          />
          <button type="submit" className="neu-flat px-4 py-3 rounded-full text-primary hover:text-blue-500 transition-all flex items-center justify-center">
            <Search size={18} />
          </button>
        </form>
      </div>

      <NeuCard className="flex-1">
        <div className="grid grid-cols-6 border-b-2 border-[#a3b1c6]/30 pb-4 mb-4 text-xs font-bold text-gray-500 uppercase tracking-wider px-4">
          <div>Claim ID</div>
          <div className="col-span-2">Policy Holder</div>
          <div>Category</div>
          <div>Amount Raised</div>
          <div>AI Priority</div>
        </div>

        <div className="flex flex-col gap-4">
          {claims.map((row) => (
            <div 
              key={row.id} 
              onClick={() => router.push(`/analyzer?claimId=${row.id}`)}
              className="grid grid-cols-6 items-center px-4 py-3 neu-flat rounded-xl text-sm text-gray-700 cursor-pointer hover:bg-blue-50/50 transition-all active:neu-pressed"
            >
              <div className="font-mono text-gray-500">{row.id}</div>
              <div className="col-span-2 font-bold">{row.name}</div>
              <div>{row.type}</div>
              <div className="font-mono">${row.amount.toLocaleString()}</div>
              <div>
                <span className={clsx(
                  "px-3 py-1 rounded-full text-xs font-bold flex items-center gap-2 w-max shadow-inner",
                  row.risk === "High" ? "bg-red-100 text-red-600 shadow-red-200" :
                  row.risk === "Medium" ? "bg-yellow-100 text-yellow-600 shadow-yellow-200" :
                  "bg-green-100 text-green-600 shadow-green-200"
                )}>
                  {row.risk === "High" ? "🚨 High" : row.risk === "Medium" ? "⚠️ Medium" : "✅ Low"}
                </span>
              </div>
            </div>
          ))}
        </div>
      </NeuCard>
    </div>
  );
}
