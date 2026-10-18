import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import type { Coverage, Finding, Q, Report, SourceResult, TimelineEvent } from "../types/contract";
import { fmtDate, fmtDateTime, fmtNumber } from "../lib/format";
import { findingText, localizeParams, notCheckedText } from "../lib/localize";
import { SEVERITY_STYLE, VERDICT_STYLE } from "../lib/verdict";
import { qrDataUrl } from "../lib/qr";
import { verifyUrl } from "../lib/verifyLocal";
import { Section } from "./ui";

const QUESTIONS: Q[] = ["Q1", "Q2", "Q3", "Q4", "Q5", "Q6"];
const COVERAGE_ICON: Record<Coverage, string> = { COVERED: "✓", PARTIAL: "◐", NOT_COVERED: "✕" };
const COVERAGE_BOX: Record<Coverage, string> = {
  COVERED: "border-green-600 bg-green-50/70",
  PARTIAL: "border-amber-500 bg-amber-50/70",
  NOT_COVERED: "border-slate-400 border-dashed bg-slate-50/70",
};

export function VerdictBanner({ verdict }: { verdict: Report["verdict"] }) {
  const { t } = useTranslation();
  const style = VERDICT_STYLE[verdict];
  return (
    <div role="status" className={`relative animate-pop overflow-hidden rounded-2xl border-2 border-l-[10px] p-5 shadow-lift sm:p-6 ${style.box}`} data-verdict={verdict}>
      <span aria-hidden="true" className="print-hide-decor pointer-events-none absolute -right-10 -top-10 h-40 w-40 rounded-full bg-current opacity-[.07]" />
      <p className="relative flex items-center gap-4 text-2xl font-bold">
        <span aria-hidden="true" className="relative flex h-14 w-14 shrink-0 items-center justify-center"><span className="print-hide-decor absolute inset-0 animate-ping2 rounded-full bg-current opacity-30" /><span className="relative flex h-14 w-14 items-center justify-center rounded-full bg-white text-3xl shadow-soft">{style.icon}</span></span>
        <span>{t(`verdict.${verdict}.label`)}</span>
      </p>
      <p className="relative mt-3 text-base text-slate-900">{t(`verdict.${verdict}.summary`)}</p>
    </div>
  );
}

function Summary({ report }: { report: Report }) {
  const { t, i18n } = useTranslation();
  const lang = i18n.language;
  const { plot, seller } = report;
  return (
    <dl className="stagger mt-5 grid grid-cols-1 gap-3 text-base sm:grid-cols-2 [&>div]:card [&>div]:card-hover [&>div]:p-4 [&_dt]:text-sm [&_dt]:uppercase [&_dt]:tracking-wide [&_dt]:text-brand-700">
      <div>
        <dt className="font-bold">{t("pages.result.plotTitle")}</dt>
        <dd>{t("pages.result.khatianDag", { khatian: plot.khatian_no, dag: plot.dag_no })}</dd>
        {plot.area_decimal !== null ? <dd>{t("pages.result.area", { area: fmtNumber(plot.area_decimal, lang) })}</dd> : null}
      </div>
      <div>
        <dt className="font-bold">{t("pages.result.sellerTitle")}</dt>
        <dd lang="bn">{seller.name}</dd>
        <dd>{t("pages.result.nameMatch", { tier: t(`matchTier.${seller.match.tier}`) })}</dd>
        <dd>{t("pages.result.holders", { count: report.holders_summary.holder_count })}</dd>
      </div>
      <div>
        <dt className="font-bold">{t("pages.result.reportId")}</dt>
        <dd>{report.report_id ?? t("pages.result.noReportId")}</dd>
      </div>
      <div>
        <dt className="font-bold">{t("pages.result.shortCode")}</dt>
        <dd className="font-mono text-xl font-bold tracking-widest text-brand-900">{report.short_code ?? t("common.notAvailable")}</dd>
      </div>
      <div>
        <dt className="font-bold">{t("pages.result.issued")}</dt>
        <dd>{fmtDateTime(report.issued_at, lang)}</dd>
      </div>
      {report.valid_until ? (
        <div>
          <dt className="font-bold">{t("pages.result.validUntil")}</dt>
          <dd>{fmtDateTime(report.valid_until, lang)}</dd>
        </div>
      ) : null}
    </dl>
  );
}

function Coverage_({ report }: { report: Report }) {
  const { t } = useTranslation();
  return (
    <ul className="stagger grid grid-cols-1 gap-3 sm:grid-cols-2">
      {QUESTIONS.map((q) => {
        const c = report.coverage[q];
        return (
          <li key={q} className={`card-hover flex items-start gap-3 rounded-xl border-2 p-3 shadow-sm ${COVERAGE_BOX[c]}`}>
            <span aria-hidden="true" className="mt-0.5 w-6 text-center text-xl font-bold">{COVERAGE_ICON[c]}</span>
            <span>
              <span className="block">{t(`questions.${q}`)}</span>
              <span className="block font-bold">{t(`coverage.${c}`)}</span>
            </span>
          </li>
        );
      })}
    </ul>
  );
}

function FindingCard({ f }: { f: Finding }) {
  const { t, i18n } = useTranslation();
  const text = findingText(t, i18n.language, f);
  return (
    <li className="card card-hover border-l-4 border-l-gold-500 p-4" data-rule={f.rule_id}>
      <p className="flex flex-wrap items-center gap-2">
        <span className={`rounded-full px-3 py-0.5 text-sm font-bold ${SEVERITY_STYLE[f.severity] ?? ""}`}>{t(`severity.${f.severity}`)}</span>
        <span className="text-sm text-slate-600">{t(`confidence.${f.confidence}`)}</span>
        {f.question ? <span className="rounded-full bg-slate-100 px-2 text-sm text-slate-700">{f.question}</span> : null}
      </p>
      <h3 className="mt-2 text-lg font-bold text-brand-900">{text.title}</h3>
      <p className="mt-1">{text.explain}</p>
      <p className="mt-3 rounded-xl bg-brand-50 p-3">
        <span className="font-bold text-brand-800">{t("rules.nextStep")}: </span>
        {text.next}
      </p>
      {f.evidence.length > 0 ? (
        <p className="mt-3 text-sm text-slate-600">
          {t("rules.evidence")}: <span className="font-mono">{f.evidence.join(", ")}</span>
        </p>
      ) : null}
    </li>
  );
}

function SourcesTable({ sources }: { sources: SourceResult[] }) {
  const { t, i18n } = useTranslation();
  const lang = i18n.language;
  return (
    <ul className="card divide-y divide-slate-200 overflow-hidden">
      {sources.map((s) => (
        <li key={s.source} className="p-3 transition-colors hover:bg-brand-50/70">
          <p className="flex flex-wrap justify-between gap-2">
            <span className="font-bold text-brand-900">{t(`sources.${s.source}`)}</span>
            <span className="rounded-full bg-brand-100 px-3 text-sm font-medium text-brand-800">{t(`sourceStatus.${s.status}`)}</span>
          </p>
          <p className="mt-1 text-sm text-slate-600">
            {t("maturity.label", { level: s.maturity })}
            {s.as_of ? ` · ${t("pages.result.asOf", { date: fmtDate(s.as_of, lang) })}` : ""}
            {s.linkage ? ` · ${t(`linkage.${s.linkage}`)}` : ""}
            {s.reason ? ` · ${t(`reasons.${s.reason}`)}` : ""}
            {` · ${t("pages.result.recordCount", { count: s.record_count })}`}
          </p>
        </li>
      ))}
    </ul>
  );
}

function Timeline({ events }: { events: TimelineEvent[] }) {
  const { t, i18n } = useTranslation();
  const lang = i18n.language;
  if (events.length === 0) return <p>{t("pages.result.noTimeline")}</p>;
  return (
    <ol className="stagger relative space-y-3 border-l-4 border-brand-200 pl-5">
      {events.map((e) => (
        <li key={`${e.record_ref}-${e.date}`} className={`relative rounded-xl p-2 transition-colors before:absolute before:-left-[1.95rem] before:top-3 before:h-3.5 before:w-3.5 before:rounded-full before:border-2 before:border-white before:bg-brand-500 before:shadow before:content-[''] hover:bg-brand-50/70 ${e.flagged_by.length ? "bg-amber-50 before:bg-amber-500" : ""}`}>
          <p className="font-bold">
            {fmtDate(e.date, lang)}: {t(`events.${e.kind}`)}
            {e.survey ? ` (${t(`surveyShort.${e.survey}`)})` : ""}
          </p>
          {e.from_masked || e.to_masked ? (
            <p lang="bn">{t("pages.result.timelineMove", { from: e.from_masked ?? "—", to: e.to_masked ?? "—" })}</p>
          ) : null}
          <p className="text-sm text-slate-600">
            <span className="font-mono">{e.record_ref}</span> · {t(`sources.${e.source}`)}
            {e.share ? ` · ${e.share}` : ""}
            {e.area_decimal !== null ? ` · ${t("pages.result.area", { area: fmtNumber(e.area_decimal, lang) })}` : ""}
          </p>
          {e.flagged_by.length ? <p className="text-sm font-bold">{t("pages.result.flagged", { rules: e.flagged_by.join(", ") })}</p> : null}
        </li>
      ))}
    </ol>
  );
}

export function LedgerLine({ report }: { report: Report }) {
  const { t, i18n } = useTranslation();
  const { ledger } = report;
  const reason = ledger.reason ? localizeParams(t, i18n.language, { reason: ledger.reason }, "R-INT-01").reason : "";
  return (
    <p className={`card flex items-center gap-3 p-4 font-medium ${ledger.ok ? "text-green-800" : "text-red-800"}`}>
      <span aria-hidden="true" className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full font-bold text-white ${ledger.ok ? "bg-green-600" : "bg-red-700"}`}>{ledger.ok ? "✓" : "✕"}</span>
      {ledger.ok
        ? t("pages.result.ledgerOk", { height: fmtNumber(ledger.height, i18n.language) })
        : t("pages.result.ledgerBroken", { reason })}
    </p>
  );
}

// The QR is drawn only when the report is signed (an INTEGRITY_ALERT report has no payload).
export function VerifyQr({ report }: { report: Report }) {
  const { t } = useTranslation();
  const [src, setSrc] = useState<string | null>(null);
  const url = report.signed_payload_b64 && report.signature_b64
    ? verifyUrl(window.location.origin, report.signed_payload_b64, report.signature_b64)
    : null;
  useEffect(() => {
    let live = true;
    if (url) void qrDataUrl(url).then((s) => live && setSrc(s)).catch(() => live && setSrc(null));
    return () => { live = false; };
  }, [url]);
  if (!url) return null;
  return (
    <figure className="card card-hover mt-2 inline-block p-4 text-center">
      {src ? <img src={src} width={176} height={176} alt={t("pages.result.qrAlt")} className="rounded-lg" /> : null}
      <figcaption className="mt-2 text-sm font-bold text-brand-900">{t("pages.result.qrTitle")}</figcaption>
    </figure>
  );
}

// One body for the Result screen and the printable report, so the two can never disagree.
export default function ReportView({ report, forPrint = false }: { report: Report; forPrint?: boolean }) {
  const { t } = useTranslation();
  return (
    <article data-testid="report">
      <VerdictBanner verdict={report.verdict} />
      <Summary report={report} />
      <Section id="sec-coverage" title={t("pages.result.coverageTitle")}><Coverage_ report={report} /></Section>
      <Section id="sec-findings" title={t("pages.result.findingsTitle")}>
        {report.findings.length === 0 ? <p>{t("pages.result.noFindings")}</p> : (
          <ul className="stagger space-y-3">{report.findings.map((f, i) => <FindingCard key={`${f.rule_id}-${i}`} f={f} />)}</ul>
        )}
      </Section>
      <Section id="sec-notchecked" title={t("pages.result.notCheckedTitle")}>
        <p className="mb-3 text-slate-700">{t("pages.result.notCheckedHelp")}</p>
        <NotCheckedList report={report} />
      </Section>
      <Section id="sec-sources" title={t("pages.result.sourcesTitle")}><SourcesTable sources={report.sources} /></Section>
      <Section id="sec-timeline" title={t("pages.result.timelineTitle")}><Timeline events={report.timeline} /></Section>
      <Section id="sec-ledger" title={t("pages.result.ledgerTitle")}><LedgerLine report={report} /></Section>
      {forPrint ? null : (
        <Section id="sec-qr" title={t("pages.result.qrTitle")}><VerifyQr report={report} /></Section>
      )}
    </article>
  );
}

function NotCheckedList({ report }: { report: Report }) {
  const { t, i18n } = useTranslation();
  return (
    <ul className="card list-disc space-y-1.5 p-4 pl-9 marker:text-gold-600">
      {report.not_checked.map((n, i) => <li key={`${n.code}-${i}`}>{notCheckedText(t, i18n.language, n)}</li>)}
    </ul>
  );
}
