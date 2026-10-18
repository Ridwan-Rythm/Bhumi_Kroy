import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import en from "./en.json";
import bn from "./bn.json";

export type Lang = "bn" | "en";
const STORAGE_KEY = "landcheck.lang";

function readStoredLang(): Lang {
  try {
    const v = window.localStorage.getItem(STORAGE_KEY);
    if (v === "en" || v === "bn") return v;
  } catch {
    // storage can be blocked; fall through to the default
  }
  return "bn"; // Bangla is the default language
}

function storeLang(lang: Lang) {
  try {
    window.localStorage.setItem(STORAGE_KEY, lang);
  } catch {
    // ignore: the toggle still works for this session
  }
}

// <html lang> and <title> follow the active language (screen readers and browser tabs).
function syncHtmlLang(lang: string) {
  document.documentElement.lang = lang;
  document.title = i18n.t("app.title");
}

void i18n.use(initReactI18next).init({
  resources: { bn: { translation: bn }, en: { translation: en } },
  lng: readStoredLang(),
  fallbackLng: "en",
  interpolation: { escapeValue: false }, // React escapes
});

syncHtmlLang(i18n.language);
i18n.on("languageChanged", (lng) => {
  syncHtmlLang(lng);
  if (lng === "en" || lng === "bn") storeLang(lng);
});

export function toggleLanguage() {
  void i18n.changeLanguage(i18n.language === "bn" ? "en" : "bn");
}

export default i18n;
