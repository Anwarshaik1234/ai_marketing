"use client";

import { useMemo, useState } from "react";
import { uploadFile } from "@/lib/api";

type Report = {
  positive_pct?: number;
  neutral_pct?: number;
  negative_pct?: number;
  trend?: string;
  voc_paragraph?: string;
  positive_themes?: { theme: string; example: string }[];
  negative_themes?: { theme: string; example: string }[];
  emotional_highlights?: string[];
  campaign_angles?: string[];
  wordcloud?: { text: string; value: number }[];
};

export default function SentimentPage() {
  const [report, setReport] = useState<Report | null>(null);
  const [col, setCol] = useState("text");

  async function onFile(e: React.ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0];
    if (!f) return;
    const fd = new FormData();
    fd.append("file", f);
    fd.append("text_column", col);
    const res = await uploadFile<Report & { report_id: string }>("/sentiment/upload", fd);
    setReport(res);
  }

  const maxVal = useMemo(() => Math.max(1, ...(report?.wordcloud?.map((w) => w.value) || [1])), [report]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-[family-name:var(--font-display)] text-3xl font-semibold">Audience &amp; sentiment</h1>
        <p className="text-slate-600">Upload a CSV with a text column of reviews or comments.</p>
      </div>
      <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm space-y-3">
        <label className="space-y-1 block">
          <span className="text-sm font-medium">Text column name</span>
          <input value={col} onChange={(e) => setCol(e.target.value)} className="w-full rounded-lg border px-3 py-2" />
        </label>
        <input type="file" accept=".csv,text/csv" onChange={onFile} />
      </div>
      {report && (
        <div className="space-y-4">
          <div className="flex flex-wrap items-center gap-3 rounded-2xl border border-slate-200 bg-white px-4 py-3">
            <p className="text-sm font-medium text-slate-700">Trend</p>
            <span className="rounded-full bg-slate-100 px-3 py-1 text-sm font-semibold capitalize text-slate-800">
              {report.trend ?? "—"}
            </span>
            <span className="text-xs text-slate-500">vs. prior period (model estimate from sample)</span>
          </div>
          <div className="grid gap-4 md:grid-cols-3">
            <div className="rounded-2xl border border-slate-200 bg-white p-4">
              <p className="text-xs uppercase text-slate-500">Positive</p>
              <p className="text-3xl font-semibold text-emerald-600">{report.positive_pct ?? "—"}%</p>
            </div>
            <div className="rounded-2xl border border-slate-200 bg-white p-4">
              <p className="text-xs uppercase text-slate-500">Neutral</p>
              <p className="text-3xl font-semibold text-slate-700">{report.neutral_pct ?? "—"}%</p>
            </div>
            <div className="rounded-2xl border border-slate-200 bg-white p-4">
              <p className="text-xs uppercase text-slate-500">Negative</p>
              <p className="text-3xl font-semibold text-rose-600">{report.negative_pct ?? "—"}%</p>
            </div>
          </div>
          <div className="rounded-2xl border border-slate-200 bg-white p-4">
            <p className="font-semibold">Voice of customer</p>
            <p className="mt-2 text-sm text-slate-700">{report.voc_paragraph}</p>
          </div>
          {report.emotional_highlights && report.emotional_highlights.length > 0 && (
            <div className="rounded-2xl border border-rose-100 bg-rose-50/50 p-4">
              <p className="font-semibold text-rose-900">High-impact comments</p>
              <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-slate-800">
                {report.emotional_highlights.map((h, i) => (
                  <li key={i}>{h}</li>
                ))}
              </ul>
            </div>
          )}
          {report.campaign_angles && report.campaign_angles.length > 0 && (
            <div className="rounded-2xl border border-accent/30 bg-blue-50/40 p-4">
              <p className="font-semibold text-accent">Suggested campaign angles</p>
              <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-slate-800">
                {report.campaign_angles.map((a, i) => (
                  <li key={i}>{a}</li>
                ))}
              </ul>
            </div>
          )}
          <div className="grid gap-4 md:grid-cols-2">
            <div className="rounded-2xl border border-slate-200 bg-white p-4">
              <p className="font-semibold">Positive themes</p>
              <ul className="mt-2 list-disc space-y-1 pl-5 text-sm">
                {report.positive_themes?.map((t, i) => (
                  <li key={i}>
                    <span className="font-medium">{t.theme}</span> — {t.example}
                  </li>
                ))}
              </ul>
            </div>
            <div className="rounded-2xl border border-slate-200 bg-white p-4">
              <p className="font-semibold">Negative themes</p>
              <ul className="mt-2 list-disc space-y-1 pl-5 text-sm">
                {report.negative_themes?.map((t, i) => (
                  <li key={i}>
                    <span className="font-medium">{t.theme}</span> — {t.example}
                  </li>
                ))}
              </ul>
            </div>
          </div>
          <div className="rounded-2xl border border-dashed border-slate-300 bg-white p-4">
            <p className="font-semibold">Word cloud (frequency)</p>
            <div className="mt-3 flex flex-wrap gap-2">
              {report.wordcloud?.slice(0, 40).map((w, i) => (
                <span
                  key={`${w.text}-${i}`}
                  className="text-slate-800"
                  style={{ fontSize: `${12 + (w.value / maxVal) * 18}px` }}
                >
                  {w.text}
                </span>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
