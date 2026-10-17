import { Link, Outlet } from "react-router-dom";
import { useTranslation } from "react-i18next";
import LanguageToggle from "./LanguageToggle";

// Mobile-first shell (designed for 360px): header, content, footer with disclaimer + watermark strip.
export default function Layout() {
  const { t } = useTranslation();
  return (
    <div className="mx-auto flex min-h-screen w-full max-w-3xl flex-col">
      <a
        href="#main"
        className="sr-only focus:not-sr-only focus:absolute focus:left-2 focus:top-2 focus:bg-white focus:p-2"
      >
        {t("layout.skipToContent")}
      </a>
      <header className="flex items-center justify-between gap-2 border-b border-gray-200 px-4 py-2">
        <Link
          to="/"
          aria-label={t("layout.home")}
          className="inline-flex min-h-tap items-center text-xl font-bold"
        >
          {t("app.name")}
        </Link>
        <LanguageToggle />
      </header>

      <main id="main" className="flex-1 px-4 py-4">
        <Outlet />
      </main>

      <footer className="border-t border-gray-200 text-sm print:hidden">
        <p className="px-4 py-3 text-gray-700">{t("footer.disclaimer")}</p>
        <div
          role="note"
          className="bg-gray-900 px-4 py-2 text-center text-sm font-bold tracking-wide text-white"
        >
          {t("footer.watermark")}
        </div>
      </footer>
    </div>
  );
}
