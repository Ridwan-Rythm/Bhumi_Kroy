import type {
  AddEventKind,
  CheckRequest,
  DemoLedger,
  Locations,
  PubKey,
  Report,
  SamplePlot,
  TamperKind,
  VerifyRequest,
  VerifyResult,
} from "../types/contract";
import { ApiError, parseErrorBody } from "./errors";
import * as mocks from "../mocks";

// Contract section 4: VITE_USE_MOCK=1 serves fixtures, 0 calls the real API.
const USE_MOCK = import.meta.env.VITE_USE_MOCK === "1";
const MOCK_DELAY_MS = 300;

const API = "/api/v1"; // contract section 5
const DEMO = "/demo"; // /demo/* is NOT under /api/v1

export const isMockMode = () => USE_MOCK;

async function mock<T>(fn: () => T): Promise<T> {
  await new Promise((r) => setTimeout(r, MOCK_DELAY_MS));
  return fn();
}

// A check takes ~0.3 s and the backend caps each source at 1.5 s, so 20 s means something is wrong.
export const REQUEST_TIMEOUT_MS = 20_000;

export async function request<T>(
  method: "GET" | "POST",
  path: string,
  body?: unknown,
  timeoutMs = REQUEST_TIMEOUT_MS,
): Promise<T> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    let res: Response;
    try {
      res = await fetch(path, {
        method,
        headers: body === undefined ? undefined : { "Content-Type": "application/json" },
        body: body === undefined ? undefined : JSON.stringify(body),
        signal: controller.signal,
      });
    } catch (e) {
      throw new ApiError(controller.signal.aborted || (e as Error)?.name === "AbortError" ? "TIMEOUT" : "NETWORK", "");
    }
    let json: unknown = null;
    let parsed = true;
    try {
      json = await res.json();
    } catch {
      parsed = false;
    }
    if (!res.ok) throw parseErrorBody(json, res.status);
    // A 2xx whose body is not JSON (a proxy's HTML page, an empty body) is a failure, not a silent null.
    if (!parsed || json === null || json === undefined) {
      throw new ApiError("BAD_RESPONSE", "Response was not JSON", null, res.status); // i18n-ignore: developer message, the UI shows errors.BAD_RESPONSE
    }
    return json as T;
  } finally {
    clearTimeout(timer);
  }
}

export const health = (): Promise<{ ok: boolean; demo_mode: boolean }> =>
  USE_MOCK ? mock(() => ({ ok: true, demo_mode: true })) : request("GET", `${API}/health`);

export const getLocations = (): Promise<Locations> =>
  USE_MOCK ? mock(mocks.mockLocations) : request("GET", `${API}/meta/locations`);

export const getSamples = (): Promise<SamplePlot[]> =>
  USE_MOCK ? mock(mocks.mockSamples) : request("GET", `${API}/meta/samples`);

export const getPubKey = (): Promise<PubKey> =>
  USE_MOCK ? mock(mocks.mockPubKey) : request("GET", `${API}/meta/pubkey`);

export const check = (req: CheckRequest): Promise<Report> =>
  USE_MOCK ? mock(() => mocks.mockCheck(req)) : request("POST", `${API}/check`, req);

export const getReport = (reportId: string): Promise<Report> =>
  USE_MOCK
    ? mock(() => mocks.mockGetReport(reportId))
    : request("GET", `${API}/reports/${encodeURIComponent(reportId)}`);

export const verify = (req: VerifyRequest): Promise<VerifyResult> =>
  USE_MOCK ? mock(() => mocks.mockVerify(req)) : request("POST", `${API}/verify`, req);

// ---- demo endpoints (DEMO_MODE=1 on the backend) ----

export const demoTamper = (plotId: string, kind: TamperKind): Promise<DemoLedger> =>
  USE_MOCK
    ? mock(() => mocks.mockDemoTamper(plotId, kind))
    : request("POST", `${DEMO}/tamper`, { plot_id: plotId, kind });

export const demoAddEvent = (
  plotId: string,
  kind: AddEventKind,
): Promise<{ ok: true; added: { record_ref: string; kind: string; date: string } }> =>
  USE_MOCK
    ? mock(() => ({ ok: true as const, added: { record_ref: "MOCK-0001", kind, date: "2026-10-17" } }))
    : request("POST", `${DEMO}/add-event`, { plot_id: plotId, kind });

export const demoReset = (): Promise<{ ok: true }> =>
  USE_MOCK ? mock(mocks.mockDemoReset) : request("POST", `${DEMO}/reset`);

export const demoLedger = (plotId: string): Promise<DemoLedger> =>
  USE_MOCK
    ? mock(() => mocks.mockDemoLedger(plotId))
    : request("GET", `${DEMO}/ledger/${encodeURIComponent(plotId)}`);

export const demoClock = (offsetDays: number): Promise<{ ok: true; now: string }> =>
  USE_MOCK
    ? mock(() => ({ ok: true as const, now: new Date().toISOString() }))
    : request("POST", `${DEMO}/clock`, { offset_days: offsetDays });
