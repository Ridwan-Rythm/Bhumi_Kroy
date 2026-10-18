// Validates every src/mocks/report_*.json against ../contracts/report.schema.json.
// Prints a clear skip message (exit 0) if the schema file is missing (it lands at S0).
import { existsSync, readdirSync, readFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import Ajv from "ajv";
import Ajv2020 from "ajv/dist/2020.js";
import addFormats from "ajv-formats";

const here = dirname(fileURLToPath(import.meta.url));
const schemaPath = resolve(here, "../../contracts/report.schema.json");
const mocksDir = resolve(here, "../src/mocks");

if (!existsSync(schemaPath)) {
  console.log(`check:contract SKIPPED: ${schemaPath} not found yet (Ridwan adds it at S0).`);
  process.exit(0);
}

const schema = JSON.parse(readFileSync(schemaPath, "utf8"));
const AjvClass = String(schema.$schema ?? "").includes("draft-07") ? Ajv : Ajv2020;
const ajv = new AjvClass({ allErrors: true, strict: false });
addFormats(ajv);
const validate = ajv.compile(schema);

const files = readdirSync(mocksDir).filter((f) => /^report_.*\.json$/.test(f));
if (files.length === 0) {
  console.log("check:contract SKIPPED: no src/mocks/report_*.json fixtures yet (added in B1.1).");
  process.exit(0);
}

let failed = 0;
for (const f of files) {
  const data = JSON.parse(readFileSync(join(mocksDir, f), "utf8"));
  if (validate(data)) {
    console.log(`ok    ${f}`);
  } else {
    failed++;
    console.log(`FAIL  ${f}`);
    for (const err of validate.errors ?? []) console.log(`        ${err.instancePath || "/"} ${err.message}`);
  }
}
process.exit(failed ? 1 : 0);
