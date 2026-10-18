import { useEffect, useId, useRef, useState } from "react";
import type { FormEvent, ReactNode } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useTranslation } from "react-i18next";
import type { CheckRequest, Locations, SamplePlot, Survey } from "../types/contract";
import { getLocations, getSamples } from "../api/client";
import { toAsciiDigits } from "../lib/digits";
import { ErrorNotice, MockBanner, Spinner } from "../components/ui";

interface FormState {
  district: string; upazila: string; mouza: string; survey: string;
  khatian: string; dag: string; name: string; father: string; bank: boolean;
}
const EMPTY: FormState = { district: "", upazila: "", mouza: "", survey: "", khatian: "", dag: "", name: "", father: "", bank: true };
const SURVEYS: Survey[] = ["CS", "SA", "RS", "BS"];
const REQUIRED: (keyof FormState)[] = ["district", "upazila", "mouza", "khatian", "dag", "name"];
const control = "control mt-1.5";

function Field({ label, error, help, optional, children, id }: { label: string; error?: string; help?: string; optional?: boolean; children: ReactNode; id: string }) {
  const { t } = useTranslation();
  return (
    <div className="mt-4">
      <label htmlFor={id} className="font-bold text-brand-900">
        {label} {optional ? <span className="font-normal text-slate-600">{t("common.optional")}</span> : null}
      </label>
      {children}
      {help ? <p id={`${id}-help`} className="mt-1 text-sm text-slate-600">{help}</p> : null}
      {error ? <p id={`${id}-err`} className="mt-1 animate-fade-up text-sm font-bold text-red-800">{error}</p> : null}
    </div>
  );
}

function fromRequest(req: CheckRequest): FormState {
  return {
    district: req.plot.district_id, upazila: req.plot.upazila_id, mouza: req.plot.mouza_id, survey: req.plot.survey ?? "",
    khatian: req.plot.khatian_no, dag: req.plot.dag_no, name: req.seller.name, father: req.seller.father_or_husband ?? "",
    bank: req.consents?.bank ?? true,
  };
}

export default function Form() {
  const { t, i18n } = useTranslation();
  const nav = useNavigate();
  const [params] = useSearchParams();
  const uid = useId();
  const [locations, setLocations] = useState<Locations | null>(null);
  const [samples, setSamples] = useState<SamplePlot[]>([]);
  const [loadError, setLoadError] = useState<unknown>(null);
  const [form, setForm] = useState<FormState>(EMPTY);
  const [errors, setErrors] = useState<Partial<Record<keyof FormState, true>>>({});
  const summary = useRef<HTMLParagraphElement>(null);
  const [attempt, setAttempt] = useState(0);
  useEffect(() => {
    if (attempt > 0 && Object.keys(errors).length > 0) summary.current?.focus();
  }, [attempt, errors]);
  const bn = i18n.language === "bn";
  const label = (u: { name_bn: string; name_en: string }) => (bn ? u.name_bn : u.name_en);

  const load = () => {
    setLoadError(null);
    Promise.all([getLocations(), getSamples()])
      .then(([l, s]) => { setLocations(l); setSamples(s); })
      .catch(setLoadError);
  };
  useEffect(load, []);

  const wanted = params.get("sample");
  useEffect(() => {
    const s = samples.find((x) => x.sample_id === wanted);
    if (s) setForm(fromRequest(s.request));
  }, [samples, wanted]);

  const set = <K extends keyof FormState>(k: K, v: FormState[K]) => setForm((f) => ({ ...f, [k]: v }));
  const district = locations?.districts.find((d) => d.id === form.district);
  const upazila = district?.upazilas.find((u) => u.id === form.upazila);

  function submit(e: FormEvent) {
    e.preventDefault();
    const bad: Partial<Record<keyof FormState, true>> = {};
    for (const k of REQUIRED) if (String(form[k]).trim() === "") bad[k] = true;
    setErrors(bad);
    setAttempt((n) => n + 1); // the summary does not exist until this render finishes; the effect below focuses it
    if (Object.keys(bad).length > 0) return;
    const request: CheckRequest = {
      plot: {
        district_id: form.district, upazila_id: form.upazila, mouza_id: form.mouza,
        survey: (form.survey || undefined) as Survey | undefined,
        khatian_no: toAsciiDigits(form.khatian).trim(), dag_no: toAsciiDigits(form.dag).trim(),
      },
      seller: { name: form.name.trim(), father_or_husband: form.father.trim() || undefined },
      consents: { bank: form.bank },
    };
    nav("/checking", { state: { request } });
  }

  if (loadError) return <ErrorNotice error={loadError} title={t("pages.check.loadFailed")} onRetry={load} />;
  if (!locations) return <Spinner />;

  const fe = (k: keyof FormState) => (errors[k] ? t("pages.check.fieldRequired") : undefined);
  const a11y = (k: keyof FormState, id: string, help = false) => ({
    "aria-invalid": errors[k] ? true : undefined,
    "aria-required": REQUIRED.includes(k) ? true : undefined,
    "aria-describedby": [help ? `${id}-help` : "", errors[k] ? `${id}-err` : ""].filter(Boolean).join(" ") || undefined,
  });
  const id = (n: string) => `${uid}-${n}`;

  return (
    <form onSubmit={submit} noValidate className="mx-auto max-w-2xl">
      <MockBanner />
      <h1 className="gradient-text text-3xl font-bold">{t("pages.check.title")}</h1>
      <p className="mt-2 text-slate-700">{t("pages.check.intro")}</p>
      {Object.keys(errors).length > 0 ? (
        <p ref={summary} tabIndex={-1} role="alert" className="mt-4 animate-pop rounded-2xl border-2 border-red-300 border-l-8 border-l-red-700 bg-red-50 p-3 font-bold text-red-900">{t("pages.check.fixErrors")}</p>
      ) : null}

      <div className="card mt-5 border-gold-400/40 bg-gradient-to-br from-amber-50/90 to-white p-4 sm:p-5"><Field id={id("sample")} label={t("pages.check.sample")} optional>
        <select id={id("sample")} className={control} value="" onChange={(e) => { const s = samples.find((x) => x.sample_id === e.target.value); if (s) { setForm(fromRequest(s.request)); setErrors({}); } }}>
          <option value="">{t("common.select")}</option>
          {samples.map((s) => <option key={s.sample_id} value={s.sample_id}>{s.sample_id}: {bn ? s.label_bn : s.label_en}</option>)}
        </select>
      </Field>

      </div>

      <fieldset className="card mt-5 p-4 sm:p-6">
        <legend className="heading-accent float-left mb-1 w-full text-xl font-bold text-brand-900">{t("pages.check.plotTitle")}</legend>
        <div className="clear-both" />
        <Field id={id("district")} label={t("pages.check.district")} error={fe("district")}>
          <select id={id("district")} className={control} value={form.district} {...a11y("district", id("district"))}
            onChange={(e) => setForm((f) => ({ ...f, district: e.target.value, upazila: "", mouza: "" }))}>
            <option value="">{t("common.select")}</option>
            {locations.districts.map((d) => <option key={d.id} value={d.id}>{label(d)}</option>)}
          </select>
        </Field>
        <Field id={id("upazila")} label={t("pages.check.upazila")} error={fe("upazila")}>
          <select id={id("upazila")} className={control} value={form.upazila} disabled={!district} {...a11y("upazila", id("upazila"))}
            onChange={(e) => setForm((f) => ({ ...f, upazila: e.target.value, mouza: "" }))}>
            <option value="">{t("common.select")}</option>
            {district?.upazilas.map((u) => <option key={u.id} value={u.id}>{label(u)}</option>)}
          </select>
        </Field>
        <Field id={id("mouza")} label={t("pages.check.mouza")} error={fe("mouza")}>
          <select id={id("mouza")} className={control} value={form.mouza} disabled={!upazila} {...a11y("mouza", id("mouza"))}
            onChange={(e) => set("mouza", e.target.value)}>
            <option value="">{t("common.select")}</option>
            {upazila?.mouzas.map((m) => <option key={m.id} value={m.id}>{t("pages.check.mouzaOption", { name: label(m), jl: m.jl_no })}</option>)}
          </select>
        </Field>
        <Field id={id("survey")} label={t("pages.check.survey")} optional>
          <select id={id("survey")} className={control} value={form.survey} onChange={(e) => set("survey", e.target.value)}>
            <option value="">{t("pages.check.surveyUnknown")}</option>
            {SURVEYS.map((s) => <option key={s} value={s}>{t(`survey.${s}`)}</option>)}
          </select>
        </Field>
        <Field id={id("khatian")} label={t("pages.check.khatian")} error={fe("khatian")}>
          <input id={id("khatian")} className={control} value={form.khatian} autoComplete="off" inputMode="numeric" {...a11y("khatian", id("khatian"))}
            onChange={(e) => set("khatian", e.target.value)} />
        </Field>
        <Field id={id("dag")} label={t("pages.check.dag")} error={fe("dag")}>
          <input id={id("dag")} className={control} value={form.dag} autoComplete="off" inputMode="numeric" {...a11y("dag", id("dag"))}
            onChange={(e) => set("dag", e.target.value)} />
        </Field>
      </fieldset>

      <fieldset className="card mt-5 p-4 sm:p-6">
        <legend className="heading-accent float-left mb-1 w-full text-xl font-bold text-brand-900">{t("pages.check.sellerTitle")}</legend>
        <div className="clear-both" />
        <Field id={id("name")} label={t("pages.check.sellerName")} error={fe("name")}>
          <input id={id("name")} className={control} value={form.name} autoComplete="off" {...a11y("name", id("name"))} onChange={(e) => set("name", e.target.value)} />
        </Field>
        <Field id={id("father")} label={t("pages.check.father")} help={t("pages.check.fatherHelp")} optional>
          <input id={id("father")} className={control} value={form.father} autoComplete="off" aria-describedby={`${id("father")}-help`} onChange={(e) => set("father", e.target.value)} />
        </Field>
        <div className="mt-5 flex items-start gap-3 rounded-xl bg-brand-50/70 p-3 transition-colors hover:bg-brand-50">
          <input id={id("bank")} type="checkbox" className="check mt-0.5" checked={form.bank} aria-describedby={`${id("bank")}-help`} onChange={(e) => set("bank", e.target.checked)} />
          <div>
            <label htmlFor={id("bank")} className="cursor-pointer font-bold text-brand-900">{t("pages.check.consentBank")}</label>
            <p id={`${id("bank")}-help`} className="text-sm text-slate-600">{t("pages.check.consentHelp")}</p>
          </div>
        </div>
      </fieldset>

      <button type="submit" className="btn-primary mt-6 w-full py-3.5">{t("pages.check.submit")}</button>
    </form>
  );
}
