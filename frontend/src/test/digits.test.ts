import { toAsciiDigits, toBanglaDigits } from "../lib/digits";

describe("digit helpers", () => {
  it("converts Bangla digits to ASCII", () => {
    expect(toAsciiDigits("১২৩৪৫৬৭৮৯০")).toBe("1234567890");
  });
  it("leaves ASCII digits and other text alone", () => {
    expect(toAsciiDigits("খতিয়ান 123/ক")).toBe("খতিয়ান 123/ক");
  });
  it("handles mixed input", () => {
    expect(toAsciiDigits("১2৩")).toBe("123");
  });
  it("converts ASCII to Bangla digits and back", () => {
    expect(toBanglaDigits("2026")).toBe("২০২৬");
    expect(toAsciiDigits(toBanglaDigits("0123456789"))).toBe("0123456789");
  });
});
