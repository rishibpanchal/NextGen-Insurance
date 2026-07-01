"use client";
import NeuCard from "@/components/NeuCard";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { ArrowLeft } from "lucide-react";

export default function AddClaim() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    claim_amount: 0,
    claim_type: "Auto",
    customer_age: 30,
    claim_description: "",
    past_claims: 0,
    claim_frequency: 1,
    kyc_verified: true
  });
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000"}/claims`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData)
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Failed to add claim");
      setSuccess(`Claim added successfully! ID: ${data.claim_id}`);
      setTimeout(() => router.push("/database"), 2000);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col gap-8 h-full max-w-3xl mx-auto w-full">
      <div className="flex items-center gap-4">
        <button onClick={() => router.back()} className="neu-flat p-3 rounded-full hover:text-blue-500 transition-all">
          <ArrowLeft size={20} />
        </button>
        <div>
          <h1 className="text-3xl font-bold text-gray-700 tracking-tight">Add Individual Claim</h1>
          <p className="text-gray-500 text-sm mt-1">Manually enter a claim into the ledger.</p>
        </div>
      </div>

      <NeuCard>
        <form onSubmit={handleSubmit} className="flex flex-col gap-6">
          <div className="grid grid-cols-2 gap-6">
            <div className="flex flex-col gap-2">
              <label className="text-xs font-bold text-gray-500 uppercase tracking-wider">Claim Amount ($)</label>
              <input type="number" required value={formData.claim_amount} onChange={e => setFormData({...formData, claim_amount: Number(e.target.value)})} className="neu-pressed px-4 py-3 rounded-xl outline-none bg-transparent" />
            </div>
            <div className="flex flex-col gap-2">
              <label className="text-xs font-bold text-gray-500 uppercase tracking-wider">Claim Type</label>
              <select value={formData.claim_type} onChange={e => setFormData({...formData, claim_type: e.target.value})} className="neu-pressed px-4 py-3 rounded-xl outline-none bg-transparent">
                <option>Auto</option>
                <option>Home</option>
                <option>Health</option>
                <option>Property</option>
                <option>Travel</option>
              </select>
            </div>
            <div className="flex flex-col gap-2">
              <label className="text-xs font-bold text-gray-500 uppercase tracking-wider">Customer Age</label>
              <input type="number" required value={formData.customer_age} onChange={e => setFormData({...formData, customer_age: Number(e.target.value)})} className="neu-pressed px-4 py-3 rounded-xl outline-none bg-transparent" />
            </div>
            <div className="flex flex-col gap-2">
              <label className="text-xs font-bold text-gray-500 uppercase tracking-wider">Past Claims</label>
              <input type="number" required value={formData.past_claims} onChange={e => setFormData({...formData, past_claims: Number(e.target.value)})} className="neu-pressed px-4 py-3 rounded-xl outline-none bg-transparent" />
            </div>
          </div>
          
          <div className="flex flex-col gap-2">
            <label className="text-xs font-bold text-gray-500 uppercase tracking-wider">Claim Description</label>
            <textarea required rows={4} value={formData.claim_description} onChange={e => setFormData({...formData, claim_description: e.target.value})} className="neu-pressed px-4 py-3 rounded-xl outline-none resize-none bg-transparent" placeholder="Enter details..."></textarea>
          </div>

          <div className="flex items-center gap-3 mt-2">
            <input type="checkbox" id="kyc" checked={formData.kyc_verified} onChange={e => setFormData({...formData, kyc_verified: e.target.checked})} className="w-5 h-5" />
            <label htmlFor="kyc" className="text-sm font-bold text-gray-600">KYC Verified</label>
          </div>

          {error && <div className="text-red-500 text-sm font-bold">{error}</div>}
          {success && <div className="text-green-500 text-sm font-bold">{success}</div>}

          <button type="submit" disabled={loading} className="mt-4 neu-flat px-6 py-4 rounded-xl font-bold text-blue-600 hover:text-blue-700 transition-all active:neu-pressed disabled:opacity-50">
            {loading ? "Processing..." : "Submit Claim to Ledger"}
          </button>
        </form>
      </NeuCard>
    </div>
  );
}
