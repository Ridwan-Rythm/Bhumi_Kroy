import { parseErrorBody, ApiError } from "../api/errors";

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
});
