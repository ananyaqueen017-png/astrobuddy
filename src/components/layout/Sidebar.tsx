"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard } from "lucide-react";
import { NAV_GROUPS } from "@/lib/nav";

export function Sidebar({ onNavigate }: { onNavigate?: () => void }) {
  const pathname = usePathname();
  const link = (href: string, active: boolean) =>
    `flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors ${
      active ? "bg-violet-500/20 text-gold-300" : "text-slate-300 hover:bg-white/5 hover:text-white"
    }`;

  return (
    <nav aria-label="Main" className="flex h-full flex-col gap-5 overflow-y-auto p-4">
      <Link href="/" onClick={onNavigate} className="px-3 pt-1 font-display text-2xl font-semibold text-gold-300">
        AstroBuddy
      </Link>
      <Link href="/" onClick={onNavigate} aria-current={pathname === "/" ? "page" : undefined} className={link("/", pathname === "/")}>
        <LayoutDashboard className="h-4 w-4" aria-hidden /> Dashboard
      </Link>
      {NAV_GROUPS.map((group) => (
        <div key={group.label}>
          <p className="mb-1 px-3 text-xs text-slate-500">{group.label}</p>
          <ul className="space-y-0.5">
            {group.items.map(({ slug, title, icon: Icon }) => {
              const href = `/${slug}`;
              const active = pathname === href;
              return (
                <li key={slug}>
                  <Link href={href} onClick={onNavigate} aria-current={active ? "page" : undefined} className={link(href, active)}>
                    <Icon className="h-4 w-4 shrink-0" aria-hidden /> <span className="truncate">{title}</span>
                  </Link>
                </li>
              );
            })}
          </ul>
        </div>
      ))}
    </nav>
  );
}
