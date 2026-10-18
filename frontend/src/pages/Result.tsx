import { useCallback, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { useTranslation } from "react-i18next";
import type { Report } from "../types/contract";
import { getReport } from "../api/client";
import { ALERT_KEY, recall } from "../lib/reportStore";
import ReportView from "../components/ReportView";
import { ErrorNotice, MockBanner, Spinner } from "../components/ui";

export function useReport(reportId: string | undefined) {
  const [report, setReport] = useState<Report | null>(() => (reportId ? recall(reportId) ?? null : null));
  const [error, setError] = useState<unknown>(null);
  const load = useCallback(() => {
    if (!reportId) return;
    const known = recall(reportId);
    if (known) { setReport(known); return; }
    setError(null);
    if (reportId === ALERT_KEY) { setError(new Error("alert reports are not stored")); return; }
    getReport(reportId).then(setReport).catch(setError);
  }, [reportId]);
  useEffect(load, [load]);
  return { report, error, reload: load };
}


export default function Result() {
  const { t } = useTranslation();
  const { reportId } = useParams();
  const { report, error, reload } = useReport(reportId);

  if (error) return <ErrorNotice error={error} title={t("pages.result.loadFailed")} onRetry={reload} />;
  if (!report) return <Spinner />;
  const key = report.report_id ?? ALERT_KEY;
  return (
    <div>
      <MockBanner />
      <h1 className="sr-only">{t("pages.result.title")}</h1>
      <ReportView report={report} />
      <nav className="mt-10 flex flex-col gap-3 sm:flex-row">
        {report.report_id ? <Link to={`/report/${encodeURIComponent(key)}/print`} className="btn-primary">{t("pages.result.printCta")}</Link> : null}
        <Link to={report.short_code ? `/verify?code=${encodeURIComponent(report.short_code)}` : "/verify"} className="btn-secondary">{t("pages.result.verifyCta")}</Link>
        <Link to="/check" className="btn-quiet">{t("pages.result.newCheck")}</Link>
      </nav>
    </div>
  );
}
