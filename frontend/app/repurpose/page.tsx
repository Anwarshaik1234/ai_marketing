"use client";

import { useState } from "react";
import { api } from "@/lib/api";

const ASSET_TYPES = [
  { value: "blog", label: "Blog / article (paste)" },
  { value: "podcast", label: "Podcast transcript (paste)" },
  { value: "webinar", label: "Webinar / call transcript (.txt upload or paste)" },
];

export default function RepurposePage() {
  const [campaignId, setCampaignId] = useState("");
  const [assetType, setAssetType] = useState("blog");
  const [assetName, setAssetName] = useState("Q3 Product Essay");
  const [text, setText] = useState(
    "Paste a long blog, podcast transcript, or webinar notes here. The engine will extract insights and rebuild every channel format with attribution.",
  );
  const [result, setResult] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(false);

  function onTranscriptFile(e: React.ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0];
    if (!f) return;
    const reader = new FileReader();
    reader.onload = () => setText(String(reader.result || ""));
    reader.readAsText(f);
  }

  async function run() {
    const cid = campaignId || localStorage.getItem("lastCampaignId") || "";
    if (!cid) {
      setResult({ error: "Set Campaign ID or create a campaign first." });
      return;
    }
    setLoading(true);
    try {
      const res = await api<Record<string, unknown>>("/repurpose/run", {
        method: "POST",
        body: JSON.stringify({
          campaign_id: cid,
          asset_name: assetName,
          asset_type: assetType,
          text,
        }),
      });
      setResult(res);
    } catch (err) {
      setResult({ error: err instanceof Error ? err.message : "Request failed" });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-[family-name:var(--font-display)] text-3xl font-semibold">Repurposing engine</h1>
        <p className="text-slate-600">Source-only generation with coverage map + insights.</p>
      </div>
      <div className="space-y-3 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <label className="space-y-1 block">
          <span className="text-sm font-medium">Campaign ID</span>
          <input value={campaignId} onChange={(e) => setCampaignId(e.target.value)} className="w-full rounded-lg border px-3 py-2" />
        </label>
        <label className="space-y-1 block">
          <span className="text-sm font-medium">Asset name</span>
          <input value={assetName} onChange={(e) => setAssetName(e.target.value)} className="w-full rounded-lg border px-3 py-2" />
        </label>
        <label className="space-y-1 block">
          <span className="text-sm font-medium">Source type</span>
          <select value={assetType} onChange={(e) => setAssetType(e.target.value)} className="w-full rounded-lg border px-3 py-2">
            {ASSET_TYPES.map((t) => (
              <option key={t.value} value={t.value}>
                {t.label}
              </option>
            ))}
          </select>
        </label>
        <label className="space-y-1 block">
          <span className="text-sm font-medium">Upload transcript (.txt) — optional</span>
          <input type="file" accept=".txt,text/plain" onChange={onTranscriptFile} className="text-sm" />
        </label>
        <label className="space-y-1 block">
          <span className="text-sm font-medium">Long-form text</span>
          <textarea value={text} onChange={(e) => setText(e.target.value)} className="w-full rounded-lg border px-3 py-2" rows={10} />
        </label>
        <button disabled={loading} onClick={run} className="rounded-xl bg-accent px-4 py-2 text-white disabled:opacity-50">
          {loading ? "Running…" : "Run repurposing"}
        </button>
      </div>
      {result && (
        <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
          {"error" in result && result.error ? (
            <p className="text-sm text-rose-700">{String(result.error)}</p>
          ) : (
            <>
              <p className="font-semibold">Coverage map</p>
              <pre className="mt-2 overflow-x-auto text-xs text-slate-700">{JSON.stringify(result.coverage_map, null, 2)}</pre>
              <p className="mt-4 font-semibold">Analysis</p>
              <pre className="mt-2 overflow-x-auto text-xs text-slate-700">{JSON.stringify(result.analysis, null, 2)}</pre>
              <p className="mt-4 text-xs text-slate-500">
                Generated pieces are saved to this campaign — open the Content hub or Calendar to review.
              </p>
            </>
          )}
        </div>
      )}
    </div>
  );
}
