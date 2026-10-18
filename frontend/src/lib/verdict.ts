import type { Verdict } from "../types/contract";

// Colour is never the only signal (standing rule 6): every verdict also has an icon and a word.
export const VERDICT_STYLE: Record<Verdict, { icon: string; box: string }> = {
  GREEN: { icon: "✓", box: "border-verdict-green bg-green-50 text-verdict-green" },
  GREY: { icon: "?", box: "border-verdict-grey bg-gray-100 text-verdict-grey" },
  AMBER: { icon: "!", box: "border-verdict-amber bg-amber-50 text-verdict-amber" },
  RED: { icon: "✕", box: "border-verdict-red bg-red-50 text-verdict-red" },
  INTEGRITY_ALERT: { icon: "⚠", box: "border-verdict-integrity bg-violet-50 text-verdict-integrity" },
};

export const SEVERITY_STYLE: Record<string, string> = {
  INTEGRITY: "bg-violet-100 text-violet-900",
  CRITICAL: "bg-red-100 text-red-900",
  HIGH: "bg-orange-100 text-orange-900",
  MEDIUM: "bg-amber-100 text-amber-900",
  INFO: "bg-blue-100 text-blue-900",
  COVERAGE: "bg-gray-200 text-gray-900",
};
