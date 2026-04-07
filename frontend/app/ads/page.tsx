"use client";

import { useState } from "react";
import { api, apiUrl } from "@/lib/api";

type Variant = {
  id: string;
  headline: string;
  body: string;
  tone_label: string;
  cta?: string;
  status?: string;
};

export default function AdsPage() {
  const [product, setProduct] = useState("AI analytics copilot for GTM teams");
  const [audience, setAudience] = useState("Revenue leaders at B2B SaaS");
  const [platform, setPlatform] = useState("LinkedIn");
  const [goal, setGoal] = useState("Lead capture");
  const [experimentId, setExperimentId] = useState("");
  const [variants, setVariants] = useState<Variant[]>([]);
  const [reco, setReco] = useState("");
  const [platformPrediction, setPlatformPrediction] = useState("");

  async function generate() {
    const res = await api<{
      experiment_id: string;
      variants: Variant[];
      recommendation_reason?: string;
      platform_prediction?: string;
    }>("/ads/generate", {
      method: "POST",
      body: JSON.stringify({ product, audience, platform, goal }),
    });
    setExperimentId(res.experiment_id);
    setVariants(res.variants);
    setReco(res.recommendation_reason || "");
    setPlatformPrediction(res.platform_prediction || "");
  }

  async function setStatus(v: Variant, status: string) {
    if (!experimentId) return;
    await api(`/ads/experiment/${experimentId}/variant`, {
      method: "PATCH",
      body: JSON.stringify({ variant_id: v.id, status }),
    });
    const fresh = await api<{ variants: Variant[] }>(`/ads/experiment/${experimentId}`);
    setVariants(fresh.variants);
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-[family-name:var(--font-display)] text-3xl font-semibold">Ad copy &amp; A/B lab</h1>
        <p className="text-slate-600">Five labelled variants, AI pick, CSV export.</p>
      </div>
      <div className="grid gap-3 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm md:grid-cols-2">
        <label className="space-y-1 md:col-span-2">
          <span className="text-sm font-medium">Product / service</span>
          <input value={product} onChange={(e) => setProduct(e.target.value)} className="w-full rounded-lg border px-3 py-2" />
        </label>
        <label className="space-y-1 md:col-span-2">
          <span className="text-sm font-medium">Audience</span>
          <input value={audience} onChange={(e) => setAudience(e.target.value)} className="w-full rounded-lg border px-3 py-2" />
        </label>
        <label className="space-y-1">
          <span className="text-sm font-medium">Platform</span>
          <input value={platform} onChange={(e) => setPlatform(e.target.value)} className="w-full rounded-lg border px-3 py-2" />
        </label>
        <label className="space-y-1">
          <span className="text-sm font-medium">Goal</span>
          <input value={goal} onChange={(e) => setGoal(e.target.value)} className="w-full rounded-lg border px-3 py-2" />
        </label>
        <button onClick={generate} className="md:col-span-2 rounded-xl bg-accent px-4 py-2 text-white">
          Generate variants
        </button>
      </div>
      {(reco || platformPrediction) && (
        <div className="space-y-2 rounded-xl bg-blue-50 p-3 text-sm text-blue-900">
          {reco && (
            <p>
              <span className="font-semibold">Top pick: </span>
              {reco}
            </p>
          )}
          {platformPrediction && (
            <p>
              <span className="font-semibold">Platform insight: </span>
              {platformPrediction}
            </p>
          )}
        </div>
      )}
      <div className="grid gap-4 md:grid-cols-2">
        {variants.map((v) => (
          <div key={v.id} className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
            <div className="flex items-center justify-between">
              <p className="text-sm font-semibold text-accent">{v.tone_label}</p>
              <span className="text-xs uppercase text-slate-500">{v.status || "Testing"}</span>
            </div>
            <p className="mt-2 text-lg font-semibold">{v.headline}</p>
            <p className="mt-2 text-sm text-slate-700">{v.body}</p>
            <p className="mt-2 text-sm font-medium">CTA: {v.cta}</p>
            <div className="mt-3 flex flex-wrap gap-2">
              {["Testing", "Winner", "Rejected"].map((s) => (
                <button key={s} onClick={() => setStatus(v, s)} className="rounded-full border px-3 py-1 text-xs">
                  {s}
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>
      {experimentId && (
        <a className="text-accent underline" href={apiUrl(`/ads/experiment/${experimentId}/export.csv`)} target="_blank" rel="noreferrer">
          Download CSV
        </a>
      )}
    </div>
  );
}
