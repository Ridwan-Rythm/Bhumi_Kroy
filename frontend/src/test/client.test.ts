import { afterEach, vi } from "vitest";
import { parseErrorBody, ApiError } from "../api/errors";
import { request } from "../api/client";

describe("error parsing (contract section 5)", () => {
  it("parses the contract error shape", () => {
    const e = parseErrorBody(
      { error: { code: "VALIDATION_ERROR", message: "bad khatian", field: "plot.khatian_no" } },
      422,
    );
    expect(e).toBeInstanceOf(ApiError);
    expect(e.code).toBe("VALIDATION_ERROR");
    expect(e.field).toBe("plot.khatian_no");
    expect(e.status).toBe(422);
  });

  it("falls back to INTERNAL for unknown bodies", () => {
    expect(parseErrorBody(null, 500).code).toBe("INTERNAL");
    expect(parseErrorBody({ oops: 1 }, 502).code).toBe("INTERNAL");
  });

  it("turns FastAPI's default 422 body into VALIDATION_ERROR with the field path", () => {
    const e = parseErrorBody({ detail: [{ loc: ["body", "plot", "dag_no"], msg: "Field required", type: "missing" }] }, 422);
    expect(e.code).toBe("VALIDATION_ERROR");
    expect(e.field).toBe("plot.dag_no");
    expect(parseErrorBody({ detail: "Unprocessable" }, 422).code).toBe("VALIDATION_ERROR");
  });

  it("never lets an unknown error.code through as if it were valid", () => {
    expect(parseErrorBody({ error: { code: "TEAPOT", message: "x", field: null } }, 500).code).toBe("INTERNAL");
    expect(parseErrorBody({ error: { code: "TEAPOT", message: "x", field: null } }, 404).code).toBe("NOT_FOUND");
    expect(parseErrorBody({ error: { code: "TEAPOT", message: "x", field: null } }, 429).code).toBe("RATE_LIMITED");
  });

  it("maps a bare status to the closest contract code", () => {
    expect(parseErrorBody(null, 404).code).toBe("NOT_FOUND");
    expect(parseErrorBody("<html>", 429).code).toBe("RATE_LIMITED");
    expect(parseErrorBody(undefined, 501).code).toBe("NOT_IMPLEMENTED");
  });
});

describe("request()", () => {
  afterEach(() => vi.unstubAllGlobals());
  const respond = (body: BodyInit | null, status = 200) =>
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(body, { status })));

  it("returns parsed JSON on success", async () => {
    respond(JSON.stringify({ ok: true }));
    await expect(request("GET", "/x")).resolves.toEqual({ ok: true });
  });

  it("rejects a 2xx whose body is not JSON instead of returning null", async () => {
    respond("<html>proxy page</html>");
    await expect(request("GET", "/x")).rejects.toMatchObject({ code: "BAD_RESPONSE" });
    respond(null);
    await expect(request("GET", "/x")).rejects.toMatchObject({ code: "BAD_RESPONSE" });
    respond("null");
    await expect(request("GET", "/x")).rejects.toMatchObject({ code: "BAD_RESPONSE" });
  });

  it("raises the contract error for a non-2xx response", async () => {
    respond(JSON.stringify({ error: { code: "NOT_FOUND", message: "no", field: "report_id" } }), 404);
    await expect(request("GET", "/x")).rejects.toMatchObject({ code: "NOT_FOUND", field: "report_id", status: 404 });
  });

  it("reports NETWORK when fetch fails", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new TypeError("Failed to fetch")));
    await expect(request("GET", "/x")).rejects.toMatchObject({ code: "NETWORK" });
  });

  it("times out instead of waiting forever", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn((_: string, init: RequestInit) =>
        new Promise((_res, rej) => init.signal?.addEventListener("abort", () => rej(new DOMException("aborted", "AbortError")))),
      ),
    );
    await expect(request("GET", "/x", undefined, 30)).rejects.toMatchObject({ code: "TIMEOUT" });
  });
});
