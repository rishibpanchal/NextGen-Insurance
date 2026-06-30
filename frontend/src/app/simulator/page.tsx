"use client";
import NeuCard from "@/components/NeuCard";
import { useState } from "react";
import { Activity, DownloadCloud, ShieldCheck } from "lucide-react";
import clsx from "clsx";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

export default function Simulator() {
  const [loading, setLoading] = useState(false);
  const [loadingSample, setLoadingSample] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [kycVerified, setKycVerified] = useState(true);
  const [description, setDescription] = useState("Customer repeatedly altering timeline facts. States items lost while commuting abroad.");
  const [amount, setAmount] = useState<number>(8500);
  const [age, setAge] = useState<number>(32);
  const [claimType, setClaimType] = useState("Auto");

  const handleLoadSample = async () => {
    setLoadingSample(true);
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000"}/random-claim`);
      if (res.ok) {
        const data = await res.json();
        setAmount(data.amount);
        setAge(data.age);
        setClaimType(data.type);
        setDescription(data.description);
        setKycVerified(true);
      }
    } catch (err) {
      console.error(err);
    }
    setLoadingSample(false);
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    
    const formData = new FormData(e.currentTarget);
    
    const payload = {
      claim_amount: amount,
      claim_type: claimType,
      customer_age: age,
      claim_description: description,
      past_claims: 0,
      claim_frequency: parseInt(formData.get("claim_frequency") as string) || 1,
      kyc_verified: kycVerified
    };

    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000"}/predict-risk`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      setResult(data);
    } catch (err) {
      console.error(err);
      alert("Failed to connect to AI Engine. Is FastAPI running?");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col gap-10">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-4xl font-extrabold text-gray-800 tracking-tight">Live Simulator</h1>
          <p className="text-gray-500 mt-2">Test the AI engine against synthetic or historical claims.</p>
        </div>
        <button 
          onClick={handleLoadSample}
          disabled={loadingSample}
          className="neu-flat px-6 py-3 rounded-full text-primary font-bold hover:text-blue-700 transition-all active:neu-pressed flex items-center gap-2"
        >
          <DownloadCloud size={20} />
          {loadingSample ? "Fetching..." : "Load Sample from Ledger"}
        </button>
      </div>

      <div className="grid grid-cols-2 gap-10">
        
        {/* Form Column */}
        <NeuCard className="col-span-1">
          <h2 className="text-lg font-bold text-gray-700 mb-6 flex items-center gap-2">
            <Activity className="text-primary" /> Input Parameters
          </h2>
          <form onSubmit={handleSubmit} className="flex flex-col gap-5">
            <div className="flex flex-col gap-2">
              <label className="text-xs font-bold text-gray-500 uppercase tracking-wider">Claim Tracking ID</label>
              <input name="claim_id" defaultValue="CX-998A" className="neu-pressed px-4 py-3 rounded-xl bg-transparent outline-none text-gray-700 focus:ring-2 focus:ring-primary/30" />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="flex flex-col gap-2">
                <label className="text-xs font-bold text-gray-500 uppercase tracking-wider">Policy Category</label>
                <select value={claimType} onChange={(e) => setClaimType(e.target.value)} name="claim_type" className="neu-pressed px-4 py-3 rounded-xl bg-transparent outline-none text-gray-700 focus:ring-2 focus:ring-primary/30 appearance-none">
                  <option>Auto</option>
                  <option>Medical</option>
                  <option>Home</option>
                  <option>Travel</option>
                </select>
              </div>
              <div className="flex flex-col gap-2">
                <label className="text-xs font-bold text-gray-500 uppercase tracking-wider">Frequency / Yr</label>
                <input name="claim_frequency" type="number" defaultValue={1} className="neu-pressed px-4 py-3 rounded-xl bg-transparent outline-none text-gray-700 focus:ring-2 focus:ring-primary/30" />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="flex flex-col gap-2">
                <label className="text-xs font-bold text-gray-500 uppercase tracking-wider">Requested ($)</label>
                <input value={amount} onChange={(e) => setAmount(Number(e.target.value))} name="claim_amount" type="number" className="neu-pressed px-4 py-3 rounded-xl bg-transparent outline-none text-gray-700 focus:ring-2 focus:ring-primary/30" />
              </div>
              <div className="flex flex-col gap-2">
                <label className="text-xs font-bold text-gray-500 uppercase tracking-wider">Holder Age</label>
                <input value={age} onChange={(e) => setAge(Number(e.target.value))} name="customer_age" type="number" className="neu-pressed px-4 py-3 rounded-xl bg-transparent outline-none text-gray-700 focus:ring-2 focus:ring-primary/30" />
              </div>
            </div>

            <div className="flex items-center gap-4 mt-2">
              <label className="text-sm font-bold text-gray-700 flex-1">e-KYC & AML Status (Onboard IQ rules)</label>
              <div className="flex items-center gap-2">
                <button 
                  type="button"
                  onClick={() => setKycVerified(true)}
                  className={clsx("px-4 py-2 rounded-xl font-bold text-sm transition-all", kycVerified ? "neu-pressed text-green-600" : "neu-flat text-gray-400")}
                >
                  Verified
                </button>
                <button 
                  type="button"
                  onClick={() => setKycVerified(false)}
                  className={clsx("px-4 py-2 rounded-xl font-bold text-sm transition-all", !kycVerified ? "neu-pressed text-red-600" : "neu-flat text-gray-400")}
                >
                  Failed
                </button>
              </div>
            </div>

            <div>
              <label className="block text-sm font-bold text-gray-700 mb-2 uppercase tracking-wider">Adjuster Narrative (NLP Text)</label>
              <textarea onChange={(e) => setDescription(e.target.value)} value={description} rows={4} className="w-full neu-pressed px-4 py-3 rounded-xl bg-transparent outline-none text-gray-700 focus:ring-2 focus:ring-primary/30 resize-none" />
            </div>

            <button type="submit" disabled={loading} className="neu-flat mt-4 py-4 rounded-xl font-bold text-primary hover:text-blue-500 transition-all active:neu-pressed disabled:opacity-50">
              {loading ? "Processing..." : "Evaluate with Neural Engine"}
            </button>
          </form>
        </NeuCard>

        {/* Results Column */}
        <div className="col-span-1">
          {result ? (
            <NeuCard className="flex flex-col items-center justify-center min-h-[300px] bg-gradient-to-br from-gray-50 to-gray-100 p-8 h-full">
                <p className="text-sm font-bold text-gray-500 tracking-wider uppercase mb-2">Automated Decision Route</p>
                <div className={clsx("px-6 py-2 rounded-full font-bold text-lg mb-6 shadow-sm", 
                  result.risk_category === "Low" ? "bg-green-100 text-green-800" : 
                  result.risk_category === "Medium" ? "bg-yellow-100 text-yellow-800" : 
                  "bg-red-100 text-red-800"
                )}>
                  {result.automated_action}
                </div>
                
                <h2 className={clsx("text-6xl font-black mb-2", 
                  result.risk_category === "High" ? "text-red-500" : 
                  result.risk_category === "Medium" ? "text-yellow-500" : "text-green-500"
                )}>
                  {(result.combined_risk_score * 100).toFixed(1)}<span className="text-3xl text-gray-400">%</span>
                </h2>
                <p className="text-gray-500 font-bold tracking-widest uppercase text-sm">Overall Risk Score</p>
                
                <div className="w-full grid grid-cols-2 gap-4 mt-8">
                  <div className="neu-pressed rounded-xl p-4 flex flex-col items-center">
                    <p className="text-xs font-bold text-gray-500 uppercase text-center">ML Probability</p>
                    <p className="text-xl font-bold text-gray-800 mt-1">{(result.ml_probability * 100).toFixed(1)}%</p>
                  </div>
                  <div className="neu-pressed rounded-xl p-4 flex flex-col items-center">
                    <p className="text-xs font-bold text-gray-500 uppercase text-center">NLP Sentiment</p>
                    <p className="text-xl font-bold text-gray-800 mt-1">{(result.nlp_risk_score * 100).toFixed(1)}%</p>
                  </div>
                </div>

                {result.top_drivers && result.top_drivers.length > 0 && (
                  <div className="w-full mt-6 text-left">
                     <h3 className="text-sm font-bold text-gray-500 uppercase tracking-wider mb-4">Decisive ML Tensors (SHAP)</h3>
                     <div className="flex flex-col gap-3">
                       {result.top_drivers.map((driver: any, idx: number) => (
                         <div key={idx} className="neu-pressed px-4 py-3 rounded-xl flex justify-between items-center text-sm">
                           <span className="font-mono text-gray-500">{driver.feature}</span>
                           <span className={clsx("font-bold", driver.importance > 0 ? "text-red-500" : "text-green-500")}>
                             {driver.importance > 0 ? "+" : ""}{driver.importance.toFixed(4)}
                           </span>
                         </div>
                       ))}
                     </div>
                  </div>
                )}

                {result.redacted_text && result.redacted_text !== description && (
                   <div className="w-full mt-6 bg-gray-800 text-green-400 p-4 rounded-xl text-left text-xs font-mono overflow-auto relative">
                     <div className="absolute top-2 right-2 bg-gray-700 px-2 py-1 rounded text-[10px] text-gray-300">DPDP PRIVY VAULT</div>
                     <p className="mb-1 text-gray-400">// PII Redaction Complete</p>
                     <p className="whitespace-pre-wrap">{result.redacted_text}</p>
                   </div>
                )}
            </NeuCard>
          ) : (
            <NeuCard className="flex items-center justify-center h-full border-2 border-dashed border-[#a3b1c6]/30 bg-transparent shadow-none">
              <p className="text-gray-400 font-medium text-center">👈 Enter claim details and click Evaluate to ping the local AI engine.</p>
            </NeuCard>
          )}
        </div>
      </div>
    </div>
  );
}
