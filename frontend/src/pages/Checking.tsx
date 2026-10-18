import { useEffect, useRef, useState } from "react";
import { Link, Navigate, useLocation, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import type { CheckRequest, SourceName } from "../types/contract";
import { check } from "../api/client";
import { remember } from "../lib/reportStore";
import { ErrorNotice, MockBanner, Spinner } from "../components/ui";

const SOURCES: SourceName[] = ["land_records", "registry", "mutation", "court", "khas", "bank"];

export default function Checking() {
  const { t } = useTranslation();
  const nav = useNavigate();
  const request = (useLocation().state as { request?: CheckRequest } | null)?.request;
  const [error, setError] = useState<unknown>(null);
  const started = useRef(false); // React StrictMode runs effects twice in dev: send the request once

  const run = (req: CheckRequest) => {
    setError(null);
    check(req)
      .then((report) => nav(`/result/${encodeURIComponent(remember(report))}`, { replace: true }))
      .catch(setError);
  };
  useEffect(() => {
    if (request && !started.current) { started.current = true; run(request); }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (!request) return <Navigate to="/check" replace />;
  return (
    <section>
      <MockBanner />
      <h1 className="text-2xl font-bold">{t("pages.checking.title")}</h1>
      {error ? (
        <div className="mt-4 space-y-3">
          <ErrorNotice error={error} title={t("pages.checking.failedTitle")} onRetry={() => run(request)} />
          <Link to="/check" className="inline-flex min-h-tap items-center underline">{t("pages.checking.backToForm")}</Link>
        </div>
      ) : (
        <>
          <p className="mt-2 text-gray-700">{t("pages.checking.subtitle")}</p>
          <div className="mt-4"><Spinner /></div>
          <h2 className="mt-6 font-bold">{t("pages.checking.listTitle")}</h2>
          <ul className="mt-1 list-disc pl-6">
            {SOURCES.map((s) => <li key={s}>{t(`sources.${s}`)}</li>)}
          </ul>
        </>
      )}
    </section>
  );
}
