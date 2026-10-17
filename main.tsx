import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
// Self-hosted Noto Sans Bengali (bundled from the npm package; no external font requests).
import "@fontsource/noto-sans-bengali/bengali-400.css";
import "@fontsource/noto-sans-bengali/bengali-700.css";
import "@fontsource/noto-sans-bengali/latin-400.css";
import "@fontsource/noto-sans-bengali/latin-700.css";
import "./index.css";
import "./i18n";
import App from "./App";

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>,
);
