import type { TFunction } from "i18next";
import type { Finding, NotChecked } from "../types/contract";
import { fmtDate, fmtNumber, looksLikeIso } from "./format";

type Params = Record<string, string | number | boolean | null>;

// Source and report fields hold codes ("land_records", "WEAK", "BS", ISO dates). Before they go into a
// sentence they are turned into words in the active language. Anything unknown is shown as it is.
export function localizeParams(t: TFunction, lang: string, params: Params, ruleId = ""): Record<string, string> {
  const out: Record<string, string> = {};
  for (const [key, value] of Object.entries(params)) {
    out[key] = one(t, lang, key, value, ruleId);
  }
  if (typeof params.applicant_is_seller === "boolean") {
    out.applicant_note = t(params.applicant_is_seller ? "rules.applicantSeller" : "rules.applicantOther");
  }
  return out;
}

function one(t: TFunction, lang: string, key: string, value: string | number | boolean | null, ruleId: string): string {
  if (value === null || value === undefined) return t("common.notAvailable");
  if (typeof value === "number") return fmtNumber(value, lang);
  if (typeof value === "boolean") return t(value ? "common.done" : "common.none");
  const tryKey = (k: string) => (t(k, { defaultValue: "" }) as string) || value;
  if (["source", "source_a", "source_b"].includes(key)) return tryKey(`sources.${value}`);
  if (key === "from_survey" || key === "to_survey") return tryKey(`surveyShort.${value}`);
  if (key === "tier") return tryKey(`matchTier.${value}`);
  if (key === "linkage") return tryKey(`linkage.${value}`);
  if (key === "reason") return ruleId === "R-INT-01" ? tryKey(`ledgerReason.${value}`) : tryKey(`reasons.${value}`);
  if (key === "maturity") return value;
  if (looksLikeIso(value)) return fmtDate(value, lang);
  return value;
}

const RULES_WITH_TEXT = new Set<string>();

export function ruleKey(t: TFunction, ruleId: string, part: "title" | "explain" | "next"): string {
  const k = `rules.${ruleId}.${part}`;
  if (RULES_WITH_TEXT.has(ruleId)) return k;
  if (t(k, { defaultValue: "" })) {
    RULES_WITH_TEXT.add(ruleId);
    return k;
  }
  return `rules.fallback.${part}`; // an unknown rule_id never crashes the page
}

export function findingText(t: TFunction, lang: string, f: Finding) {
  const vars = { ...localizeParams(t, lang, f.params, f.rule_id), rule_id: f.rule_id };
  return {
    title: t(ruleKey(t, f.rule_id, "title"), vars),
    explain: t(ruleKey(t, f.rule_id, "explain"), vars),
    next: t(ruleKey(t, f.rule_id, "next"), vars),
  };
}

export function notCheckedText(t: TFunction, lang: string, n: NotChecked): string {
  const key = `notChecked.${n.code}`;
  const exists = Boolean(t(key, { defaultValue: "" }));
  return t(exists ? key : "notChecked.fallback", localizeParams(t, lang, n.params));
}
