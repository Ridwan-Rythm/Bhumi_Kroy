import { readdirSync, readFileSync, statSync } from "node:fs";
import { join, relative, sep } from "node:path";
import { scanSource } from "./scan-text";

// Rule 4: ALL user-visible text comes from i18n keys.
//  - .tsx: JSX text, {"literal"}, {`template`}, {cond ? "a" : "b"} and visible attributes written as literals.
//  - .ts (logic files): sentence-like string literals. Developer-only messages carry `// i18n-ignore: reason`.
const SRC = join(__dirname, "..");
const SKIP_TS_DIRS = new Set(["test", "i18n", "mocks", "types"]);

function files(dir: string, ext: ".ts" | ".tsx"): string[] {
  return readdirSync(dir).flatMap((name) => {
    const p = join(dir, name);
    if (statSync(p).isDirectory()) return name === "test" && ext === ".tsx" ? [] : files(p, ext);
    return p.endsWith(ext) && !p.endsWith(".d.ts") ? [p] : [];
  });
}

describe("no hard-coded user-visible text", () => {
  it("every .tsx file uses i18n keys only", () => {
    const all = files(SRC, ".tsx").flatMap((f) => scanSource(relative(SRC, f), readFileSync(f, "utf8"), "tsx"));
    expect(all).toEqual([]);
  });

  it("logic .ts files contain no sentence-like literals", () => {
    const all = files(SRC, ".ts")
      .filter((f) => !relative(SRC, f).split(sep).some((part) => SKIP_TS_DIRS.has(part)))
      .flatMap((f) => scanSource(relative(SRC, f), readFileSync(f, "utf8"), "ts"));
    expect(all).toEqual([]);
  });
});

describe("the scanner itself", () => {
  const tsx = (body: string) => scanSource("x.tsx", `const A = () => (${body});`, "tsx");

  it("catches text nodes, literal expressions, templates, ternaries and visible attributes", () => {
    expect(tsx("<p>Hello</p>")).toHaveLength(1);
    expect(tsx('<p>{"Hello"}</p>')).toHaveLength(1);
    expect(tsx("<p>{`Hi ${name}`}</p>")).toHaveLength(1);
    expect(tsx('<p>{ok ? "Yes" : "No"}</p>')).toHaveLength(2);
    expect(tsx('<img alt="a photo" />')).toHaveLength(1);
    expect(tsx('<img alt={"a photo"} />')).toHaveLength(1);
    expect(tsx('<button aria-label="Close" />')).toHaveLength(1);
    expect(tsx('<input aria-roledescription="Slider" />')).toHaveLength(1);
    expect(tsx('<input summary={ok ? "a" : "b"} />')).toHaveLength(2);
  });

  it("allows i18n calls, comparisons, punctuation and non-visible attributes", () => {
    expect(tsx('<p>{t("a.b")}</p>')).toEqual([]);
    expect(tsx('<p>{ok ? t("a") : t("b")}</p>')).toEqual([]);
    expect(tsx('<p>{" · "}</p>')).toEqual([]);
    expect(tsx('<p>{x === "a" && <b>{t("k")}</b>}</p>')).toEqual([]);
    expect(tsx('<p>{items.map((i) => <li key={i}>{t(i)}</li>)}</p>')).toEqual([]);
    expect(tsx('<p className="mt-2" data-x="abc def">{t(`k.${id}`)}</p>')).toEqual([]);
    expect(tsx('<p>{map["a b"]}</p>')).toEqual([]);
  });

  it("flags sentence-like strings in .ts files unless marked i18n-ignore", () => {
    expect(scanSource("a.ts", 'const m = "Something went wrong";', "ts")).toHaveLength(1);
    expect(scanSource("a.ts", 'const m = "NETWORK"; const n = "Content-Type";', "ts")).toEqual([]);
    expect(scanSource("a.ts", 'throw new Error("Not JSON"); // i18n-ignore: developer message', "ts")).toEqual([]);
    expect(scanSource("a.ts", 'import x from "a b";', "ts")).toEqual([]);
  });
});
