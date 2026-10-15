"use client";
import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { Settings, User } from "lucide-react";
import { useBirthProfile } from "@/context/BirthProfileContext";

export function ProfileMenu() {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  const { birth } = useBirthProfile();

  useEffect(() => {
    const close = (e: MouseEvent | KeyboardEvent) => {
      if (e instanceof KeyboardEvent ? e.key === "Escape" : !ref.current?.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", close);
    document.addEventListener("keydown", close);
    return () => { document.removeEventListener("mousedown", close); document.removeEventListener("keydown", close); };
  }, []);

  return (
    <div ref={ref} className="relative">
      <button onClick={() => setOpen((o) => !o)} aria-haspopup="menu" aria-expanded={open} aria-label="Profile menu"
        className="flex h-9 w-9 items-center justify-center rounded-full border border-white/15 bg-night-800 hover:border-gold-400">
        <User className="h-4 w-4" aria-hidden />
      </button>
      {open && (
        <div role="menu" className="panel absolute right-0 z-40 mt-2 w-64 space-y-1 p-2 shadow-xl">
          <p className="px-3 py-2 text-xs text-slate-400">
            {birth ? `Birth details entered${birth.name ? ` for ${birth.name}` : ""}.` : "No birth details entered yet."}
            {" "}AstroBuddy has no sign-in yet.
          </p>
          <Link role="menuitem" href="/" onClick={() => setOpen(false)} className="block rounded-lg px-3 py-2 text-sm hover:bg-white/5">Birth details</Link>
          <Link role="menuitem" href="/settings" onClick={() => setOpen(false)} className="flex items-center gap-2 rounded-lg px-3 py-2 text-sm hover:bg-white/5">
            <Settings className="h-4 w-4" aria-hidden /> Settings
          </Link>
        </div>
      )}
    </div>
  );
}
