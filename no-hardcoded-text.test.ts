import { readdirSync, readFileSync, statSync } from "node:fs";
import { join } from "node:path";
import ts from "typescript";

// Rule 4: ALL user-visible text comes from i18n keys. This test fails if any .tsx file
// contains a JSX text node or a user-visible string attribute written as a literal.
const SRC = join(__dirname, "..");
const VISIBLE_ATTRS = new Set(["aria-label", "alt", "title", "placeholder", "label", "aria-description"]);

function tsxFiles(dir: string): string[] {
  return readdirSync(dir).flatMap((name) => {
    const p = join(dir, name);
    if (statSync(p).isDirectory()) return tsxFiles(p);
    return p.endsWith(".tsx") ? [p] : [];
  });
}

function offenders(file: string): string[] {
  const sf = ts.createSourceFile(file, readFileSync(file, "utf8"), ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX);
  const found: string[] = [];
  const visit = (node: ts.Node) => {
    if (ts.isJsxText(node) && node.text.trim() !== "") {
      found.push(`text node "${node.text.trim()}"`);
    }
    if (
      ts.isJsxAttribute(node) &&
      VISIBLE_ATTRS.has(node.name.getText(sf)) &&
      node.initializer &&
      ts.isStringLiteral(node.initializer)
    ) {
      found.push(`${node.name.getText(sf)}="${node.initializer.text}"`);
    }
    ts.forEachChild(node, visit);
  };
  visit(sf);
  return found.map((f) => `${file}: ${f}`);
}

describe("no hard-coded user-visible text in .tsx files", () => {
  it("every .tsx file uses i18n keys only", () => {
    const all = tsxFiles(SRC).flatMap(offenders);
    expect(all).toEqual([]);
  });
});
