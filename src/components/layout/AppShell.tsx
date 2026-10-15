"use client";
import { useEffect, useState, type ReactNode } from "react";
import { usePathname } from "next/navigation";
import { Menu, X } from "lucide-react";
import { Sidebar } from "./Sidebar";
import { ProfileMenu } from "./ProfileMenu";

export function AppShell({ children }: { children: ReactNode }) {
  const [open, setOpen] = useState(false);
  const pathname = usePathname();

  useEffect(() => setOpen(false), [pathname]);
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && setOpen(false);
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, []);

  return (
    <div className="min-h-screen lg:grid lg:grid-cols-[17rem_1fr]">
      <aside className="sticky top-0 hidden h-screen border-r border-white/10 bg-night-900/80 lg:block">
        <Sidebar />
      </aside>

      {open && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <button aria-label="Close menu" className="absolute inset-0 bg-black/60" onClick={() => setOpen(false)} />
          <aside className="relative h-full w-72 max-w-[85vw] border-r border-white/10 bg-night-900">
            <button aria-label="Close menu" onClick={() => setOpen(false)} className="absolute right-3 top-3 rounded-lg p-2 hover:bg-white/5">
              <X className="h-5 w-5" aria-hidden />
            </button>
            <Sidebar onNavigate={() => setOpen(false)} />
          </aside>
        </div>
      )}

      <div className="min-w-0">
        <header className="sticky top-0 z-30 flex items-center justify-between border-b border-white/10 bg-night-950/80 px-4 py-3 backdrop-blur sm:px-6">
          <button aria-label="Open menu" aria-expanded={open} onClick={() => setOpen(true)} className="rounded-lg p-2 hover:bg-white/5 lg:hidden">
            <Menu className="h-5 w-5" aria-hidden />
          </button>
          <span className="font-display text-xl text-gold-300 lg:hidden">AstroBuddy</span>
          <span className="hidden lg:block" />
          <ProfileMenu />
        </header>
        <main className="mx-auto w-full max-w-6xl px-4 py-8 sm:px-6">{children}</main>
      </div>
    </div>
  );
}
