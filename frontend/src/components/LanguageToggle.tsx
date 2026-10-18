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
      className="min-h-tap min-w-tap rounded-full border border-brand-300 bg-white px-4 text-base font-medium text-brand-800 shadow-sm transition-all duration-200 hover:-translate-y-0.5 hover:border-brand-600 hover:bg-brand-600 hover:text-white hover:shadow-glow active:translate-y-0 active:scale-95"
    >
      {t("language.switch")}
    </button>
  );
}
