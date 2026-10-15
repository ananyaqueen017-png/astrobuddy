"use client";
import { ApiStatus } from "@/components/ApiStatus";
import { useBirthProfile } from "@/context/BirthProfileContext";
import { getApiBaseUrl, isApiConfigured } from "@/lib/api/client";

export default function SettingsPage() {
  const { birth, clear } = useBirthProfile();
  return (
    <div className="space-y-6">
      <h1 className="font-display text-4xl font-semibold text-slate-50">Settings</h1>
      <section className="panel max-w-xl space-y-3 p-5">
        <h2 className="font-display text-2xl text-gold-300">Backend connection</h2>
        <p className="break-all text-sm text-slate-300">
          API URL: {isApiConfigured() ? getApiBaseUrl() : "not set. Add NEXT_PUBLIC_API_BASE_URL to .env.local."}
        </p>
        <ApiStatus />
      </section>
      <section className="panel max-w-xl space-y-3 p-5">
        <h2 className="font-display text-2xl text-gold-300">Saved birth details</h2>
        <p className="text-sm text-slate-300">
          Stored only in this browser. {birth ? "Details are currently saved." : "Nothing is saved."}
        </p>
        <button className="btn-ghost" disabled={!birth} onClick={clear}>Clear saved details</button>
      </section>
    </div>
  );
}
