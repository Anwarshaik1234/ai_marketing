import Link from "next/link";
import clsx from "clsx";

const links = [
  { href: "/", label: "Home" },
  { href: "/brand", label: "Brand" },
  { href: "/campaign", label: "Campaign" },
  { href: "/hub", label: "Content hub" },
  { href: "/repurpose", label: "Repurpose" },
  { href: "/ads", label: "Ad lab" },
  { href: "/sentiment", label: "Sentiment" },
  { href: "/calendar", label: "Calendar" },
  { href: "/bonus", label: "Bonus" },
];

export function Nav() {
  return (
    <nav className="flex flex-wrap gap-2 border-b border-slate-200 bg-white/80 px-4 py-3 backdrop-blur">
      {links.map((l) => (
        <Link
          key={l.href}
          href={l.href}
          className={clsx(
            "rounded-full px-3 py-1 text-sm font-medium text-slate-700 hover:bg-slate-100",
          )}
        >
          {l.label}
        </Link>
      ))}
    </nav>
  );
}
