import type { ReactNode } from "react";
import { useTranslation } from "react-i18next";
import { ApiError } from "../api/errors";
import { isMockMode } from "../api/client";

export function Spinner() {
  const { t } = useTranslation();
  return (
    <p role="status" className="flex items-center gap-2 text-gray-700">
      <span aria-hidden="true" className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-gray-400 border-t-transparent" />
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
    <div role="alert" className="rounded border-2 border-red-700 bg-red-50 p-3 text-red-900">
      {title ? <p className="font-bold">{title}</p> : null}
      <p>{errorMessage(t, error)}</p>
      {onRetry ? (
        <button type="button" onClick={onRetry} className="mt-2 min-h-tap rounded border border-red-900 px-3 font-medium">
          {t("common.retry")}
        </button>
      ) : null}
    </div>
  );
}

export function MockBanner() {
  const { t } = useTranslation();
  if (!isMockMode()) return null;
  return <p className="mb-3 rounded bg-yellow-100 px-3 py-2 text-sm text-yellow-900">{t("common.mockBanner")}</p>;
}

export function Section({ title, children, id }: { title: string; children: ReactNode; id?: string }) {
  return (
    <section aria-labelledby={id} className="mt-6 break-inside-avoid">
      <h2 id={id} className="mb-2 text-xl font-bold">
        {title}
      </h2>
      {children}
    </section>
  );
}
