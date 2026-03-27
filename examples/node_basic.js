/**
 * AgentTax — Basic Node.js Integration
 * Calculate sales tax for an AI agent transaction.
 */

const API_KEY = "atx_live_your_key"; // or omit for demo mode
const BASE_URL = "https://agenttax.io";

async function calculateTax({ role, amount, buyer_state, transaction_type, counterparty_id, buyer_zip, work_type, is_b2b }) {
  const headers = { "Content-Type": "application/json" };
  if (API_KEY !== "atx_live_your_key") headers["X-API-Key"] = API_KEY;

  const body = { role, amount, buyer_state, transaction_type, counterparty_id };
  if (buyer_zip) body.buyer_zip = buyer_zip;
  if (work_type) body.work_type = work_type;
  if (is_b2b) body.is_b2b = true;

  const resp = await fetch(`${BASE_URL}/api/v1/calculate`, {
    method: "POST",
    headers,
    body: JSON.stringify(body),
  });
  return resp.json();
}

async function logTrade({ trade_type, asset_symbol, quantity, price_per_unit, resident_state }) {
  const body = { trade_type, asset_symbol, quantity, price_per_unit };
  if (resident_state) body.resident_state = resident_state;
  const resp = await fetch(`${BASE_URL}/api/v1/trades`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-API-Key": API_KEY },
    body: JSON.stringify(body),
  });
  return resp.json();
}

// Example: seller in Texas
const result = await calculateTax({
  role: "seller",
  amount: 2500,
  buyer_state: "TX",
  buyer_zip: "75201",
  transaction_type: "saas",
  work_type: "content",
  counterparty_id: "buyer-agent-99",
});

console.log(`Tax: $${result.total_tax}`);
console.log(`Rate: ${(result.combined_rate * 100).toFixed(2)}%`);
console.log(`Confidence: ${result.confidence.level}`);
