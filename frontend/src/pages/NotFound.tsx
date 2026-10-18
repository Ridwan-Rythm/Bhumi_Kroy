import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";

export default function NotFound() {
  const { t } = useTranslation();
  return (
    <section className="card mx-auto mt-6 max-w-xl p-8 text-center">
      <div aria-hidden="true" className="mx-auto mb-4 flex h-16 w-16 animate-float items-center justify-center rounded-full bg-gradient-to-br from-brand-100 to-gold-300/50 text-3xl shadow-soft">?</div>
      <h1 className="gradient-text text-3xl font-bold">{t("pages.notFound.title")}</h1>
      <p className="mt-2 text-slate-700">{t("pages.notFound.body")}</p>
      <p className="mt-6"><Link to="/" className="btn-primary">{t("pages.notFound.home")}</Link></p>
    </section>
  );
}
