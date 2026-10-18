import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import type { Q, SamplePlot } from "../types/contract";
import { getSamples } from "../api/client";
import { MockBanner } from "../components/ui";

const QUESTIONS: Q[] = ["Q1", "Q2", "Q3", "Q4", "Q5", "Q6"];

export default function Home() {
  const { t, i18n } = useTranslation();
  const [samples, setSamples] = useState<SamplePlot[]>([]);
  useEffect(() => {
    let live = true;
    getSamples().then((s) => live && setSamples(s)).catch(() => live && setSamples([]));
    return () => { live = false; };
  }, []);

  return (
    <div>
      <MockBanner />
      <section className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-brand-900 via-brand-800 to-brand-600 p-6 text-white shadow-lift sm:p-10">
        <div aria-hidden="true" className="print-hide-decor pointer-events-none absolute inset-0">
          <div className="grid-dots absolute inset-0 opacity-30 [mask-image:linear-gradient(135deg,transparent,#000_70%)]" />
          <div className="blob -right-16 -top-16 h-64 w-64 bg-gold-400/30" />
          <div className="blob -bottom-20 left-10 h-56 w-56 bg-brand-300/30 [animation-delay:-5s]" />
          <svg viewBox="0 0 200 200" className="absolute -bottom-6 -right-4 hidden h-64 w-64 animate-float text-white/15 sm:block">
            <path d="M20 150 100 40l80 110z" fill="none" stroke="currentColor" strokeWidth="6" strokeLinejoin="round" />
            <path d="M50 150h100M100 40v110M60 120h80M75 95h50" stroke="currentColor" strokeWidth="5" strokeLinecap="round" />
            <circle cx="100" cy="40" r="10" fill="#f5c04a" />
          </svg>
        </div>
        <div className="relative max-w-2xl">
          <h1 className="animate-fade-up text-3xl font-bold leading-tight sm:text-4xl">{t("pages.home.promise")}</h1>
          <p className="mt-4 animate-fade-up text-lg text-brand-50/95 [animation-delay:.12s]">{t("pages.home.lead")}</p>
          <div className="mt-6 flex animate-fade-up flex-col gap-3 [animation-delay:.24s] sm:flex-row">
            <Link to="/check" className="btn group bg-gradient-to-r from-gold-400 to-gold-500 text-brand-950 shadow-soft hover:-translate-y-0.5 hover:shadow-glow">
              {t("pages.home.start")}
              <span aria-hidden="true" className="transition-transform duration-300 group-hover:translate-x-1.5">→</span>
            </Link>
            <Link to="/verify" className="btn border-2 border-white/60 text-white backdrop-blur hover:-translate-y-0.5 hover:border-white hover:bg-white/15">{t("pages.home.verifyCta")}</Link>
          </div>
          <p className="mt-4 animate-fade-in text-sm text-brand-100 [animation-delay:.4s]">{t("pages.home.syntheticNote")}</p>
        </div>
      </section>

      <h2 className="heading-accent mt-10 text-xl font-bold text-brand-900">{t("pages.home.howTitle")}</h2>
      <ol className="steps stagger mt-3">
        <li>{t("pages.home.step1")}</li>
        <li>{t("pages.home.step2")}</li>
        <li>{t("pages.home.step3")}</li>
      </ol>

      <h2 className="heading-accent mt-10 text-xl font-bold text-brand-900">{t("pages.home.checksTitle")}</h2>
      <ul className="ticks stagger mt-3 grid grid-cols-1 gap-3 sm:grid-cols-2">
        {QUESTIONS.map((q) => <li key={q}>{t(`questions.${q}`)}</li>)}
      </ul>

      {samples.length > 0 ? (
        <>
          <h2 className="heading-accent mt-10 text-xl font-bold text-brand-900">{t("pages.home.samplesTitle")}</h2>
          <p className="mt-1 text-slate-700">{t("pages.home.samplesHelp")}</p>
          <ul className="stagger mt-3 grid grid-cols-1 gap-3 sm:grid-cols-2">
            {samples.map((s) => (
              <li key={s.sample_id}>
                <Link to={`/check?sample=${encodeURIComponent(s.sample_id)}`} className="card card-hover link-arrow flex min-h-tap items-center px-4 py-3 font-medium text-brand-900 hover:text-brand-600">
                  <span className="flex-1">{s.sample_id}: {i18n.language === "bn" ? s.label_bn : s.label_en}</span>
                </Link>
              </li>
            ))}
          </ul>
        </>
      ) : null}

      <p className="mt-10"><Link to="/demo" className="nav-link link-arrow">{t("pages.home.demoLink")}</Link></p>
    </div>
  );
}
