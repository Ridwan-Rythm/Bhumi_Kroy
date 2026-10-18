import type { Report } from "../types/contract";

// Keeps reports in memory so the Result page does not refetch what the Checking page just received.
// An INTEGRITY_ALERT report has no report_id, so it lives under the key "alert".
const store = new Map<string, Report>();
export const ALERT_KEY = "alert";

export function remember(report: Report): string {
  const key = report.report_id ?? ALERT_KEY;
  store.set(key, report);
  return key;
}

export const recall = (key: string): Report | undefined => store.get(key);
