"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

const platforms = ["LinkedIn", "Instagram", "Email", "Google Ads", "Twitter"];
const goals = ["Awareness", "Lead Gen", "Retention", "Product Launch"];

export default function CampaignPage() {
  const [brandId, setBrandId] = useState("");
  const [picked, setPicked] = useState<string[]>([]);
  const [notes, setNotes] = useState<string[]>([]);
  const [msg, setMsg] = useState("");

  useEffect(() => {
    setBrandId(localStorage.getItem("lastBrandId") || "");
  }, []);

  const toggle = (p: string) => {
    setPicked((prev) => (prev.includes(p) ? prev.filter((x) => x !== p) : [...prev, p]));
  };

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (!brandId) {
      setMsg("Set a brand ID (save brand first)");
      return;
    }
    const fd = new FormData(e.currentTarget);
    const startStr = String(fd.get("start_date") || "");
    const endStr = String(fd.get("end_date") || "");
    const body = {
      brand_id: brandId,
      name: String(fd.get("name")),
      goal: String(fd.get("goal")),
      start_date: startStr ? startStr : null,
      end_date: endStr ? endStr : null,
      platforms: picked,
    };
    try {
      const res = await api<{
        campaign: { id: string };
        validation_notes: string;
        suggestions: string[];
      }>("/campaigns", { method: "POST", body: JSON.stringify(body) });
      localStorage.setItem("lastCampaignId", res.campaign.id);
      setNotes([res.validation_notes, ...res.suggestions]);
      setMsg(`Campaign ${res.campaign.id} saved`);
    } catch (err: unknown) {
      setMsg(err instanceof Error ? err.message : "Error");
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-[family-name:var(--font-display)] text-3xl font-semibold">Campaign setup</h1>
        <p className="text-slate-600">AI validates tone vs platform mix after save.</p>
      </div>
      <form onSubmit={onSubmit} className="space-y-4 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <label className="space-y-1 block">
          <span className="text-sm font-medium">Brand ID</span>
          <input
            value={brandId}
            onChange={(e) => setBrandId(e.target.value)}
            className="w-full rounded-lg border px-3 py-2"
            placeholder="Paste from Brand page"
          />
        </label>
        <label className="space-y-1 block">
          <span className="text-sm font-medium">Campaign name</span>
          <input name="name" required className="w-full rounded-lg border px-3 py-2" />
        </label>
        <label className="space-y-1 block">
          <span className="text-sm font-medium">Goal</span>
          <select name="goal" className="w-full rounded-lg border px-3 py-2">
            {goals.map((g) => (
              <option key={g}>{g}</option>
            ))}
          </select>
        </label>
        <div className="grid gap-4 md:grid-cols-2">
          <label className="space-y-1">
            <span className="text-sm font-medium">Start</span>
            <input name="start_date" type="date" className="w-full rounded-lg border px-3 py-2" />
          </label>
          <label className="space-y-1">
            <span className="text-sm font-medium">End</span>
            <input name="end_date" type="date" className="w-full rounded-lg border px-3 py-2" />
          </label>
        </div>
        <div>
          <p className="text-sm font-medium">Platforms</p>
          <div className="mt-2 flex flex-wrap gap-2">
            {platforms.map((p) => (
              <button
                type="button"
                key={p}
                onClick={() => toggle(p)}
                className={`rounded-full border px-3 py-1 text-sm ${
                  picked.includes(p) ? "border-coral bg-orange-50 text-coral" : "border-slate-200"
                }`}
              >
                {p}
              </button>
            ))}
          </div>
        </div>
        <button type="submit" className="rounded-xl bg-accent px-4 py-2 text-white">
          Create campaign
        </button>
        {msg && <p className="text-sm">{msg}</p>}
        {notes.length > 0 && (
          <div className="rounded-xl bg-slate-50 p-4 text-sm text-slate-700">
            <p className="font-semibold">AI validation</p>
            <ul className="mt-2 list-disc space-y-1 pl-5">
              {notes.map((n, i) => (
                <li key={i}>{n}</li>
              ))}
            </ul>
          </div>
        )}
      </form>
    </div>
  );
}
