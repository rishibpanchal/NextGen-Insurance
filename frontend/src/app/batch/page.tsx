"use client";
import NeuCard from "@/components/NeuCard";
import { UploadCloud, CheckCircle2, AlertTriangle, ShieldAlert, Activity } from "lucide-react";
import { useState } from "react";
import clsx from "clsx";

export default function BatchProcessing() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any>(null);

  const [isDragging, setIsDragging] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
    }
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    setResults(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000"}/batch-predict`, {
        method: "POST",
        body: formData,
      });
      if (!res.ok) throw new Error("Upload failed");
      const data = await res.json();
      setResults(data);
    } catch (err) {
      console.error(err);
      alert("Failed to process batch. Make sure CSV has correct columns.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col gap-10 h-full">
      <div>
        <div className="flex items-center gap-3">
           <h1 className="text-4xl font-extrabold text-gray-800 tracking-tight">Batch Adjudication</h1>
           <span className="px-3 py-1 bg-blue-100 text-blue-700 text-xs font-bold rounded-full border border-blue-200 uppercase tracking-wider">Enterprise STP</span>
        </div>
        <p className="text-gray-500 mt-2">Upload bulk CSV files to instantly route claims using Straight-Through Processing (STP) logic.</p>
      </div>

      <NeuCard className={clsx(
        "flex flex-col items-center justify-center p-10 border-2 border-dashed transition-all",
        isDragging ? "border-blue-500 bg-blue-50" : "border-[#a3b1c6]/50"
      )}
      >
        <div 
          className="w-full h-full flex flex-col items-center justify-center"
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          <UploadCloud size={48} className={clsx("mb-4 transition-colors", isDragging ? "text-blue-500" : "text-primary")} />
          <h2 className="text-xl font-bold text-gray-700 mb-2">Drag & Drop Database Export</h2>
          <p className="text-gray-500 mb-6 text-sm">Supports CSV files containing hundreds of claim rows.</p>
          
          <label className="neu-flat px-6 py-3 rounded-full text-primary font-bold cursor-pointer hover:text-blue-700 transition-all active:neu-pressed">
            Browse Files
            <input type="file" accept=".csv" className="hidden" onChange={handleFileChange} />
          </label>
          
          {file && (
            <div className="mt-6 flex flex-col items-center w-full">
              <p className="text-gray-700 font-bold mb-4 bg-white/50 px-4 py-2 rounded-lg">Selected: {file.name}</p>
              <button 
                onClick={handleUpload} 
                disabled={loading}
                className="px-8 py-3 bg-primary text-white font-bold rounded-full shadow-lg shadow-blue-500/30 hover:bg-blue-700 transition-all disabled:opacity-50 flex items-center gap-2"
              >
                {loading ? <Activity className="animate-spin" /> : <PlayIcon />}
                {loading ? "Processing Batch via ML Engine..." : "Execute Batch Adjudication"}
              </button>
            </div>
          )}
        </div>
      </NeuCard>

      {results && (
        <div className="flex flex-col gap-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
          <h2 className="text-2xl font-bold text-gray-700">Triage Results Overview</h2>
          
          <div className="grid grid-cols-4 gap-6">
            <NeuCard className="flex flex-col justify-center h-32 border-l-4 border-gray-400">
              <p className="text-xs font-bold text-gray-500 tracking-wider uppercase">Total Processed</p>
              <p className="text-4xl font-black text-gray-800 mt-2">{results.total_processed}</p>
            </NeuCard>
            
            <NeuCard className="flex flex-col justify-center h-32 border-l-4 border-green-500 bg-green-50/50">
              <div className="flex items-center gap-2 mb-2">
                 <CheckCircle2 size={16} className="text-green-600" />
                 <p className="text-xs font-bold text-green-700 tracking-wider uppercase">Auto-Approved</p>
              </div>
              <p className="text-4xl font-black text-green-600">{results.auto_approved}</p>
            </NeuCard>

            <NeuCard className="flex flex-col justify-center h-32 border-l-4 border-yellow-500 bg-yellow-50/50">
              <div className="flex items-center gap-2 mb-2">
                 <AlertTriangle size={16} className="text-yellow-600" />
                 <p className="text-xs font-bold text-yellow-700 tracking-wider uppercase">Manual Review</p>
              </div>
              <p className="text-4xl font-black text-yellow-600">{results.manual_review}</p>
            </NeuCard>

            <NeuCard className="flex flex-col justify-center h-32 border-l-4 border-red-500 bg-red-50/50">
              <div className="flex items-center gap-2 mb-2">
                 <ShieldAlert size={16} className="text-red-600" />
                 <p className="text-xs font-bold text-red-700 tracking-wider uppercase">SIU Fraud Routing</p>
              </div>
              <p className="text-4xl font-black text-red-600">{results.fraud_siu}</p>
            </NeuCard>
          </div>
          
          <NeuCard className="p-6">
             <h3 className="font-bold text-gray-700 mb-4">Sample Routing Output (First 50)</h3>
             <div className="max-h-[300px] overflow-auto">
               <table className="w-full text-left border-collapse">
                 <thead>
                   <tr className="border-b border-gray-200 sticky top-0 bg-[#e0e5ec]">
                     <th className="py-3 px-4 text-xs font-bold text-gray-500 uppercase">Row</th>
                     <th className="py-3 px-4 text-xs font-bold text-gray-500 uppercase">Amount</th>
                     <th className="py-3 px-4 text-xs font-bold text-gray-500 uppercase">Risk Score</th>
                     <th className="py-3 px-4 text-xs font-bold text-gray-500 uppercase">Automated Route</th>
                   </tr>
                 </thead>
                 <tbody>
                   {results.sample_results.map((r: any, idx: number) => (
                     <tr key={idx} className="border-b border-gray-100/50 hover:bg-white/40 transition-colors">
                       <td className="py-3 px-4 font-mono text-sm text-gray-500">{r.index}</td>
                       <td className="py-3 px-4 font-bold text-gray-700">${r.amount}</td>
                       <td className="py-3 px-4">
                         <span className={clsx(
                           "px-2 py-1 rounded text-xs font-bold",
                           r.risk > 0.7 ? "bg-red-100 text-red-700" : r.risk > 0.4 ? "bg-yellow-100 text-yellow-700" : "bg-green-100 text-green-700"
                         )}>
                           {(r.risk * 100).toFixed(1)}%
                         </span>
                       </td>
                       <td className="py-3 px-4">
                         <span className={clsx(
                           "font-bold text-sm",
                           r.status.includes("APPROVED") ? "text-green-600" : r.status.includes("REVIEW") ? "text-yellow-600" : "text-red-600"
                         )}>
                           {r.status}
                         </span>
                       </td>
                     </tr>
                   ))}
                 </tbody>
               </table>
             </div>
          </NeuCard>
        </div>
      )}
    </div>
  );
}

function PlayIcon() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polygon points="5 3 19 12 5 21 5 3"></polygon>
    </svg>
  );
}
