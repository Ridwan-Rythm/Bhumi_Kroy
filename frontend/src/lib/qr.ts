import QRCode from "qrcode";

export const qrDataUrl = (text: string): Promise<string> =>
  QRCode.toDataURL(text, { errorCorrectionLevel: "M", margin: 1, width: 240 });
