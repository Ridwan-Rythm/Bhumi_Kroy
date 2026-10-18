import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { qrDataUrl } from "../lib/qr";
import { verifyUrl } from "../lib/verifyLocal";
import ReportView from "../components/ReportView";
import { ErrorNotice, Spinner } from "../components/ui";
import { useReport } from "./Result";

// The Layout footer (disclaimer + SYNTHETIC strip) prints too. This page adds a diagonal watermark on every
// printed page and a QR block with the verification link in text, so a paper copy can still be checked.
export default function PrintReport() {
  const { t } = useTranslation();
  const { reportId } = useParams();
  const { report, error, reload } = useReport(reportId);
  const [qr, setQr] = useState<string | null>(null);
  const url = report?.signed_payload_b64 && report.signature_b64
    ? verifyUrl(window.location.origin, report.signed_payload_b64, report.signature_b64)
    : null;
  useEffect(() => {
    let live = true;
    if (url) void qrDataUrl(url).then((s) => live && setQr(s)).catch(() => live && setQr(null));
    return () => { live = false; };
  }, [url]);

  if (error) return <ErrorNotice error={error} title={t("pages.result.loadFailed")} onRetry={reload} />;
  if (!report) return <Spinner />;
  return (
    <div>
      <div aria-hidden="true" data-testid="print-watermark"
        className="pointer-events-none fixed inset-0 z-0 hidden items-center justify-center overflow-hidden print:flex">
        <span className="-rotate-[30deg] select-none text-8xl font-black tracking-widest text-gray-500/20">{t("footer.watermarkShort")}</span>
      </div>
      <div className="relative z-10">
        <div className="mb-4 flex flex-wrap gap-3 print:hidden">
          <button type="button" onClick={() => window.print()} className="btn-primary">{t("common.print")}</button>
          <Link to={`/result/${encodeURIComponent(reportId ?? "")}`} className="nav-link link-arrow">{t("pages.print.back")}</Link>
        </div>
        <p className="mb-3 text-sm text-slate-600 print:hidden">{t("pages.print.hint")}</p>
        <h1 className="mb-3 text-2xl font-bold">{t("pages.print.title")}</h1>
        <ReportView report={report} forPrint />
        {url ? (
          <section className="mt-6 flex items-center gap-4 break-inside-avoid border-t border-gray-400 pt-4">
            {qr ? <img src={qr} width={160} height={160} alt={t("pages.result.qrAlt")} /> : null}
            <div className="min-w-0">
              <p className="font-bold">{t("pages.result.qrTitle")}</p>
              <p className="font-mono text-lg tracking-widest">{report.short_code}</p>
              <p className="break-all text-xs text-gray-700">{t("pages.print.verifyAt", { url: `${window.location.origin}/verify` })}</p>
            </div>
          </section>
        ) : null}
      </div>
    </div>
  );
}
