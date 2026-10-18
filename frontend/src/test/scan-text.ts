import ts from "typescript";

// Finds user-visible text that is written as a literal instead of coming from an i18n key (rule 4).
// Used by no-hardcoded-text.test.ts, which also tests the scanner itself on small snippets.
export const VISIBLE_ATTRS = new Set([
  "aria-label", "aria-description", "aria-placeholder", "aria-roledescription", "aria-valuetext",
  "alt", "title", "placeholder", "label", "summary",
]);

const HAS_LETTER = /\p{L}/u;
const TWO_WORDS = /\p{L}+\s+\p{L}+/u;
// "border-red-700 bg-red-50": a class list, not a sentence (every word has a -, : / or [ in it).
const isClassList = (text: string) => text.trim().split(/\s+/).every((tok) => /[-:/[]/.test(tok));
const COMPARISONS = new Set([
  ts.SyntaxKind.EqualsEqualsToken, ts.SyntaxKind.EqualsEqualsEqualsToken,
  ts.SyntaxKind.ExclamationEqualsToken, ts.SyntaxKind.ExclamationEqualsEqualsToken,
]);

// Literals that could end up on screen inside a JSX expression. Arguments of calls (t("key"), x.includes("a"))
// and operands of comparisons (x === "a") are not displayed, so they are skipped.
function visibleLiterals(node: ts.Node, out: ts.Node[]): void {
  // Nested JSX is scanned by the main visitor; its attributes (className...) are not display text.
  if (ts.isCallExpression(node) || ts.isObjectLiteralExpression(node) || ts.isJsxElement(node) || ts.isJsxSelfClosingElement(node) || ts.isJsxFragment(node)) return;
  if (ts.isBinaryExpression(node) && COMPARISONS.has(node.operatorToken.kind)) return;
  if (ts.isElementAccessExpression(node)) return visibleLiterals(node.expression, out);
  if ((ts.isStringLiteral(node) || ts.isNoSubstitutionTemplateLiteral(node)) && HAS_LETTER.test(node.text)) {
    out.push(node);
    return;
  }
  if (ts.isTemplateExpression(node)) {
    const parts = [node.head.text, ...node.templateSpans.map((s) => s.literal.text)];
    if (parts.some((p) => HAS_LETTER.test(p))) out.push(node);
  }
  ts.forEachChild(node, (c) => visibleLiterals(c, out));
}

export function scanSource(file: string, source: string, kind: "tsx" | "ts"): string[] {
  const sf = ts.createSourceFile(file, source, ts.ScriptTarget.Latest, true, kind === "tsx" ? ts.ScriptKind.TSX : ts.ScriptKind.TS);
  const lines = source.split("\n");
  const found: string[] = [];
  const ignored = (n: ts.Node) => lines[sf.getLineAndCharacterOfPosition(n.getStart(sf)).line]?.includes("i18n-ignore");
  const report = (n: ts.Node, what: string) => { if (!ignored(n)) found.push(`${what} (line ${sf.getLineAndCharacterOfPosition(n.getStart(sf)).line + 1})`); };

  const visit = (node: ts.Node) => {
    if (kind === "tsx") {
      if (ts.isJsxText(node) && HAS_LETTER.test(node.text)) report(node, `text node "${node.text.trim()}"`);
      if (ts.isJsxAttribute(node) && VISIBLE_ATTRS.has(node.name.getText(sf)) && node.initializer) {
        const name = node.name.getText(sf);
        if (ts.isStringLiteral(node.initializer)) report(node, `${name}="${node.initializer.text}"`);
        else if (ts.isJsxExpression(node.initializer) && node.initializer.expression) {
          const lits: ts.Node[] = [];
          visibleLiterals(node.initializer.expression, lits);
          for (const l of lits) report(l, `${name}={${l.getText(sf)}}`);
        }
      }
      if (ts.isJsxExpression(node) && node.expression && (ts.isJsxElement(node.parent) || ts.isJsxFragment(node.parent))) {
        const lits: ts.Node[] = [];
        visibleLiterals(node.expression, lits);
        for (const l of lits) report(l, `expression ${l.getText(sf)}`);
      }
    } else if (
      (ts.isStringLiteral(node) || ts.isNoSubstitutionTemplateLiteral(node)) &&
      TWO_WORDS.test(node.text) &&
      !isClassList(node.text) &&
      !ts.isImportDeclaration(node.parent) && !ts.isExportDeclaration(node.parent)
    ) {
      report(node, `sentence-like string "${node.text}"`);
    }
    ts.forEachChild(node, visit);
  };
  visit(sf);
  return found.map((f) => `${file}: ${f}`);
}
