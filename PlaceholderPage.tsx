import { useTranslation } from "react-i18next";

// Used by every route until its real screen is built (B1.2, B1.3, B3).
export default function PlaceholderPage({ titleKey }: { titleKey: string }) {
  const { t } = useTranslation();
  return (
    <section>
      <h1 className="text-2xl font-bold">{t(titleKey)}</h1>
      <p className="mt-2 text-base text-gray-700">{t("common.placeholder")}</p>
    </section>
  );
}
