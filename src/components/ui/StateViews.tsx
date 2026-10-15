import { AlertTriangle, Inbox, Loader2, RefreshCw, FlaskConical } from "lucide-react";
import type { ReactNode } from "react";

export function LoadingState({ label = "Loading…" }: { label?: string }) {
  return (
    <div role="status" className="flex items-center gap-3 p-6 text-sm text-slate-300">
      <Loader2 className="h-4 w-4 animate-spin text-gold-400" aria-hidden /> {label}
    </div>
  );
}

export function EmptyState({ title, hint, action }: { title: string; hint?: string; action?: ReactNode }) {
  return (
    <div className="flex flex-col items-center gap-2 p-8 text-center">
      <Inbox className="h-6 w-6 text-violet-400" aria-hidden />
      <p className="font-medium text-slate-100">{title}</p>
      {hint && <p className="max-w-sm text-sm text-slate-400">{hint}</p>}
      {action}
    </div>
  );
}

export function ErrorState({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div role="alert" className="flex flex-col items-start gap-3 rounded-xl border border-red-400/30 bg-red-950/30 p-4">
      <p className="flex items-start gap-2 text-sm text-red-200">
        <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" aria-hidden /> {message}
      </p>
      {onRetry && (
        <button onClick={onRetry} className="btn-ghost">
          <RefreshCw className="h-4 w-4" aria-hidden /> Try again
        </button>
      )}
    </div>
  );
}

/** Marks any content that is illustrative and not a real user result. */
export function DemoBadge() {
  return (
    <span className="inline-flex items-center gap-1 rounded-full border border-gold-500/40 bg-gold-500/10 px-2 py-0.5 text-xs text-gold-300">
      <FlaskConical className="h-3 w-3" aria-hidden /> Demo data, not your result
    </span>
  );
}
