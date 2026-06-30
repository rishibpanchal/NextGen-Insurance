"use client";
import NeuCard from "@/components/NeuCard";
import { useSearchParams } from "next/navigation";
import { useEffect, useState, Suspense } from "react";
import clsx from "clsx";
import { Download, AlertTriangle, FileText, Search } from "lucide-react";

function AnalyzerContent() {
  const searchParams = useSearchParams();
  const claimId = searchParams?.get("claimId");
  const [claim, setClaim] = useState<any>(null);
  const [error, setError] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!claimId) return;
    setLoading(true);
    fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000"}/claims/${claimId}`)
      .then(res => {
        if (!res.ok) throw new Error("Not found");
        return res.json();
      })
      .then(data => {
        setClaim(data);
        setError(false);
      })
      .catch(() => setError(true))
      .finally(() => setLoading(false));
  }, [claimId]);

  const exportCSV = () => {
    if (!claim) return;
    
    // Create CSV content for a single claim
    const headers = ["Claim_ID", "Policy_Holder", "Category", "Amount", "Age", "Risk_Category", "Composite_Score", "ML_Probability", "NLP_Sentiment", "Anomaly_Flag", "Description"];
    const row = [
      claim.id,
      claim.customer_id,
      claim.type,
      claim.amount,
      claim.age,
      claim.risk,
      claim.score,
      claim.ml_prob,
      claim.nlp_score,
      claim.anomaly,
      `"${claim.description.replace(/"/g, '""')}"`
    ];
    
    const csvContent = "data:text/csv;charset=utf-8," + headers.join(",") + "\n" + row.join(",");
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `Claim_Analysis_${claim.id}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  if (!claimId) {
    return (
      <NeuCard className="flex flex-col items-center justify-center p-20 mt-10">
        <Search size={48} className="text-gray-300 mb-4" />
        <h2 className="text-xl font-bold text-gray-500">No Claim Selected</h2>
        <p className="text-gray-400 mt-2">Please go to the Database Ledger and select a claim to analyze.</p>
      </NeuCard>
    );
  }

  if (loading) return <div className="p-10 text-gray-500 font-bold tracking-widest text-center mt-20">FETCHING CLAIM RECORD...</div>;

  if (error || !claim) {
    return (
      <NeuCard className="flex flex-col items-center justify-center p-20 mt-10 border-2 border-red-200 bg-red-50">
        <AlertTriangle size={48} className="text-red-400 mb-4" />
        <h2 className="text-xl font-bold text-red-700">Claim Not Found</h2>
        <p className="text-red-500 mt-2">Could not find record for ID: {claimId}</p>
      </NeuCard>
    );
  }

  return (
    <div className="flex flex-col gap-10">
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-4xl font-extrabold text-gray-800 tracking-tight">Claim Analyzer</h1>
          <p className="text-gray-500 mt-2">Deep dive into a specific historical claim record.</p>
        </div>
        <button 
          onClick={exportCSV}
          className="neu-flat px-6 py-3 rounded-full text-green-600 font-bold hover:text-green-700 transition-all active:neu-pressed flex items-center gap-2"
        >
          <Download size={20} /> Export Claim CSV
        </button>
      </div>

      <div className="grid grid-cols-3 gap-10">
        <NeuCard className="col-span-2">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-black text-gray-700 font-mono">{claim.id}</h2>
            <div className={clsx("px-4 py-1 rounded-full font-bold text-sm", 
              claim.risk === "High" ? "bg-red-100 text-red-800" : 
              claim.risk === "Medium" ? "bg-yellow-100 text-yellow-800" : 
              "bg-green-100 text-green-800"
            )}>
              {claim.risk} Risk Profile
            </div>
          </div>

          <div className="grid grid-cols-2 gap-8 mb-8">
            <div className="flex flex-col gap-4">
               <div>
                 <p className="text-xs font-bold text-gray-500 uppercase tracking-wider">Policy Holder</p>
                 <p className="text-lg font-bold text-gray-800 mt-1">{claim.customer_id}</p>
               </div>
               <div>
                 <p className="text-xs font-bold text-gray-500 uppercase tracking-wider">Policy Category</p>
                 <p className="text-lg font-bold text-gray-800 mt-1">{claim.type}</p>
               </div>
            </div>
            <div className="flex flex-col gap-4">
               <div>
                 <p className="text-xs font-bold text-gray-500 uppercase tracking-wider">Claim Amount</p>
                 <p className="text-lg font-bold text-gray-800 mt-1">${claim.amount.toLocaleString()}</p>
               </div>
               <div>
                 <p className="text-xs font-bold text-gray-500 uppercase tracking-wider">Holder Age</p>
                 <p className="text-lg font-bold text-gray-800 mt-1">{claim.age} yrs</p>
               </div>
            </div>
          </div>

          <div>
             <p className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2 flex items-center gap-2"><FileText size={16}/> Adjuster Narrative</p>
             <div className="neu-pressed p-4 rounded-xl text-gray-700 text-sm whitespace-pre-wrap">
               {claim.description}
             </div>
          </div>
        </NeuCard>

        <NeuCard className="col-span-1 flex flex-col items-center justify-center text-center p-8 bg-gradient-to-br from-gray-50 to-gray-100">
           <h3 className="text-sm font-bold text-gray-500 uppercase tracking-wider mb-6">Neural Engine Scores</h3>
           
           <h2 className={clsx("text-6xl font-black mb-2", 
             claim.risk === "High" ? "text-red-500" : 
             claim.risk === "Medium" ? "text-yellow-500" : "text-green-500"
           )}>
             {(claim.score * 100).toFixed(1)}<span className="text-3xl text-gray-400">%</span>
           </h2>
           <p className="text-gray-500 font-bold tracking-widest uppercase text-sm mb-8">Composite Risk</p>
           
           <div className="w-full flex flex-col gap-4">
             <div className="neu-pressed rounded-xl p-4 flex justify-between items-center">
               <p className="text-xs font-bold text-gray-500 uppercase">ML Tensor</p>
               <p className="text-lg font-bold text-gray-800">{(claim.ml_prob * 100).toFixed(1)}%</p>
             </div>
             <div className="neu-pressed rounded-xl p-4 flex justify-between items-center">
               <p className="text-xs font-bold text-gray-500 uppercase">NLP Sentiment</p>
               <p className="text-lg font-bold text-gray-800">{(claim.nlp_score * 100).toFixed(1)}%</p>
             </div>
             {claim.anomaly && (
               <div className="mt-2 text-xs font-bold text-red-500 bg-red-100 py-2 px-4 rounded-lg flex items-center justify-center gap-2">
                 <AlertTriangle size={14} /> Mathematical Anomaly Detected
               </div>
             )}
           </div>
        </NeuCard>
      </div>
    </div>
  );
}

export default function Analyzer() {
  return (
    <Suspense fallback={<div className="p-10 text-gray-500 font-bold tracking-widest text-center mt-20">LOADING...</div>}>
      <AnalyzerContent />
    </Suspense>
  );
}
