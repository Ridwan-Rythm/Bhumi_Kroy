import nacl from "tweetnacl";

function fromB64u(s: string): Uint8Array {
  const bin = atob(s.replace(/-/g, "+").replace(/_/g, "/") + "=".repeat((4 - (s.length % 4)) % 4));
  return Uint8Array.from(bin, (c) => c.charCodeAt(0));
}

// Checks the Ed25519 signature in the browser, so the person does not have to trust the server's "valid".
// Returns null when the inputs are not decodable.
export function verifySignatureLocally(payloadB64: string, signatureB64: string, publicKeyB64: string): boolean | null {
  try {
    return nacl.sign.detached.verify(fromB64u(payloadB64), fromB64u(signatureB64), fromB64u(publicKeyB64));
  } catch {
    return null;
  }
}

// Verification links carry the payload in the #fragment so it never reaches a server log:  /verify#<payload>.<signature>
export function parseVerifyFragment(hash: string): { payload_b64: string; signature_b64: string } | null {
  const m = hash.replace(/^#/, "").match(/^([A-Za-z0-9_-]+)\.([A-Za-z0-9_-]+)$/);
  return m ? { payload_b64: m[1], signature_b64: m[2] } : null;
}

// Contract section 7: QR text is `${origin}/verify#${signed_payload_b64}.${signature_b64}`, built here, never by the backend.
export function verifyUrl(origin: string, payloadB64: string, signatureB64: string): string {
  return `${origin}/verify#${payloadB64}.${signatureB64}`;
}
