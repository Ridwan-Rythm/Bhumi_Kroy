import { Link, Outlet } from "react-router-dom";
import { useTranslation } from "react-i18next";
import LanguageToggle from "./LanguageToggle";

// Mobile-first shell (designed for 360px): header, content, footer with disclaimer + watermark strip.
// The footer is part of the printed report on purpose: the contract requires the disclaimer and the
// SYNTHETIC watermark on the printable report, so it must NOT be hidden with print:hidden.
export default function Layout() {
  const { t } = useTranslation();
  return (
    <div className="mx-auto flex min-h-screen w-full max-w-3xl flex-col">
      <a
        href="#main"
        className="sr-only focus:not-sr-only focus:absolute focus:left-2 focus:top-2 focus:z-50 focus:bg-white focus:p-2"
      >
        {t("layout.skipToContent")}
      </a>
      <header className="flex items-center justify-between gap-2 border-b border-gray-200 px-4 py-2 print:hidden">
        <Link to="/" className="inline-flex min-h-tap items-center text-xl font-bold">
          {t("app.name")}
        </Link>
        <nav className="flex items-center gap-2">
          <Link to="/verify" className="inline-flex min-h-tap items-center px-2 underline">
            {t("layout.verifyLink")}
          </Link>
          <LanguageToggle />
        </nav>
      </header>

      {/* tabIndex=-1: lets the skip link move keyboard focus here, not just scroll */}
      <main id="main" tabIndex={-1} className="flex-1 px-4 py-4 focus:outline-none">
        <Outlet />
      </main>

      <footer className="border-t border-gray-200 text-sm">
        <p className="px-4 py-3 text-gray-700">{t("footer.disclaimer")}</p>
        <div
          role="note"
          className="bg-gray-900 px-4 py-2 text-center text-sm font-bold tracking-wide text-white print:border-2 print:border-gray-900 print:bg-white print:text-gray-900"
        >
          {t("footer.watermark")}
        </div>
      </footer>
    </div>
  );
}
