import { readFileSync } from "node:fs";
import { join } from "node:path";
import en from "../i18n/en.json";
import bn from "../i18n/bn.json";

function leaves(obj: unknown, prefix = ""): Record<string, string> {
  if (typeof obj === "string") return { [prefix]: obj };
  return Object.entries(obj as Record<string, unknown>).reduce<Record<string, string>>(
    (acc, [k, v]) => ({ ...acc, ...leaves(v, prefix ? `${prefix}.${k}` : k) }),
    {},
  );
}

const enLeaves = leaves(en);
const bnLeaves = leaves(bn);

describe("i18n catalogues", () => {
  it("en and bn have exactly the same keys", () => {
    expect(Object.keys(bnLeaves).sort()).toEqual(Object.keys(enLeaves).sort());
  });

  it("no empty strings", () => {
    for (const v of [...Object.values(enLeaves), ...Object.values(bnLeaves)]) {
      expect(v.trim()).not.toBe("");
    }
  });

  // Rule 5: never "safe", "clean title" or "guaranteed" (English). Bangla equivalents are
  // audited by hand in B4 because a word list cannot catch every phrasing.
  it("English copy never says safe / clean title / guaranteed", () => {
    for (const v of Object.values(enLeaves)) {
      expect(v).not.toMatch(/\bsafe(ly|ty)?\b/i);
      expect(v).not.toMatch(/clean title/i);
      expect(v).not.toMatch(/guaranteed/i);
    }
  });

  // Rule 7: every Bangla string is listed in REVIEW.md.
  it("every Bangla key is listed in REVIEW.md", () => {
    const review = readFileSync(join(__dirname, "../i18n/REVIEW.md"), "utf8");
    const missing = Object.keys(bnLeaves).filter((k) => !review.includes("`" + k + "`"));
    expect(missing).toEqual([]);
  });
});
