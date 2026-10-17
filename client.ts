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

async function request<T>(method: "GET" | "POST", path: string, body?: unknown): Promise<T> {
  let res: Response;
  try {
    res = await fetch(path, {
      method,
      headers: body === undefined ? undefined : { "Content-Type": "application/json" },
      body: body === undefined ? undefined : JSON.stringify(body),
    });
  } catch {
    throw new ApiError("NETWORK", "");
  }
  let json: unknown = null;
  try {
    json = await res.json();
  } catch {
    // non-JSON body: handled below
  }
  if (!res.ok) throw parseErrorBody(json, res.status);
  return json as T;
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
    ? mock(() => mocks.mockDemoLedger(plotId))
    : request("POST", `${DEMO}/tamper`, { plot_id: plotId, kind });

export const demoAddEvent = (
  plotId: string,
  kind: AddEventKind,
): Promise<{ ok: true; added: { record_ref: string; kind: string; date: string } }> =>
  USE_MOCK
    ? mock(() => ({ ok: true as const, added: { record_ref: "MOCK-0001", kind, date: "2026-10-17" } }))
    : request("POST", `${DEMO}/add-event`, { plot_id: plotId, kind });

export const demoReset = (): Promise<{ ok: true }> =>
  USE_MOCK ? mock(() => ({ ok: true as const })) : request("POST", `${DEMO}/reset`);

export const demoLedger = (plotId: string): Promise<DemoLedger> =>
  USE_MOCK
    ? mock(() => mocks.mockDemoLedger(plotId))
    : request("GET", `${DEMO}/ledger/${encodeURIComponent(plotId)}`);

export const demoClock = (offsetDays: number): Promise<{ ok: true; now: string }> =>
  USE_MOCK
    ? mock(() => ({ ok: true as const, now: new Date().toISOString() }))
    : request("POST", `${DEMO}/clock`, { offset_days: offsetDays });
