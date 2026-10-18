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
  COVERED: "border-green-700",
  PARTIAL: "border-amber-600",
  NOT_COVERED: "border-gray-500 border-dashed",
};

export function VerdictBanner({ verdict }: { verdict: Report["verdict"] }) {
  const { t } = useTranslation();
  const style = VERDICT_STYLE[verdict];
  return (
    <div role="status" className={`rounded-lg border-4 p-4 ${style.box}`} data-verdict={verdict}>
      <p className="flex items-center gap-3 text-2xl font-bold">
        <span aria-hidden="true" className="text-3xl">{style.icon}</span>
        <span>{t(`verdict.${verdict}.label`)}</span>
      </p>
      <p className="mt-2 text-base text-gray-900">{t(`verdict.${verdict}.summary`)}</p>
    </div>
  );
}

function Summary({ report }: { report: Report }) {
  const { t, i18n } = useTranslation();
  const lang = i18n.language;
  const { plot, seller } = report;
  return (
    <dl className="mt-4 grid grid-cols-1 gap-2 text-base sm:grid-cols-2">
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
        <dd className="font-mono text-lg tracking-widest">{report.short_code ?? t("common.notAvailable")}</dd>
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
    <ul className="grid grid-cols-1 gap-2 sm:grid-cols-2">
      {QUESTIONS.map((q) => {
        const c = report.coverage[q];
        return (
          <li key={q} className={`flex items-start gap-3 rounded border-2 p-2 ${COVERAGE_BOX[c]}`}>
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
    <li className="rounded border border-gray-300 p-3" data-rule={f.rule_id}>
      <p className="flex flex-wrap items-center gap-2">
        <span className={`rounded px-2 py-0.5 text-sm font-bold ${SEVERITY_STYLE[f.severity] ?? ""}`}>{t(`severity.${f.severity}`)}</span>
        <span className="text-sm text-gray-700">{t(`confidence.${f.confidence}`)}</span>
        {f.question ? <span className="text-sm text-gray-700">{f.question}</span> : null}
      </p>
      <h3 className="mt-1 text-lg font-bold">{text.title}</h3>
      <p className="mt-1">{text.explain}</p>
      <p className="mt-2">
        <span className="font-bold">{t("rules.nextStep")}: </span>
        {text.next}
      </p>
      {f.evidence.length > 0 ? (
        <p className="mt-2 text-sm text-gray-700">
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
    <ul className="divide-y divide-gray-200 rounded border border-gray-300">
      {sources.map((s) => (
        <li key={s.source} className="p-2">
          <p className="flex flex-wrap justify-between gap-2">
            <span className="font-bold">{t(`sources.${s.source}`)}</span>
            <span>{t(`sourceStatus.${s.status}`)}</span>
          </p>
          <p className="text-sm text-gray-700">
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
    <ol className="space-y-2 border-l-4 border-gray-300 pl-3">
      {events.map((e) => (
        <li key={`${e.record_ref}-${e.date}`} className={e.flagged_by.length ? "rounded bg-amber-50 p-1" : ""}>
          <p className="font-bold">
            {fmtDate(e.date, lang)}: {t(`events.${e.kind}`)}
            {e.survey ? ` (${t(`surveyShort.${e.survey}`)})` : ""}
          </p>
          {e.from_masked || e.to_masked ? (
            <p lang="bn">{t("pages.result.timelineMove", { from: e.from_masked ?? "—", to: e.to_masked ?? "—" })}</p>
          ) : null}
          <p className="text-sm text-gray-700">
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
    <p>
      <span aria-hidden="true" className="mr-1 font-bold">{ledger.ok ? "✓" : "✕"}</span>
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
    <figure className="mt-2 inline-block text-center">
      {src ? <img src={src} width={176} height={176} alt={t("pages.result.qrAlt")} /> : null}
      <figcaption className="text-sm font-bold">{t("pages.result.qrTitle")}</figcaption>
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
          <ul className="space-y-3">{report.findings.map((f, i) => <FindingCard key={`${f.rule_id}-${i}`} f={f} />)}</ul>
        )}
      </Section>
      <Section id="sec-notchecked" title={t("pages.result.notCheckedTitle")}>
        <p className="mb-2 text-gray-700">{t("pages.result.notCheckedHelp")}</p>
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
    <ul className="list-disc space-y-1 pl-6">
      {report.not_checked.map((n, i) => <li key={`${n.code}-${i}`}>{notCheckedText(t, i18n.language, n)}</li>)}
    </ul>
  );
}
