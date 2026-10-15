import {
  Orbit, Clock3, MessageCircle, Sparkles, CalendarDays, BookOpen, BarChart3,
  Hourglass, Briefcase, HeartHandshake, GraduationCap, History, FlaskConical,
  type LucideIcon,
} from "lucide-react";

export interface FeatureItem {
  slug: string;
  title: string;
  blurb: string;
  icon: LucideIcon;
  services: string[]; // service functions this page will use
}
export interface NavGroup { label: string; items: FeatureItem[] }

export const NAV_GROUPS: NavGroup[] = [
  { label: "Chart", items: [
    { slug: "living-kundli", title: "Living Kundli", blurb: "Explore planets and houses on an interactive chart.", icon: Orbit, services: ["calculateChart"] },
    { slug: "dasha-timeline", title: "Dasha Timeline", blurb: "Browse major and sub-periods across your life.", icon: Hourglass, services: ["getDashas"] },
    { slug: "time-machine", title: "Astro Time Machine", blurb: "Compare your chart state on any two dates.", icon: History, services: ["getTransits", "calculateChart"] },
  ]},
  { label: "Timing", items: [
    { slug: "why-now", title: "Why Is This Happening Now?", blurb: "See the transits and periods behind this moment.", icon: Clock3, services: ["getTransits", "getDashas"] },
    { slug: "calendar", title: "Personality Astro Calendar", blurb: "A monthly view of meaningful dates.", icon: CalendarDays, services: ["listCalendarEntries"] },
  ]},
  { label: "Guidance", items: [
    { slug: "ask-kundli", title: "Ask Your Kundli", blurb: "Ask questions and see the chart factors behind each answer.", icon: MessageCircle, services: ["askKundli"] },
    { slug: "personality", title: "Personality Engine", blurb: "A personalized interpretation dashboard.", icon: Sparkles, services: ["calculateChart", "askKundli"] },
    { slug: "career-explorer", title: "Career Explorer", blurb: "Match your interests with chart indications.", icon: Briefcase, services: ["calculateChart", "askKundli"] },
    { slug: "compatibility", title: "Deeper Compatibility", blurb: "Compare two charts by clear categories.", icon: HeartHandshake, services: ["compareCompatibility"] },
  ]},
  { label: "Reflect", items: [
    { slug: "journal", title: "Astrology Journal", blurb: "Write, tag, search and filter your entries.", icon: BookOpen, services: ["listJournalEntries", "createJournalEntry"] },
    { slug: "analytics", title: "Astrology + Data Analytics", blurb: "Timelines and comparisons from your own data.", icon: BarChart3, services: ["getTransits", "listJournalEntries"] },
  ]},
  { label: "Learn & Experiment", items: [
    { slug: "learning", title: "Astrology Learning Mode", blurb: "Lessons, quizzes and Learn My Chart.", icon: GraduationCap, services: ["calculateChart"] },
    { slug: "lab", title: "Astrology Lab", blurb: "Run comparison experiments side by side.", icon: FlaskConical, services: ["runLabComparison"] },
  ]},
];

export const ALL_FEATURES = NAV_GROUPS.flatMap((g) => g.items);
