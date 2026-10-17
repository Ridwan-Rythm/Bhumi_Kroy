import { useTranslation } from "react-i18next";
import { toggleLanguage } from "../i18n";

export default function LanguageToggle() {
  const { t } = useTranslation();
  return (
    <button
      type="button"
      onClick={toggleLanguage}
      aria-label={t("language.switchLabel")}
      className="min-h-tap min-w-tap rounded border border-gray-400 px-3 text-base font-medium"
    >
      {t("language.switch")}
    </button>
  );
}
