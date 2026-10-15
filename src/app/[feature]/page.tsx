import { notFound } from "next/navigation";
import Link from "next/link";
import { ALL_FEATURES } from "@/lib/nav";

export function generateStaticParams() {
  return ALL_FEATURES.map((f) => ({ feature: f.slug }));
}
export const dynamicParams = false;

// Stage 1 placeholder. Each route is replaced by its real page in later stages.
export default function FeaturePage({ params }: { params: { feature: string } }) {
  const f = ALL_FEATURES.find((x) => x.slug === params.feature);
  if (!f) notFound();
  const Icon = f.icon;
  return (
    <div className="space-y-6">
      <h1 className="flex items-center gap-3 font-display text-4xl font-semibold text-slate-50">
        <Icon className="h-7 w-7 text-violet-400" aria-hidden /> {f.title}
      </h1>
      <p className="max-w-xl text-slate-400">{f.blurb}</p>
      <div className="panel max-w-xl space-y-3 p-5">
        <p className="font-medium text-gold-300">Not built yet</p>
        <p className="text-sm text-slate-300">This page is scheduled for a later stage. It will call these service functions:</p>
        <ul className="flex flex-wrap gap-2">
          {f.services.map((s) => <li key={s}><code className="rounded bg-night-900 px-2 py-1 text-xs text-violet-300">{s}</code></li>)}
        </ul>
        <Link href="/" className="btn-ghost">Back to dashboard</Link>
      </div>
    </div>
  );
}
