"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

type Piece = {
  id: string;
  platform: string;
  format_key: string;
  title: string;
  body: string;
};

export default function HubPage() {
  const [campaignId, setCampaignId] = useState("");
  const [topic, setTopic] = useState("Launching our analytics refresh");
  const [brief, setBrief] = useState("Emphasize trust and speed for marketing teams.");
  const [pieces, setPieces] = useState<Piece[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [refine, setRefine] = useState<Record<string, string>>({});

  useEffect(() => {
    setCampaignId(localStorage.getItem("lastCampaignId") || "");
  }, []);

  async function load() {
    if (!campaignId) return;
    const data = await api<Piece[]>(`/content/campaign/${campaignId}`);
    setPieces(data);
  }

  async function generate() {
    setLoading(true);
    setError("");
    try {
      await api("/content/generate", {
        method: "POST",
        body: JSON.stringify({ campaign_id: campaignId, topic, brief }),
      });
      await load();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Generation failed");
    } finally {
      setLoading(false);
    }
  }

  async function regenerate(p: Piece) {
    const instruction = refine[p.id] || "Tighten copy; keep brand guardrails.";
    await api("/content/regenerate", {
      method: "POST",
      body: JSON.stringify({
        campaign_id: campaignId,
        content_piece_id: p.id,
        current_text: p.body,
        instruction,
      }),
    });
    await load();
  }

  useEffect(() => {
    if (campaignId) load();
  }, [campaignId]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-[family-name:var(--font-display)] text-3xl font-semibold">Content generation hub</h1>
        <p className="text-slate-600">One brief → all formats. Regenerate or refine each block.</p>
      </div>
      <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm space-y-3">
        <label className="space-y-1 block">
          <span className="text-sm font-medium">Campaign ID</span>
          <input value={campaignId} onChange={(e) => setCampaignId(e.target.value)} className="w-full rounded-lg border px-3 py-2" />
        </label>
        <label className="space-y-1 block">
          <span className="text-sm font-medium">Topic</span>
          <input value={topic} onChange={(e) => setTopic(e.target.value)} className="w-full rounded-lg border px-3 py-2" />
        </label>
        <label className="space-y-1 block">
          <span className="text-sm font-medium">Brief</span>
          <textarea value={brief} onChange={(e) => setBrief(e.target.value)} className="w-full rounded-lg border px-3 py-2" rows={3} />
        </label>
        <button
          disabled={loading || !campaignId}
          onClick={generate}
          className="rounded-xl bg-accent px-4 py-2 text-white disabled:opacity-50"
        >
          {loading ? "Generating…" : "Generate all formats"}
        </button>
        {error && <p className="text-sm text-rose-700">{error}</p>}
      </div>
      <div className="grid gap-4 md:grid-cols-2">
        {pieces.map((p) => (
          <div key={p.id} className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
            <div className="flex items-center justify-between gap-2">
              <div>
                <p className="text-xs uppercase text-slate-500">{p.platform}</p>
                <p className="font-semibold">{p.format_key}</p>
              </div>
            </div>
            <pre className="mt-3 whitespace-pre-wrap text-sm text-slate-800">{p.body}</pre>
            <div className="mt-3 space-y-2">
              <input
                value={refine[p.id] || ""}
                onChange={(e) => setRefine({ ...refine, [p.id]: e.target.value })}
                placeholder='Refine: e.g. "Make more aggressive" or "Shorten"'
                className="w-full rounded-lg border px-3 py-2 text-sm"
              />
              <div className="flex gap-2">
                <button
                  onClick={() => regenerate(p)}
                  className="rounded-lg border border-slate-200 px-3 py-1 text-sm"
                >
                  Regenerate
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
