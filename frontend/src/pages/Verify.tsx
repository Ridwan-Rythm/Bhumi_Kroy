import { useCallback, useEffect, useRef, useState } from "react";
import type { FormEvent } from "react";
import { Link, useLocation, useSearchParams } from "react-router-dom";
import { useTranslation } from "react-i18next";
import type { VerifyRequest, VerifyResult } from "../types/contract";
import { getPubKey, verify } from "../api/client";
import { fmtDate, fmtDateTime } from "../lib/format";
import { localizeParams } from "../lib/localize";
import { parseVerifyFragment, verifySignatureLocally } from "../lib/verifyLocal";
import { ErrorNotice, MockBanner, Spinner } from "../components/ui";

type VerifyState = VerifyResult["state"];

const STATE_STYLE: Record<VerifyState, { icon: string; box: string }> = {
  GENUINE_CURRENT: { icon: "✓", box: "border-verdict-green bg-green-50 text-verdict-green" },
  GENUINE_EXPIRED: { icon: "!", box: "border-verdict-amber bg-amber-50 text-verdict-amber" },
  GENUINE_SUPERSEDED: { icon: "!", box: "border-verdict-amber bg-amber-50 text-verdict-amber" },
  TAMPERED: { icon: "✕", box: "border-verdict-red bg-red-50 text-verdict-red" },
  INTEGRITY_ALERT: { icon: "⚠", box: "border-verdict-integrity bg-violet-50 text-verdict-integrity" },
  UNKNOWN: { icon: "?", box: "border-verdict-grey bg-gray-100 text-verdict-grey" },
};

export default function Verify() {
  const { t, i18n } = useTranslation();
  const lang = i18n.language;
  const loc = useLocation();
  const [params] = useSearchParams();
  const [code, setCode] = useState(params.get("code") ?? "");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<unknown>(null);
  const [result, setResult] = useState<VerifyResult | null>(null);
  const [local, setLocal] = useState<boolean | null>(null);
  const [fromLink, setFromLink] = useState(false);
  const ran = useRef(false); // StrictMode runs effects twice in dev

  const run = useCallback(async (req: VerifyRequest) => {
    setBusy(true); setError(null); setResult(null); setLocal(null);
    try {
      const res = await verify(req);
      setResult(res);
      if ("payload_b64" in req) {
        // The server said what it thinks; the browser checks the signature on its own as well.
        const key = await getPubKey().catch(() => null);
        if (key) setLocal(verifySignatureLocally(req.payload_b64, req.signature_b64, key.public_key_b64));
      }
    } catch (e) {
      setError(e);
    } finally {
      setBusy(false);
    }
  }, []);

  useEffect(() => {
    if (ran.current) return;
    ran.current = true;
    const frag = parseVerifyFragment(loc.hash);
    if (frag) { setFromLink(true); void run(frag); return; }
    const c = params.get("code");
    if (c) void run({ short_code: c });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function submit(e: FormEvent) {
    e.preventDefault();
    if (code.trim()) { setFromLink(false); void run({ short_code: code.trim() }); }
  }

  const style = result ? STATE_STYLE[result.state] : null;
  return (
    <div>
      <MockBanner />
      <h1 className="gradient-text text-3xl font-bold">{t("pages.verify.title")}</h1>
      <p className="mt-2 text-slate-700">{t("pages.verify.lead")}</p>
      <form onSubmit={submit} className="card mt-5 p-4 sm:p-6">
        <label htmlFor="verify-code" className="font-bold text-brand-900">{t("pages.verify.codeLabel")}</label>
        <input id="verify-code" value={code} onChange={(e) => setCode(e.target.value)} autoComplete="off" autoCapitalize="characters"
          aria-describedby="verify-code-help" placeholder={t("pages.verify.codePlaceholder")}
          className="control mt-1.5 font-mono text-lg uppercase tracking-widest" />
        <p id="verify-code-help" className="mt-1 text-sm text-slate-600">{t("pages.verify.codeHelp")}</p>
        <button type="submit" disabled={busy} className="btn-primary mt-4 w-full py-3.5">
          {busy ? t("pages.verify.checking") : t("pages.verify.submit")}
        </button>
      </form>

      {fromLink && busy ? <p className="mt-3">{t("pages.verify.fromLink")}</p> : null}
      {busy ? <div className="mt-4"><Spinner /></div> : null}
      {error ? <div className="mt-4"><ErrorNotice error={error} onRetry={() => code.trim() && run({ short_code: code.trim() })} /></div> : null}

      {result && style ? (
        <div className="mt-6" data-state={result.state}>
          <div role="status" className={`animate-pop rounded-2xl border-2 border-l-[10px] p-5 shadow-lift ${style.box}`}>
            <p className="flex items-center gap-3 text-2xl font-bold">
              <span aria-hidden="true" className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-white text-3xl shadow-soft">{style.icon}</span>
              {t(`pages.verify.states.${result.state}.title`)}
            </p>
            <p className="mt-2 text-gray-900">{t(`pages.verify.states.${result.state}.body`)}</p>
          </div>

          <ul className="stagger card mt-4 space-y-1 p-4">
            <li>{result.signature_valid ? t("pages.verify.signatureValid") : t("pages.verify.signatureInvalid")}</li>
            {local !== null ? <li>{local ? t("pages.verify.browserValid") : t("pages.verify.browserInvalid")}</li> : null}
            <li>
              {result.ledger.ok
                ? t("pages.verify.ledgerOk")
                : t("pages.verify.ledgerBroken", { reason: result.ledger.reason ? localizeParams(t, lang, { reason: result.ledger.reason }, "R-INT-01").reason : "" })}
            </li>
            <li className="text-sm text-slate-600">{t("pages.verify.checkedAt", { date: fmtDateTime(result.checked_at, lang) })}</li>
          </ul>

          {result.report ? (
            <section className="card mt-5 animate-fade-up p-4" aria-labelledby="verify-report">
              <h2 id="verify-report" className="heading-accent text-xl font-bold text-brand-900">{t("pages.verify.reportTitle")}</h2>
              <dl className="mt-1 space-y-1">
                <div><dt className="inline font-bold">{t("pages.result.reportId")}: </dt><dd className="inline">{result.report.report_id}</dd></div>
                <div><dt className="inline font-bold">{t("pages.result.shortCode")}: </dt><dd className="inline font-mono">{result.report.short_code}</dd></div>
                <div><dt className="inline font-bold">{t("pages.result.issued")}: </dt><dd className="inline">{fmtDateTime(result.report.issued_at, lang)}</dd></div>
                <div><dt className="inline font-bold">{t("pages.result.validUntil")}: </dt><dd className="inline">{fmtDateTime(result.report.valid_until, lang)}</dd></div>
              </dl>
              <p className="mt-1">{t("pages.verify.verdictAtIssue", { verdict: t(`verdict.${result.report.verdict}.label`) })}</p>
            </section>
          ) : null}

          {result.diff && result.diff.length > 0 ? (
            <section className="card mt-5 animate-fade-up p-4" aria-labelledby="verify-diff">
              <h2 id="verify-diff" className="heading-accent text-xl font-bold text-brand-900">{t("pages.verify.diffTitle")}</h2>
              <ul className="list-disc pl-6">
                {result.diff.map((d) => (
                  <li key={d.record_ref}>{t("pages.verify.diffItem", { kind: t(`events.${d.kind}`), date: fmtDate(d.date, lang), ref: d.record_ref })}</li>
                ))}
              </ul>
            </section>
          ) : null}

          {result.state === "GENUINE_EXPIRED" || result.state === "GENUINE_SUPERSEDED" ? (
            <p className="mt-4"><Link to="/check" className="btn-primary">{t("pages.verify.newCheck")}</Link></p>
          ) : null}
        </div>
      ) : null}
    </div>
  );
}
