import { Link, Outlet, useLocation } from "react-router-dom";
import { useTranslation } from "react-i18next";
import LanguageToggle from "./LanguageToggle";

// Mobile-first shell (designed for 360px): header, content, footer with disclaimer + watermark strip.
// The footer is part of the printed report on purpose: the contract requires the disclaimer and the
// SYNTHETIC watermark on the printable report, so it must NOT be hidden with print:hidden.
function LogoMark() {
  return (
    <svg aria-hidden="true" viewBox="0 0 40 40" className="h-9 w-9 shrink-0 transition-transform duration-500 group-hover:rotate-[360deg]">
      <defs>
        <linearGradient id="bk-g" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#45b97b" />
          <stop offset="1" stopColor="#0d412c" />
        </linearGradient>
      </defs>
      <rect width="40" height="40" rx="11" fill="url(#bk-g)" />
      <path d="M8 27 20 11l12 16z" fill="none" stroke="#fbd97a" strokeWidth="2.4" strokeLinejoin="round" />
      <path d="M13 27h14M20 11v16" stroke="#fff" strokeWidth="2" strokeLinecap="round" opacity=".9" />
    </svg>
  );
}

export default function Layout() {
  const { t } = useTranslation();
  const { pathname } = useLocation();
  return (
    <div className="relative flex min-h-screen w-full flex-col overflow-x-clip">
      {/* soft animated backdrop, decorative only */}
      <div aria-hidden="true" className="print-hide-decor pointer-events-none absolute inset-0 -z-0 overflow-hidden">
        <div className="blob -left-24 top-40 h-72 w-72 bg-brand-300/30" />
        <div className="blob -right-24 top-[28rem] h-80 w-80 bg-gold-300/25 [animation-delay:-6s]" />
      </div>

      <a
        href="#main"
        className="sr-only focus:not-sr-only focus:absolute focus:left-2 focus:top-2 focus:z-50 focus:rounded-lg focus:bg-white focus:p-2 focus:shadow-lift"
      >
        {t("layout.skipToContent")}
      </a>
      <header className="sticky top-0 z-40 border-b border-brand-100/80 bg-white/75 backdrop-blur-xl print:hidden">
        <div className="mx-auto flex w-full max-w-4xl items-center justify-between gap-2 px-4 py-2">
          <Link to="/" className="group inline-flex min-h-tap items-center gap-2.5 rounded-lg text-xl font-bold text-brand-900">
            <LogoMark />
            <span className="gradient-text">{t("app.name")}</span>
          </Link>
          <nav className="flex items-center gap-1 sm:gap-2">
            <Link to="/verify" className="nav-link">
              {t("layout.verifyLink")}
            </Link>
            <LanguageToggle />
          </nav>
        </div>
      </header>

      {/* tabIndex=-1: lets the skip link move keyboard focus here, not just scroll */}
      <main id="main" tabIndex={-1} className="relative z-10 mx-auto w-full max-w-4xl flex-1 px-4 py-6 focus:outline-none sm:py-8">
        <div key={pathname} className="page-enter">
          <Outlet />
        </div>
      </main>

      <footer className="relative z-10 mt-8 border-t border-brand-100 bg-white/70 text-sm backdrop-blur">
        <p className="mx-auto max-w-4xl px-4 py-4 text-slate-700">{t("footer.disclaimer")}</p>
        <div
          role="note"
          className="bg-gradient-to-r from-brand-950 via-brand-800 to-brand-950 px-4 py-2.5 text-center text-sm font-bold tracking-wide text-gold-300 print:border-2 print:border-gray-900 print:bg-white print:bg-none print:text-gray-900"
        >
          {t("footer.watermark")}
        </div>
      </footer>
    </div>
  );
}
