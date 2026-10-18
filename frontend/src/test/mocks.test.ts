import { mockCheck, mockGetReport, mockSamples, mockVerify } from "../mocks";
import type { CheckRequest } from "../types/contract";

const clone = <T,>(x: T): T => JSON.parse(JSON.stringify(x)) as T;

describe("mock mode behaves like the real API", () => {
  it("has a report for every one of the 10 samples, with the expected verdict", () => {
    const samples = mockSamples();
    expect(samples).toHaveLength(10);
    for (const s of samples) {
      const r = mockCheck(s.request);
      expect(r.verdict).toBe(s.expected_verdict);
      expect(r.synthetic).toBe(true);
    }
  });

  it("P-008B (same plot as P-008, with the father's name) gets its own report, not P-001's", () => {
    const samples = mockSamples();
    const a = mockCheck((samples.find((s) => s.sample_id === "P-008") as { request: CheckRequest }).request);
    const b = mockCheck((samples.find((s) => s.sample_id === "P-008B") as { request: CheckRequest }).request);
    expect(a.plot.plot_id).toBe("P-008");
    expect(b.plot.plot_id).toBe("P-008");
    expect(a.seller.match.tier).toBe("PROBABLE");
    expect(b.seller.match.tier).toBe("STRONG");
    expect(a.verdict).toBe("AMBER");
    expect(b.verdict).toBe("GREEN");
    expect(b.findings.map((f) => f.rule_id)).toContain("R-INFO-01");
    expect(b.report_id).not.toBe(a.report_id);
    expect(b.plot.plot_id).not.toBe("P-001");
  });

  it("does not ignore consents, district, upazila or survey when matching", () => {
    const req = clone(mockSamples()[0].request);
    expect(() => mockCheck({ ...req, consents: { bank: false } })).toThrow(/No mock fixture/);
    for (const edit of [
      (r: CheckRequest) => { r.plot.district_id = "dhaka"; },
      (r: CheckRequest) => { r.plot.upazila_id = "other"; },
      (r: CheckRequest) => { r.plot.survey = "CS"; },
    ]) {
      const r = clone(req);
      edit(r);
      expect(() => mockCheck(r)).toThrow(/No mock fixture/);
    }
  });

  it("normalises Bangla digits and spaces like the backend", () => {
    const req = clone(mockSamples()[0].request);
    req.plot.khatian_no = req.plot.khatian_no.replace(/\d/g, (d) => String.fromCharCode(0x09e6 + Number(d)));
    req.seller.name = `  ${req.seller.name}  `;
    expect(mockCheck(req).plot.plot_id).toBe("P-001");
  });

  it("has every report reachable by id, and verifies short codes case- and hyphen-insensitively", () => {
    const r = mockCheck(mockSamples()[0].request);
    expect(mockGetReport(r.report_id as string)).toEqual(r);
    const code = (r.short_code as string).toLowerCase().replace("-", " ");
    expect(mockVerify({ short_code: code }).state).toBe("GENUINE_CURRENT");
    expect(mockVerify({ short_code: "ZZZZ-ZZZZ" }).state).toBe("UNKNOWN");
  });

  it("checks the Ed25519 signature for real, so a flipped byte is TAMPERED", () => {
    const r = mockCheck(mockSamples()[0].request);
    const payload = r.signed_payload_b64 as string;
    const signature = r.signature_b64 as string;
    expect(mockVerify({ payload_b64: payload, signature_b64: signature }).state).toBe("GENUINE_CURRENT");
    const flipped = payload.slice(0, -3) + (payload.endsWith("AAA") ? "BBB" : "AAA");
    expect(mockVerify({ payload_b64: flipped, signature_b64: signature }).state).toBe("TAMPERED");
    expect(mockVerify({ payload_b64: "###", signature_b64: signature }).state).toBe("TAMPERED");
  });
});
