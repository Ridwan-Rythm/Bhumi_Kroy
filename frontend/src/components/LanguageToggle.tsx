import { useTranslation } from "react-i18next";
import { toggleLanguage } from "../i18n";

// The visible text is the accessible name (WCAG 2.5.3 Label in Name): "English" or "বাংলা", the language you
// get by pressing it. `lang` makes a screen reader pronounce that word in its own language.
export default function LanguageToggle() {
  const { t, i18n } = useTranslation();
  const target = i18n.language === "bn" ? "en" : "bn";
  return (
    <button
      type="button"
      onClick={toggleLanguage}
      lang={target}
      className="min-h-tap min-w-tap rounded border border-gray-400 px-3 text-base font-medium"
    >
      {t("language.switch")}
    </button>
  );
}
