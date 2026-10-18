// Regenerates src/i18n/REVIEW.md from bn.json. Keeps the Status of keys whose Bangla text did not change.
//   npm run gen:review
import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const dir = join(here, "..", "src", "i18n");
const bn = JSON.parse(readFileSync(join(dir, "bn.json"), "utf8"));
const file = join(dir, "REVIEW.md");

const leaves = (o, p = "") =>
  typeof o === "string" ? [[p, o]] : Object.entries(o).flatMap(([k, v]) => leaves(v, p ? `${p}.${k}` : k));

const prev = new Map();
if (existsSync(file)) {
  for (const line of readFileSync(file, "utf8").split("\n")) {
    const m = line.match(/^\| `([^`]+)` \| (.*) \| ([^|]+) \|$/);
    if (m) prev.set(m[1], { text: m[2], status: m[3].trim() });
  }
}

const rows = leaves(bn).map(([k, v]) => {
  const old = prev.get(k);
  const status = old && old.text === v.replace(/\|/g, "\\|") ? old.status : "needs native review";
  return `| \`${k}\` | ${v.replace(/\|/g, "\\|")} | ${status} |`;
});

writeFileSync(
  file,
  `# Bangla strings: needs native review

Every Bangla string in \`bn.json\` is listed here (workflow rule 7). Read this file aloud and fix awkward wording.
A test (\`src/test/i18n.test.ts\`) fails if a key is in \`bn.json\` but missing from this table.
Status column: change to \`reviewed\` once a native speaker has read it. Regenerate with \`npm run gen:review\`
(a changed string goes back to "needs native review").

Points to look at first: the watermark and disclaimer, the six verdict summaries, all \`rules.*\` text, the product
name in \`app.name\`, and anything that uses legal words (khas, vested, namjari, mutation).

| Key | Bangla | Status |
|---|---|---|
${rows.join("\n")}
`,
);
console.log(`wrote ${rows.length} rows`);
