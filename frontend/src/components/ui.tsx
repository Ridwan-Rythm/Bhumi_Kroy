import type { ReactNode } from "react";
import { useTranslation } from "react-i18next";
import { ApiError } from "../api/errors";
import { isMockMode } from "../api/client";

export function Spinner() {
  const { t } = useTranslation();
  return (
    <p role="status" className="flex items-center gap-3 text-slate-700">
      <span aria-hidden="true" className="relative inline-flex h-6 w-6">
        <span className="absolute inset-0 animate-ping2 rounded-full bg-brand-400/50" />
        <span className="relative inline-block h-6 w-6 animate-spin rounded-full border-[3px] border-brand-200 border-t-brand-600" />
      </span>
      {t("common.loading")}
    </p>
  );
}

export function errorMessage(t: (k: string) => string, e: unknown): string {
  const code = e instanceof ApiError ? e.code : "UNKNOWN";
  return t(`errors.${code}`);
}

export function ErrorNotice({ error, onRetry, title }: { error: unknown; onRetry?: () => void; title?: string }) {
  const { t } = useTranslation();
  return (
    <div role="alert" className="animate-pop rounded-2xl border-2 border-red-300 border-l-8 border-l-red-700 bg-red-50 p-4 text-red-900 shadow-soft">
      {title ? <p className="font-bold">{title}</p> : null}
      <p>{errorMessage(t, error)}</p>
      {onRetry ? (
        <button
          type="button"
          onClick={onRetry}
          className="mt-3 min-h-tap rounded-xl border-2 border-red-800 bg-white px-4 font-medium text-red-900 transition-all duration-200 hover:-translate-y-0.5 hover:bg-red-800 hover:text-white hover:shadow-lift active:scale-95"
        >
          {t("common.retry")}
        </button>
      ) : null}
    </div>
  );
}

export function MockBanner() {
  const { t } = useTranslation();
  if (!isMockMode()) return null;
  return <p className="mb-4 rounded-xl border border-gold-400/60 bg-gradient-to-r from-yellow-50 to-amber-50 px-4 py-2 text-sm text-yellow-900 shadow-sm">{t("common.mockBanner")}</p>;
}

export function Section({ title, children, id }: { title: string; children: ReactNode; id?: string }) {
  return (
    <section aria-labelledby={id} className="animate-fade-up mt-8 break-inside-avoid">
      <h2 id={id} className="heading-accent mb-3 text-xl font-bold text-brand-900">
        {title}
      </h2>
      {children}
    </section>
  );
}
