import type { ApiErrorCode } from "../types/contract";

// Contract section 5 error codes, plus two client-only codes for failures that never reach the API.
export type ClientErrorCode = ApiErrorCode | "NETWORK" | "MOCK_MISSING";

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

// Parses {"error": {"code","message","field"}} into an ApiError. Anything else becomes INTERNAL.
export function parseErrorBody(body: unknown, status: number): ApiError {
  if (body && typeof body === "object" && "error" in body) {
    const e = (body as { error?: { code?: string; message?: string; field?: string | null } }).error;
    if (e && typeof e.code === "string") {
      return new ApiError(e.code as ClientErrorCode, e.message ?? "", e.field ?? null, status);
    }
  }
  return new ApiError("INTERNAL", "", null, status);
}
