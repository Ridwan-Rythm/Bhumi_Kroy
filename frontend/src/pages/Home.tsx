import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import type { Q, SamplePlot } from "../types/contract";
import { getSamples } from "../api/client";
import { MockBanner } from "../components/ui";

const QUESTIONS: Q[] = ["Q1", "Q2", "Q3", "Q4", "Q5", "Q6"];
const button = "inline-flex min-h-tap items-center justify-center rounded px-4 py-2 text-lg font-bold";

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
      <h1 className="text-3xl font-bold">{t("pages.home.promise")}</h1>
      <p className="mt-3 text-lg">{t("pages.home.lead")}</p>
      <div className="mt-4 flex flex-col gap-3 sm:flex-row">
        <Link to="/check" className={`${button} bg-gray-900 text-white`}>{t("pages.home.start")}</Link>
        <Link to="/verify" className={`${button} border-2 border-gray-900`}>{t("pages.home.verifyCta")}</Link>
      </div>
      <p className="mt-3 text-sm text-gray-700">{t("pages.home.syntheticNote")}</p>

      <h2 className="mt-8 text-xl font-bold">{t("pages.home.howTitle")}</h2>
      <ol className="mt-2 list-decimal space-y-1 pl-6">
        <li>{t("pages.home.step1")}</li>
        <li>{t("pages.home.step2")}</li>
        <li>{t("pages.home.step3")}</li>
      </ol>

      <h2 className="mt-8 text-xl font-bold">{t("pages.home.checksTitle")}</h2>
      <ul className="mt-2 list-disc space-y-1 pl-6">
        {QUESTIONS.map((q) => <li key={q}>{t(`questions.${q}`)}</li>)}
      </ul>

      {samples.length > 0 ? (
        <>
          <h2 className="mt-8 text-xl font-bold">{t("pages.home.samplesTitle")}</h2>
          <p className="text-gray-700">{t("pages.home.samplesHelp")}</p>
          <ul className="mt-2 grid grid-cols-1 gap-2 sm:grid-cols-2">
            {samples.map((s) => (
              <li key={s.sample_id}>
                <Link to={`/check?sample=${encodeURIComponent(s.sample_id)}`} className="flex min-h-tap items-center rounded border border-gray-400 px-3 py-2 underline">
                  {s.sample_id}: {i18n.language === "bn" ? s.label_bn : s.label_en}
                </Link>
              </li>
            ))}
          </ul>
        </>
      ) : null}

      <p className="mt-8"><Link to="/demo" className="inline-flex min-h-tap items-center underline">{t("pages.home.demoLink")}</Link></p>
    </div>
  );
}
