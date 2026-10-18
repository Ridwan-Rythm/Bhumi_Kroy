import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import type { AddEventKind, DemoLedger, Report, SamplePlot, TamperKind } from "../types/contract";
import { ApiError } from "../api/errors";
import { check, demoAddEvent, demoClock, demoLedger, demoReset, demoTamper, getSamples } from "../api/client";
import { fmtDateTime } from "../lib/format";
import { localizeParams } from "../lib/localize";
import { remember } from "../lib/reportStore";
import { ErrorNotice, MockBanner, Spinner, errorMessage } from "../components/ui";

const TAMPER: TamperKind[] = ["edit_field", "edit_and_rehash", "delete_entry", "swap_signature", "reorder", "replace_entry", "replay_checkpoint"];
const ADD: AddEventKind[] = ["new_mortgage", "new_mutation_pending"];
const btn = "min-h-tap rounded border-2 border-gray-900 px-3 py-2 text-left font-medium disabled:opacity-60";

export default function Demo() {
  const { t, i18n } = useTranslation();
  const lang = i18n.language;
  const [samples, setSamples] = useState<SamplePlot[]>([]);
  const [plotId, setPlotId] = useState("P-001");
  const [ledger, setLedger] = useState<DemoLedger | null>(null);
  const [error, setError] = useState<unknown>(null);
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const [last, setLast] = useState<Report | null>(null);
  const [days, setDays] = useState("8");
  const [disabled, setDisabled] = useState(false);

  const fail = useCallback((e: unknown) => {
    if (e instanceof ApiError && e.code === "DEMO_DISABLED") setDisabled(true);
    setError(e);
  }, []);

  const refresh = useCallback((id: string) => {
    demoLedger(id).then((l) => { setLedger(l); setError(null); }).catch(fail);
  }, [fail]);

  useEffect(() => { getSamples().then(setSamples).catch(fail); }, [fail]);
  useEffect(() => { refresh(plotId); }, [plotId, refresh]);

  async function act(fn: () => Promise<string | void>) {
    setBusy(true); setError(null); setMessage("");
    try {
      const m = await fn();
      if (m) setMessage(m);
      refresh(plotId);
    } catch (e) {
      if (e instanceof ApiError && e.code === "NOT_IMPLEMENTED") setMessage(errorMessage(t, e));
      else fail(e);
    } finally {
      setBusy(false);
    }
  }

  async function issue() {
    const sample = samples.find((s) => s.plot_id === plotId);
    if (!sample) return;
    const report = await check(sample.request);
    remember(report);
    setLast(report);
    return report.short_code
      ? t("pages.demo.lastReport", { code: report.short_code, verdict: t(`verdict.${report.verdict}.label`) })
      : t("pages.demo.lastReport", { code: t("common.notAvailable"), verdict: t(`verdict.${report.verdict}.label`) });
  }

  if (disabled) return <p role="alert" className="rounded border-2 border-gray-700 p-3">{t("pages.demo.disabled")}</p>;
  const plots = Array.from(new Set(samples.map((s) => s.plot_id)));
  return (
    <div>
      <MockBanner />
      <h1 className="text-2xl font-bold">{t("pages.demo.title")}</h1>
      <p className="mt-1 text-gray-700">{t("pages.demo.intro")}</p>

      <label htmlFor="demo-plot" className="mt-4 block font-bold">{t("pages.demo.plot")}</label>
      <select id="demo-plot" value={plotId} onChange={(e) => setPlotId(e.target.value)} className="mt-1 block min-h-tap w-full rounded border border-gray-500 px-3 py-2">
        {(plots.length ? plots : [plotId]).map((p) => <option key={p} value={p}>{p}</option>)}
      </select>

      <p role="status" className="mt-3 min-h-6 font-bold">{busy ? t("pages.demo.working") : message}</p>
      {error ? <ErrorNotice error={error} /> : null}

      <h2 className="mt-6 text-xl font-bold">{t("pages.demo.ledgerTitle")}</h2>
      {!ledger ? <Spinner /> : (
        <div>
          <p className="font-bold" data-testid="ledger-status">
            <span aria-hidden="true" className="mr-1">{ledger.ok ? "✓" : "✕"}</span>
            {ledger.ok ? t("pages.demo.statusOk") : `${t("pages.demo.statusBroken")}: ${localizeParams(t, lang, { reason: ledger.reason ?? "" }, "R-INT-01").reason}`}
          </p>
          <div className="overflow-x-auto">
            <table className="mt-2 w-full border-collapse text-sm">
              <thead><tr className="text-left">
                <th className="border-b p-1">{t("pages.demo.colSeq")}</th><th className="border-b p-1">{t("pages.demo.colSource")}</th>
                <th className="border-b p-1">{t("pages.demo.colRecord")}</th><th className="border-b p-1">{t("pages.demo.colStatus")}</th>
              </tr></thead>
              <tbody>
                {ledger.entries.map((e) => (
                  <tr key={e.seq} className={e.status === "broken" ? "bg-red-50 font-bold" : ""}>
                    <td className="border-b p-1">{e.seq}</td><td className="border-b p-1">{t(`sources.${e.source}`)}</td>
                    <td className="border-b p-1 font-mono">{e.record_id}</td>
                    <td className="border-b p-1"><span aria-hidden="true">{e.status === "ok" ? "✓ " : "✕ "}</span>{e.status === "ok" ? t("pages.demo.entryOk") : t("pages.demo.entryBroken")}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="mt-1 text-sm text-gray-700">
            {ledger.checkpoint
              ? `${ledger.checkpoint.valid ? t("pages.demo.checkpointValid") : t("pages.demo.checkpointInvalid")} · ${fmtDateTime(ledger.checkpoint.ts, lang)}`
              : t("pages.demo.noCheckpoint")}
          </p>
        </div>
      )}

      <h2 className="mt-6 text-xl font-bold">{t("pages.demo.issueTitle")}</h2>
      <div className="mt-2 flex flex-col gap-2 sm:flex-row">
        <button type="button" className={btn} disabled={busy} onClick={() => void act(issue)}>{t("pages.demo.issue")}</button>
        {last?.short_code ? <Link to={`/verify?code=${encodeURIComponent(last.short_code)}`} className={`${btn} inline-flex items-center`}>{t("pages.demo.verifyLast")}</Link> : null}
      </div>

      <h2 className="mt-6 text-xl font-bold">{t("pages.demo.tamperTitle")}</h2>
      <div className="mt-2 grid grid-cols-1 gap-2 sm:grid-cols-2">
        {TAMPER.map((k) => <button key={k} type="button" className={btn} disabled={busy} onClick={() => void act(async () => { await demoTamper(plotId, k); })}>{t(`pages.demo.tamper.${k}`)}</button>)}
      </div>

      <h2 className="mt-6 text-xl font-bold">{t("pages.demo.addTitle")}</h2>
      <div className="mt-2 grid grid-cols-1 gap-2 sm:grid-cols-2">
        {ADD.map((k) => <button key={k} type="button" className={btn} disabled={busy} onClick={() => void act(async () => { await demoAddEvent(plotId, k); })}>{t(`pages.demo.add.${k}`)}</button>)}
      </div>

      <h2 className="mt-6 text-xl font-bold">{t("pages.demo.clockTitle")}</h2>
      <div className="mt-2 flex items-end gap-2">
        <div>
          <label htmlFor="demo-days" className="block font-bold">{t("pages.demo.clockDays")}</label>
          <input id="demo-days" inputMode="numeric" value={days} onChange={(e) => setDays(e.target.value)} className="mt-1 block min-h-tap w-28 rounded border border-gray-500 px-3 py-2" />
        </div>
        <button type="button" className={btn} disabled={busy || !/^\d+$/.test(days)} onClick={() => void act(async () => { await demoClock(Number(days)); })}>{t("pages.demo.clockApply")}</button>
      </div>

      <h2 className="mt-6 text-xl font-bold">{t("pages.demo.resetTitle")}</h2>
      <button type="button" className={`${btn} mt-2`} disabled={busy} onClick={() => void act(async () => { await demoReset(); await demoClock(0); setLast(null); })}>{t("pages.demo.reset")}</button>

      <h2 className="mt-8 text-xl font-bold">{t("pages.demo.scriptTitle")}</h2>
      <ol className="mt-1 list-decimal space-y-1 pl-6">
        <li>{t("pages.demo.script1")}</li><li>{t("pages.demo.script2")}</li><li>{t("pages.demo.script3")}</li>
      </ol>
    </div>
  );
}
