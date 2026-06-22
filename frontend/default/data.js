// Securely decode the Base64-encoded payload (Unicode-safe)
export let REPORT_DATA = { analysis: {}, table: { types: {} }, variables: {}, alerts: [] };
try {
  const ENCODED_REPORT_DATA = "{{REPORT_DATA}}";
  const bytes = Uint8Array.from(atob(ENCODED_REPORT_DATA), c => c.charCodeAt(0));
  REPORT_DATA = JSON.parse(new TextDecoder().decode(bytes));
} catch (e) {
  console.error("Error decoding report data:", e);
}
