// Locale-aware dates and numbers. Bangla mode shows Bangla digits (bn-BD); names and record IDs are never touched.
const locale = (lang: string) => (lang === "bn" ? "bn-BD" : "en-GB");

export function fmtNumber(n: number, lang: string): string {
  return new Intl.NumberFormat(locale(lang), { maximumFractionDigits: 2 }).format(n);
}

const DATE_ONLY = /^\d{4}-\d{2}-\d{2}$/;

// "2026-10-17" stays a calendar date (no time-zone shift); a full timestamp is shown in Dhaka time.
export function fmtDate(iso: string, lang: string): string {
  const d = DATE_ONLY.test(iso) ? new Date(`${iso}T12:00:00Z`) : new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  return new Intl.DateTimeFormat(locale(lang), { dateStyle: "medium", timeZone: DATE_ONLY.test(iso) ? "UTC" : "Asia/Dhaka" }).format(d);
}

export function fmtDateTime(iso: string, lang: string): string {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  return new Intl.DateTimeFormat(locale(lang), { dateStyle: "medium", timeStyle: "short", timeZone: "Asia/Dhaka" }).format(d);
}

export const looksLikeIso = (v: string): boolean => /^\d{4}-\d{2}-\d{2}(T|$)/.test(v);
