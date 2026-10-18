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
    <section className="mx-auto max-w-2xl">
      <MockBanner />
      <h1 className="gradient-text text-3xl font-bold">{t("pages.checking.title")}</h1>
      {error ? (
        <div className="mt-4 space-y-3">
          <ErrorNotice error={error} title={t("pages.checking.failedTitle")} onRetry={() => run(request)} />
          <Link to="/check" className="nav-link link-arrow">{t("pages.checking.backToForm")}</Link>
        </div>
      ) : (
        <>
          <p className="mt-2 text-slate-700">{t("pages.checking.subtitle")}</p>
          <div className="card relative mt-5 overflow-hidden p-5">
            <div aria-hidden="true" className="absolute inset-x-0 top-0 h-1 overflow-hidden bg-brand-100">
              <div className="h-full w-2/5 animate-scan rounded-full bg-gradient-to-r from-brand-400 via-gold-400 to-brand-600" />
            </div>
            <Spinner />
            <h2 className="heading-accent mt-6 font-bold text-brand-900">{t("pages.checking.listTitle")}</h2>
            <ul className="mt-3 grid grid-cols-1 gap-2 sm:grid-cols-2">
              {SOURCES.map((s, i) => (
                <li key={s} className="flex items-center gap-3 rounded-xl border border-brand-100 bg-brand-50/60 px-3 py-2.5 transition-colors hover:bg-brand-100/70">
                  <span aria-hidden="true" className="h-2.5 w-2.5 shrink-0 animate-blink rounded-full bg-brand-500" style={{ animationDelay: `${i * 0.25}s` }} />
                  {t(`sources.${s}`)}
                </li>
              ))}
            </ul>
          </div>
        </>
      )}
    </section>
  );
}
