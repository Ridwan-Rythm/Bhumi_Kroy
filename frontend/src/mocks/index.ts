import nacl from "tweetnacl";
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

// Fixtures are generated from the REAL API by `cd backend && python -m scripts.export_mocks`.
const modules = import.meta.glob("./*.json", { eager: true, import: "default" }) as Record<string, unknown>;

function fixture<T>(name: string): T {
  const hit = modules[`./${name}.json`];
  if (hit === undefined) {
    throw new ApiError("MOCK_MISSING", `Missing mock fixture: ${name}.json`);
  }
  return hit as T;
}

export const mockLocations = () => fixture<Locations>("locations");
export const mockSamples = () => fixture<SamplePlot[]>("samples");
export const mockPubKey = () => fixture<PubKey>("pubkey");

const reportFixtureName = (sampleId: string) => `report_${sampleId.replace("-", "")}`;
const allReports = (): Report[] =>
  Object.keys(modules)
    .filter((k) => /^\.\/report_.*\.json$/.test(k))
    .map((k) => modules[k] as Report);

// Same normalisation as the backend: ASCII digits, collapsed whitespace, case-insensitive short codes.
const num = (s: string) => toAsciiDigits(s).replace(/\s+/g, "");
const text = (s: string | undefined | null) => (s ?? "").normalize("NFC").replace(/\s+/g, " ").trim();

function samePlot(a: CheckRequest, b: CheckRequest): boolean {
  return (
    a.plot.district_id === b.plot.district_id &&
    a.plot.upazila_id === b.plot.upazila_id &&
    a.plot.mouza_id === b.plot.mouza_id &&
    (a.plot.survey ?? null) === (b.plot.survey ?? null) &&
    num(a.plot.khatian_no) === num(b.plot.khatian_no) &&
    num(a.plot.dag_no) === num(b.plot.dag_no) &&
    text(a.seller.name) === text(b.seller.name) &&
    text(a.seller.father_or_husband) === text(b.seller.father_or_husband) &&
    (a.consents?.bank ?? true) === (b.consents?.bank ?? true)
  );
}

export function mockCheck(req: CheckRequest): Report {
  const sample = mockSamples().find((s) => samePlot(s.request, req));
  if (!sample) {
    throw new ApiError("MOCK_MISSING", "No mock fixture matches this plot request.");
  }
  return fixture<Report>(reportFixtureName(sample.sample_id));
}

export function mockGetReport(reportId: string): Report {
  const r = allReports().find((x) => x.report_id === reportId);
  if (!r) throw new ApiError("NOT_FOUND", "Report not found", null, 404);
  return r;
}

const normCode = (c: string) => c.toUpperCase().replace(/[\s-]/g, "");

function genuine(r: Report): VerifyResult {
  const base = fixture<VerifyResult>("verify_genuine_current");
  return {
    ...base,
    report: {
      report_id: r.report_id as string,
      short_code: r.short_code as string,
      plot_id: r.plot.plot_id,
      verdict: r.verdict,
      issued_at: r.issued_at,
      valid_until: r.valid_until as string,
    },
    checked_at: new Date().toISOString(),
  };
}

const fromB64u = (s: string): Uint8Array => {
  const b = atob(s.replace(/-/g, "+").replace(/_/g, "/") + "=".repeat((4 - (s.length % 4)) % 4));
  return Uint8Array.from(b, (c) => c.charCodeAt(0));
};

// Mock verify uses the real Ed25519 check against pubkey.json, so mock mode behaves like real mode.
export function mockVerify(req: VerifyRequest): VerifyResult {
  if ("short_code" in req) {
    const code = normCode(req.short_code);
    const hit = allReports().find((r) => r.short_code && normCode(r.short_code) === code);
    return hit ? genuine(hit) : fixture<VerifyResult>("verify_unknown");
  }
  try {
    const raw = fromB64u(req.payload_b64);
    const ok = nacl.sign.detached.verify(raw, fromB64u(req.signature_b64), fromB64u(mockPubKey().public_key_b64));
    if (!ok) return fixture<VerifyResult>("verify_tampered");
    const payload = JSON.parse(new TextDecoder().decode(raw)) as { report_id?: string };
    const hit = allReports().find((r) => r.report_id === payload.report_id);
    return hit ? genuine(hit) : fixture<VerifyResult>("verify_unknown");
  } catch {
    return fixture<VerifyResult>("verify_tampered");
  }
}

// Mock mode keeps one bit of demo state: whether the demo ledger has been tampered with.
let tampered = false;
export const mockDemoLedger = (plotId: string): DemoLedger => ({
  ...fixture<DemoLedger>(tampered ? "demo_ledger_tampered" : "demo_ledger"),
  plot_id: plotId,
});
export function mockDemoTamper(plotId: string, kind: string): DemoLedger {
  // Same as the backend: these two kinds are announced in the contract but not built yet.
  if (kind === "replace_entry" || kind === "replay_checkpoint") {
    throw new ApiError("NOT_IMPLEMENTED", `${kind} is not implemented`, null, 501);
  }
  tampered = true;
  return mockDemoLedger(plotId);
}
export function mockDemoReset(): { ok: true } {
  tampered = false;
  return { ok: true };
}
