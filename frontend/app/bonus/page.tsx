"use client";

import { useState } from "react";
import { api } from "@/lib/api";

export default function BonusPage() {
  const [brandId, setBrandId] = useState("");
  const [campaignId, setCampaignId] = useState("");
  const [competitor, setCompetitor] = useState("They claim the cheapest analytics — we know it's a trap.");
  const [sample, setSample] = useState("Our launch post draft goes here...");
  const [out, setOut] = useState<Record<string, unknown> | null>(null);
  const [tone, setTone] = useState<Record<string, unknown> | null>(null);

  async function runComp() {
    const res = await api<Record<string, unknown>>("/bonus/competitor", {
      method: "POST",
      body: JSON.stringify({
        competitor_post: competitor,
        brand_id: brandId || localStorage.getItem("lastBrandId"),
        campaign_id: campaignId || localStorage.getItem("lastCampaignId") || null,
      }),
    });
    setOut(res);
  }

  async function runTone() {
    const res = await api<Record<string, unknown>>("/bonus/tone-score", {
      method: "POST",
      body: JSON.stringify({ text: sample, brand_id: brandId || localStorage.getItem("lastBrandId") }),
    });
    setTone(res);
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-[family-name:var(--font-display)] text-3xl font-semibold">Bonus tools</h1>
        <p className="text-slate-600">Competitor counter-positioning and tone consistency scoring.</p>
      </div>
      <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm space-y-3">
        <label className="space-y-1 block">
          <span className="text-sm font-medium">Brand ID</span>
          <input value={brandId} onChange={(e) => setBrandId(e.target.value)} className="w-full rounded-lg border px-3 py-2" />
        </label>
        <label className="space-y-1 block">
          <span className="text-sm font-medium">Campaign ID (optional)</span>
          <input value={campaignId} onChange={(e) => setCampaignId(e.target.value)} className="w-full rounded-lg border px-3 py-2" />
        </label>
        <label className="space-y-1 block">
          <span className="text-sm font-medium">Competitor post</span>
          <textarea value={competitor} onChange={(e) => setCompetitor(e.target.value)} className="w-full rounded-lg border px-3 py-2" rows={5} />
        </label>
        <button onClick={runComp} className="rounded-xl bg-accent px-4 py-2 text-white">
          Analyze competitor
        </button>
        {out && <pre className="mt-3 overflow-x-auto text-xs">{JSON.stringify(out, null, 2)}</pre>}
      </div>
      <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm space-y-3">
        <label className="space-y-1 block">
          <span className="text-sm font-medium">Sample copy to score</span>
          <textarea value={sample} onChange={(e) => setSample(e.target.value)} className="w-full rounded-lg border px-3 py-2" rows={6} />
        </label>
        <button onClick={runTone} className="rounded-xl bg-coral px-4 py-2 text-white">
          Score tone fit
        </button>
        {tone && <pre className="mt-3 overflow-x-auto text-xs">{JSON.stringify(tone, null, 2)}</pre>}
      </div>
    </div>
  );
}
