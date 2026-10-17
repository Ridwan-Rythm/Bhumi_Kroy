import type {
  CheckRequest,
  DemoLedger,
  Locations,
  PubKey,
  Report,
  SamplePlot,
  VerifyRequest,
  VerifyResult,
} from "../types/contract";
import { ApiError } from "../api/errors";
import { toAsciiDigits } from "../lib/digits";

// Fixtures are added in step B1.1. Until then every lookup fails with MOCK_MISSING.
const modules = import.meta.glob("./*.json", { eager: true, import: "default" }) as Record<string, unknown>;

function fixture<T>(name: string): T {
  const hit = modules[`./${name}.json`];
  if (hit === undefined) {
    throw new ApiError("MOCK_MISSING", `Missing mock fixture: ${name}.json`);
  }
  return hit as T;
}

// plot_id (sample) -> fixture. Only the five fixtures required by B1.1 exist; others are not faked.
const REPORT_BY_SAMPLE: Record<string, string> = {
  "P-001": "report_green",
  "P-008B": "report_green",
  "P-003": "report_red",
  "P-007": "report_amber",
  "P-009": "report_grey",
};

export const mockLocations = () => fixture<Locations>("locations");
export const mockSamples = () => fixture<SamplePlot[]>("samples");
export const mockPubKey = () => fixture<PubKey>("pubkey");

function samePlot(a: CheckRequest, b: CheckRequest): boolean {
  return (
    a.plot.mouza_id === b.plot.mouza_id &&
    toAsciiDigits(a.plot.khatian_no) === toAsciiDigits(b.plot.khatian_no) &&
    toAsciiDigits(a.plot.dag_no) === toAsciiDigits(b.plot.dag_no) &&
    a.seller.name.trim() === b.seller.name.trim() &&
    (a.seller.father_or_husband ?? "").trim() === (b.seller.father_or_husband ?? "").trim()
  );
}

export function mockCheck(req: CheckRequest): Report {
  const sample = mockSamples().find((s) => samePlot(s.request, req));
  const name = sample ? REPORT_BY_SAMPLE[sample.sample_id] : undefined;
  if (!name) {
    throw new ApiError("MOCK_MISSING", "No mock fixture matches this plot request.");
  }
  return fixture<Report>(name);
}

const ALL_REPORTS = ["report_green", "report_grey", "report_amber", "report_red", "report_integrity"];

export function mockGetReport(reportId: string): Report {
  for (const name of ALL_REPORTS) {
    if (modules[`./${name}.json`] === undefined) continue;
    const r = fixture<Report>(name);
    if (r.report_id === reportId) return r;
  }
  throw new ApiError("NOT_FOUND", "Report not found", null, 404);
}

// One fixture per VerifyResult state: verify_genuine_current.json, verify_tampered.json, ...
export function mockVerify(req: VerifyRequest): VerifyResult {
  if ("short_code" in req) {
    const known = ALL_REPORTS.filter((n) => modules[`./${n}.json`] !== undefined)
      .map((n) => fixture<Report>(n))
      .some((r) => r.short_code === req.short_code);
    return fixture<VerifyResult>(known ? "verify_genuine_current" : "verify_unknown");
  }
  return fixture<VerifyResult>(
    req.signature_b64.includes("tampered") ? "verify_tampered" : "verify_genuine_current",
  );
}

export const mockDemoLedger = (plotId: string) => {
  const l = fixture<DemoLedger>("demo_ledger");
  return { ...l, plot_id: plotId };
};
