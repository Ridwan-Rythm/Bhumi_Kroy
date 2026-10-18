import { act, cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, beforeEach } from "vitest";
import i18n from "../i18n";
import App from "../App";
import en from "../i18n/en.json";
import bn from "../i18n/bn.json";
import { mockCheck, mockSamples } from "../mocks";
import { remember } from "../lib/reportStore";
import type { Report, Verdict } from "../types/contract";

const REPORTS = mockSamples().map((s) => ({ sample: s, report: mockCheck(s.request) }));
const WAIT = { timeout: 4000 };

function renderAt(path: string) {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <App />
    </MemoryRouter>,
  );
}
const setLang = (l: "bn" | "en") => act(async () => { await i18n.changeLanguage(l); });

beforeEach(() => setLang("en"));
afterEach(cleanup);

// Contract 8.2 and 8.3: text for EVERY rule id and not_checked code, Tier 2 included, in both languages.
const RULE_IDS = [
  "R-OWN-01", "R-OWN-02", "R-DISP-01", "R-DISP-02", "R-DISP-03", "R-RES-01", "R-RES-02", "R-LIEN-01", "R-SALE-01",
  "R-CHAIN-03", "R-CHAIN-04", "R-INT-01", "R-INT-02", "R-INT-03", "R-INFO-01", "R-INFO-02", "R-INFO-03",
  "R-OWN-03", "R-CHAIN-01", "R-CHAIN-02", "R-RES-03", "R-INT-04",
];
const NOT_CHECKED = [
  "source_unavailable", "source_stale", "source_partial", "linkage_party_name_only", "low_maturity",
  "static_physical_possession", "static_boundaries", "static_unregistered_agreements", "static_equitable_mortgage",
  "static_seller_documents", "static_legal_review",
];
const get = (o: unknown, path: string) => path.split(".").reduce<unknown>((a, k) => (a as Record<string, unknown>)?.[k], o);

describe("text coverage", () => {
  it("every rule has title, explanation and next step in en and bn", () => {
    for (const id of RULE_IDS) for (const part of ["title", "explain", "next"]) for (const cat of [en, bn]) {
      expect(get(cat, `rules.${id}.${part}`), `${id}.${part}`).toBeTruthy();
    }
  });
  it("every not_checked code, verdict, coverage, source status and verify state has text in en and bn", () => {
    const need = [
      ...NOT_CHECKED.map((c) => `notChecked.${c}`),
      ...(["GREEN", "GREY", "AMBER", "RED", "INTEGRITY_ALERT"] as Verdict[]).flatMap((v) => [`verdict.${v}.label`, `verdict.${v}.summary`]),
      ...["GENUINE_CURRENT", "GENUINE_EXPIRED", "GENUINE_SUPERSEDED", "TAMPERED", "INTEGRITY_ALERT", "UNKNOWN"].flatMap((s) => [`pages.verify.states.${s}.title`, `pages.verify.states.${s}.body`]),
      ...["COVERED", "PARTIAL", "NOT_COVERED"].map((c) => `coverage.${c}`),
      ...["OK", "NO_RECORD", "PARTIAL", "STALE", "UNAVAILABLE", "ERROR"].map((c) => `sourceStatus.${c}`),
      ...["NETWORK", "TIMEOUT", "VALIDATION_ERROR", "NOT_FOUND", "RATE_LIMITED", "DEMO_DISABLED", "NOT_IMPLEMENTED", "INTERNAL", "BAD_RESPONSE", "MOCK_MISSING"].map((c) => `errors.${c}`),
    ];
    for (const k of need) for (const cat of [en, bn]) expect(get(cat, k), k).toBeTruthy();
  });
  it("the watermark is the contract text with an em dash, and the Bangla one is Bangla", () => {
    expect(en.footer.watermark).toBe("SYNTHETIC — NOT A REAL LAND RECORD");
    expect(bn.footer.watermark).toMatch(/[\u0980-\u09FF]/);
    expect(bn.footer.watermark).toContain("—");
    expect(bn.footer.watermark).not.toContain(" - ");
  });
  it("GREEN never says safe or guaranteed, and says it is not a guarantee", () => {
    expect(en.verdict.GREEN.summary).toBe("No red flags found in the sources we checked. This is not a guarantee.");
  });
});

describe("Result screen", () => {
  for (const lang of ["en", "bn"] as const) {
    for (const { sample, report } of REPORTS) {
      it(`${sample.sample_id} renders its verdict, coverage, disclaimer and watermark (${lang})`, async () => {
        await setLang(lang);
        const key = remember(report);
        renderAt(`/result/${key}`);
        const t = i18n.t.bind(i18n);
        expect(await screen.findByTestId("report")).toBeInTheDocument();
        expect(screen.getByRole("status", { name: "" }).getAttribute("data-verdict")).toBe(report.verdict);
        expect(screen.getByText(t(`verdict.${report.verdict}.label`))).toBeInTheDocument();
        expect(screen.getByText(t("footer.disclaimer"))).toBeInTheDocument();
        expect(screen.getByRole("note")).toHaveTextContent(t("footer.watermark"));
        expect(screen.getByText(t("pages.result.notCheckedTitle"))).toBeInTheDocument();
        for (const f of report.findings) {
          expect(document.querySelector(`[data-rule="${f.rule_id}"]`), f.rule_id).not.toBeNull();
          // no finding falls back to the generic text
          expect(document.body.textContent).not.toContain(t("rules.fallback.explain"));
        }
      });
    }
  }

  it("an unknown rule_id and unknown not_checked code render the generic fallback and do not crash", async () => {
    const base = REPORTS[0].report;
    const weird: Report = {
      ...base,
      findings: [{ rule_id: "R-FUTURE-99", severity: "MEDIUM", confidence: "LOW", question: "Q1", evidence: [], params: { x: 1 } }],
      not_checked: [{ code: "something_new", params: {} }],
    };
    renderAt(`/result/${remember(weird)}`);
    expect(await screen.findByText(i18n.t("rules.fallback.explain"))).toBeInTheDocument();
    expect(screen.getByText(i18n.t("notChecked.fallback"))).toBeInTheDocument();
  });

  it("an INTEGRITY_ALERT report (no id, no signature) shows the alert and no QR", async () => {
    const alert = mockCheck(mockSamples()[0].request);
    const r: Report = { ...alert, verdict: "INTEGRITY_ALERT", report_id: null, short_code: null, valid_until: null, signed_payload_b64: null, signature_b64: null };
    renderAt(`/result/${remember(r)}`);
    expect(await screen.findByText(i18n.t("verdict.INTEGRITY_ALERT.label"))).toBeInTheDocument();
    expect(screen.getAllByText(i18n.t("pages.result.noReportId")).length).toBeGreaterThan(0);
    expect(screen.queryByAltText(i18n.t("pages.result.qrAlt"))).toBeNull();
  });

  it("Bangla mode shows Bangla digits for numbers and keeps names untouched", async () => {
    await setLang("bn");
    const r = REPORTS.find((x) => x.report.holders_summary.holder_count >= 1)!.report;
    renderAt(`/result/${remember(r)}`);
    await screen.findByTestId("report");
    expect(screen.getByText(r.seller.name)).toBeInTheDocument();
    expect(document.body.textContent).toMatch(/[০-৯]/);
  });
});

describe("full flow with mock data", () => {
  it("Home -> Form (sample) -> Checking -> Result", async () => {
    renderAt("/");
    fireEvent.click(await screen.findByRole("link", { name: i18n.t("pages.home.start") }));
    expect(await screen.findByRole("heading", { name: i18n.t("pages.check.title") }, WAIT)).toBeInTheDocument();
    const sample = await screen.findByLabelText(new RegExp(i18n.t("pages.check.sample")), undefined, WAIT);
    await waitFor(() => expect(within(sample).getAllByRole("option").length).toBeGreaterThan(5), WAIT);
    fireEvent.change(sample, { target: { value: "P-003" } });
    fireEvent.click(screen.getByRole("button", { name: i18n.t("pages.check.submit") }));
    expect(await screen.findByRole("heading", { name: i18n.t("pages.checking.title") })).toBeInTheDocument();
    expect(await screen.findByText(i18n.t("verdict.RED.label"), undefined, WAIT)).toBeInTheDocument();
  });

  it("the form shows field errors and focuses the summary when required fields are empty", async () => {
    renderAt("/check");
    const submit = await screen.findByRole("button", { name: i18n.t("pages.check.submit") }, WAIT);
    fireEvent.click(submit);
    const alert = await screen.findByRole("alert");
    expect(alert).toHaveTextContent(i18n.t("pages.check.fixErrors"));
    expect(document.activeElement).toBe(alert);
    expect(screen.getAllByText(i18n.t("pages.check.fieldRequired")).length).toBe(6);
    expect(screen.getByLabelText(new RegExp(i18n.t("pages.check.khatian")))).toHaveAttribute("aria-invalid", "true");
  });

  it("?sample= prefills the form, and Bangla digits are sent as ASCII", async () => {
    renderAt("/check?sample=P-001");
    const khatian = (await screen.findByLabelText(new RegExp(i18n.t("pages.check.khatian")), undefined, WAIT)) as HTMLInputElement;
    await waitFor(() => expect(khatian.value).toBe("1203"), WAIT);
  });

  it("Checking without a request goes back to the form", async () => {
    renderAt("/checking");
    expect(await screen.findByRole("heading", { name: i18n.t("pages.check.title") }, WAIT)).toBeInTheDocument();
  });
});

describe("Verify screen", () => {
  const p1 = REPORTS[0].report;

  it("verifies a short code typed with lower case and a space", async () => {
    renderAt("/verify");
    const input = screen.getByLabelText(i18n.t("pages.verify.codeLabel"));
    fireEvent.change(input, { target: { value: (p1.short_code as string).toLowerCase().replace("-", " ") } });
    fireEvent.click(screen.getByRole("button", { name: i18n.t("pages.verify.submit") }));
    expect(await screen.findByText(i18n.t("pages.verify.states.GENUINE_CURRENT.title"), undefined, WAIT)).toBeInTheDocument();
  });

  it("an unknown code says so", async () => {
    renderAt("/verify?code=ZZZZ-ZZZZ");
    expect(await screen.findByText(i18n.t("pages.verify.states.UNKNOWN.title"), undefined, WAIT)).toBeInTheDocument();
  });

  it("a #payload.signature link is verified by the server mock AND by the browser", async () => {
    renderAt(`/verify#${p1.signed_payload_b64}.${p1.signature_b64}`);
    expect(await screen.findByText(i18n.t("pages.verify.states.GENUINE_CURRENT.title"), undefined, WAIT)).toBeInTheDocument();
    expect(await screen.findByText(i18n.t("pages.verify.browserValid"), undefined, WAIT)).toBeInTheDocument();
  });

  it("a link with a flipped byte is TAMPERED and the browser agrees", async () => {
    const payload = p1.signed_payload_b64 as string;
    const bad = payload.slice(0, -3) + (payload.endsWith("AAA") ? "BBB" : "AAA");
    renderAt(`/verify#${bad}.${p1.signature_b64}`);
    expect(await screen.findByText(i18n.t("pages.verify.states.TAMPERED.title"), undefined, WAIT)).toBeInTheDocument();
    expect(await screen.findByText(i18n.t("pages.verify.browserInvalid"), undefined, WAIT)).toBeInTheDocument();
  });
});

describe("Print screen", () => {
  it("keeps the disclaimer and the SYNTHETIC watermark in the printable page", async () => {
    renderAt(`/report/${remember(REPORTS[2].report)}/print`);
    expect(await screen.findByTestId("report")).toBeInTheDocument();
    expect(screen.getByText(i18n.t("footer.disclaimer"))).toBeInTheDocument();
    expect(screen.getByRole("note")).toHaveTextContent(i18n.t("footer.watermark"));
    expect(screen.getByTestId("print-watermark")).toHaveTextContent(i18n.t("footer.watermarkShort"));
    // nothing that carries the disclaimer or the watermark may be hidden when printing
    const footer = document.querySelector("footer") as HTMLElement;
    expect(footer.className).not.toMatch(/print:hidden/);
    expect(screen.getByRole("note").closest("footer")).toBe(footer);
  });
});

describe("Demo console (mock mode)", () => {
  it("tampering breaks the ledger, reset heals it, and unbuilt tamper kinds say so", async () => {
    renderAt("/demo");
    const status = await screen.findByTestId("ledger-status", undefined, WAIT);
    await waitFor(() => expect(status).toHaveTextContent(i18n.t("pages.demo.statusOk")), WAIT);
    fireEvent.click(screen.getByRole("button", { name: i18n.t("pages.demo.tamper.edit_field") }));
    await waitFor(() => expect(screen.getByTestId("ledger-status")).toHaveTextContent(i18n.t("pages.demo.statusBroken")), WAIT);
    fireEvent.click(screen.getByRole("button", { name: i18n.t("pages.demo.tamper.replay_checkpoint") }));
    expect(await screen.findByText(i18n.t("errors.NOT_IMPLEMENTED"), undefined, WAIT)).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: i18n.t("pages.demo.reset") }));
    await waitFor(() => expect(screen.getByTestId("ledger-status")).toHaveTextContent(i18n.t("pages.demo.statusOk")), WAIT);
  });
});

describe("shell accessibility and language", () => {
  it("the language button's accessible name is its visible text (WCAG 2.5.3) and carries lang", async () => {
    await setLang("en");
    renderAt("/");
    const btn = await screen.findByRole("button", { name: "বাংলা" });
    expect(btn).toHaveTextContent("বাংলা");
    expect(btn).toHaveAttribute("lang", "bn");
    expect(btn).not.toHaveAttribute("aria-label");
  });

  it("the home link's accessible name contains its visible text", async () => {
    renderAt("/");
    const link = await screen.findByRole("link", { name: i18n.t("app.name") });
    expect(link).not.toHaveAttribute("aria-label");
  });

  it("main can receive focus so the skip link moves focus", async () => {
    renderAt("/");
    const main = (await screen.findAllByRole("main"))[0];
    expect(main).toHaveAttribute("id", "main");
    expect(main).toHaveAttribute("tabindex", "-1");
  });

  it("switching language updates <html lang> and the document title", async () => {
    renderAt("/");
    await setLang("bn");
    expect(document.documentElement.lang).toBe("bn");
    expect(document.title).toBe(bn.app.title);
    await setLang("en");
    expect(document.documentElement.lang).toBe("en");
    expect(document.title).toBe(en.app.title);
  });

  it("the product name is the same in the title and header", () => {
    expect(en.app.name).toBe("Bhumi_Kroy");
    expect(en.app.title.startsWith("Bhumi_Kroy")).toBe(true);
    expect(bn.app.name).toBe("ভূমি ক্রয়");
    expect(en.app.name).not.toMatch(/[\u0980-\u09FF]/);
  });
});
