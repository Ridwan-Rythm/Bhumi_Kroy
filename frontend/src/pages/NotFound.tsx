import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";

export default function NotFound() {
  const { t } = useTranslation();
  return (
    <section>
      <h1 className="text-2xl font-bold">{t("pages.notFound.title")}</h1>
      <p className="mt-2">{t("pages.notFound.body")}</p>
      <p className="mt-4"><Link to="/" className="inline-flex min-h-tap items-center underline">{t("pages.notFound.home")}</Link></p>
    </section>
  );
}
