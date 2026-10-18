import type { ApiErrorCode } from "../types/contract";

// Contract section 5 error codes, plus client-only codes for failures that never produce a contract error.
export type ClientErrorCode = ApiErrorCode | "NETWORK" | "TIMEOUT" | "BAD_RESPONSE" | "MOCK_MISSING";

const API_CODES: readonly ApiErrorCode[] = [
  "VALIDATION_ERROR",
  "NOT_FOUND",
  "RATE_LIMITED",
  "DEMO_DISABLED",
  "NOT_IMPLEMENTED",
  "INTERNAL",
];

export const isApiCode = (v: unknown): v is ApiErrorCode =>
  typeof v === "string" && (API_CODES as readonly string[]).includes(v);

export class ApiError extends Error {
  readonly code: ClientErrorCode;
  readonly field: string | null;
  readonly status: number;

  constructor(code: ClientErrorCode, message: string, field: string | null = null, status = 0) {
    super(message);
    this.name = "ApiError";
    this.code = code;
    this.field = field;
    this.status = status;
  }
}

// What a bare HTTP status means when the body has no usable contract error.
function codeFromStatus(status: number): ApiErrorCode {
  if (status === 422) return "VALIDATION_ERROR";
  if (status === 404) return "NOT_FOUND";
  if (status === 429) return "RATE_LIMITED";
  if (status === 501) return "NOT_IMPLEMENTED";
  return "INTERNAL";
}

// FastAPI's default 422 body: {"detail": [{"loc": ["body","plot","dag_no"], "msg": "...", "type": "..."}]}
// (or {"detail": "text"}). A proxy or a misconfigured server can still produce it, so it must not become INTERNAL.
function parseFastApiDetail(body: object, status: number): ApiError | null {
  if (!("detail" in body)) return null;
  const detail = (body as { detail: unknown }).detail;
  if (status !== 422) return null;
  if (Array.isArray(detail) && detail.length > 0 && typeof detail[0] === "object" && detail[0] !== null) {
    const first = detail[0] as { loc?: unknown; msg?: unknown };
    const path = Array.isArray(first.loc)
      ? first.loc.filter((p) => p !== "body" && p !== "query" && p !== "path").join(".")
      : "";
    return new ApiError("VALIDATION_ERROR", typeof first.msg === "string" ? first.msg : "", path || null, status);
  }
  return new ApiError("VALIDATION_ERROR", typeof detail === "string" ? detail : "", null, status);
}

// Parses {"error": {"code","message","field"}} into an ApiError. An unknown code never leaks through as a
// "valid" code: it falls back to what the HTTP status says. Anything else becomes INTERNAL.
export function parseErrorBody(body: unknown, status: number): ApiError {
  if (body && typeof body === "object") {
    if ("error" in body) {
      const e = (body as { error?: { code?: unknown; message?: unknown; field?: unknown } }).error;
      if (e && typeof e === "object") {
        const code = isApiCode(e.code) ? e.code : codeFromStatus(status);
        const message = typeof e.message === "string" ? e.message : "";
        const field = typeof e.field === "string" ? e.field : null;
        return new ApiError(code, message, field, status);
      }
    }
    const fastApi = parseFastApiDetail(body, status);
    if (fastApi) return fastApi;
  }
  return new ApiError(codeFromStatus(status), "", null, status);
}
