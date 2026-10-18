// Contract section 5: numeric strings may use Bangla (U+09E6..U+09EF) or ASCII digits.
// The backend stores ASCII; the UI normalises on input so users see consistent values.
const BN_ZERO = 0x09e6;

export function toAsciiDigits(input: string): string {
  return input.replace(/[\u09E6-\u09EF]/g, (ch) => String(ch.charCodeAt(0) - BN_ZERO));
}

export function toBanglaDigits(input: string): string {
  return input.replace(/[0-9]/g, (ch) => String.fromCharCode(BN_ZERO + Number(ch)));
}
