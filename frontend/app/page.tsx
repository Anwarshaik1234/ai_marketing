import Link from "next/link";

export default function Page() {
  return (
    <div className="space-y-8">
      <header className="space-y-3">
        <p className="text-sm font-semibold uppercase tracking-wide text-accent">Workspace</p>
        <h1 className="font-[family-name:var(--font-display)] text-4xl font-semibold text-ink">
          AI Marketing Intelligence &amp; Content Engine
        </h1>
        <p className="max-w-2xl text-lg text-slate-600">
          Define brand context once, generate coordinated multi-channel assets, repurpose long-form sources, run ad
          experiments, read the voice of the customer, and schedule everything on one calendar.
        </p>
      </header>
      <div className="grid gap-4 md:grid-cols-2">
        {[
          { href: "/brand", title: "1 · Brand & campaign", desc: "Tone, guardrails, goals, platform validation" },
          { href: "/hub", title: "2 · Content hub", desc: "All formats from one brief + refinements" },
          { href: "/repurpose", title: "3 · Repurpose", desc: "Coverage map & attributed outputs" },
          { href: "/ads", title: "4 · Ad lab", desc: "Five variants, labels, export CSV" },
          { href: "/sentiment", title: "5 · Sentiment", desc: "Themes, VoC, word cloud" },
          { href: "/calendar", title: "6 · Calendar", desc: "Drag-drop, gaps, AI schedule" },
          { href: "/bonus", title: "Bonus", desc: "Competitor counter & tone consistency score" },
        ].map((c) => (
          <Link
            key={c.href}
            href={c.href}
            className="group rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition hover:border-accent/40 hover:shadow-md"
          >
            <h2 className="text-lg font-semibold text-ink group-hover:text-accent">{c.title}</h2>
            <p className="mt-2 text-slate-600">{c.desc}</p>
          </Link>
        ))}
      </div>
    </div>
  );
}
