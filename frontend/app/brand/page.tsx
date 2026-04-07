"use client";

import { useState } from "react";
import { api } from "@/lib/api";

const tones = ["Professional", "Witty", "Warm", "Bold", "Minimalist", "Playful", "Authoritative"];

export default function BrandPage() {
  const [sel, setSel] = useState<string[]>([]);
  const [msg, setMsg] = useState("");
  const toggle = (t: string) => {
    setSel((prev) => {
      if (prev.includes(t)) return prev.filter((x) => x !== t);
      if (prev.length >= 3) return prev;
      return [...prev, t];
    });
  };

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (sel.length !== 3) {
      setMsg("Choose exactly 3 brand tones (assignment requires three picks).");
      return;
    }
    const fd = new FormData(e.currentTarget);
    const body = {
      brand_name: String(fd.get("brand_name")),
      industry: String(fd.get("industry")),
      audience_age: String(fd.get("audience_age")),
      audience_interests: String(fd.get("audience_interests")),
      audience_pain_points: String(fd.get("audience_pain_points")),
      brand_tones: sel,
      keywords_include: String(fd.get("keywords_include")),
      keywords_avoid: String(fd.get("keywords_avoid")),
    };
    try {
      const res = await api<{ id: string }>("/brands", { method: "POST", body: JSON.stringify(body) });
      localStorage.setItem("lastBrandId", res.id);
      setMsg(`Saved brand profile · ID ${res.id}`);
    } catch (err: unknown) {
      setMsg(err instanceof Error ? err.message : "Error");
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-[family-name:var(--font-display)] text-3xl font-semibold">Brand context</h1>
        <p className="text-slate-600">Pick exactly three tones. Everything downstream respects this.</p>
      </div>
      <form onSubmit={onSubmit} className="space-y-4 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="grid gap-4 md:grid-cols-2">
          <label className="space-y-1">
            <span className="text-sm font-medium">Brand name</span>
            <input name="brand_name" required className="w-full rounded-lg border px-3 py-2" />
          </label>
          <label className="space-y-1">
            <span className="text-sm font-medium">Industry</span>
            <input name="industry" required className="w-full rounded-lg border px-3 py-2" />
          </label>
          <label className="space-y-1 md:col-span-2">
            <span className="text-sm font-medium">Audience — age</span>
            <input name="audience_age" className="w-full rounded-lg border px-3 py-2" placeholder="e.g. 25–40" />
          </label>
          <label className="space-y-1 md:col-span-2">
            <span className="text-sm font-medium">Interests</span>
            <textarea name="audience_interests" className="w-full rounded-lg border px-3 py-2" rows={2} />
          </label>
          <label className="space-y-1 md:col-span-2">
            <span className="text-sm font-medium">Pain points</span>
            <textarea name="audience_pain_points" className="w-full rounded-lg border px-3 py-2" rows={2} />
          </label>
        </div>
        <div>
          <p className="text-sm font-medium">Brand tone (exactly 3)</p>
          <div className="mt-2 flex flex-wrap gap-2">
            {tones.map((t) => (
              <button
                type="button"
                key={t}
                onClick={() => toggle(t)}
                className={`rounded-full border px-3 py-1 text-sm ${
                  sel.includes(t) ? "border-accent bg-blue-50 text-accent" : "border-slate-200 bg-white"
                }`}
              >
                {t}
              </button>
            ))}
          </div>
        </div>
        <label className="space-y-1 block">
          <span className="text-sm font-medium">Keywords to include</span>
          <input name="keywords_include" className="w-full rounded-lg border px-3 py-2" />
        </label>
        <label className="space-y-1 block">
          <span className="text-sm font-medium">Words to avoid</span>
          <input name="keywords_avoid" className="w-full rounded-lg border px-3 py-2" />
        </label>
        <button type="submit" className="rounded-xl bg-accent px-4 py-2 text-white">
          Save brand profile
        </button>
        {msg && <p className="text-sm text-slate-700">{msg}</p>}
      </form>
    </div>
  );
}
