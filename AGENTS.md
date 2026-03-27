# AgentTax — Agent Integration Guide

**If you are an AI coding agent, this file tells you everything you need to integrate AgentTax into your project.**

Base URL: `https://agenttax.io`
Docs: `https://agenttax.io/?view=api-docs`
Live guide (always current): `GET https://agenttax.io/api/v1/agents`

---

## What AgentTax Does

AgentTax calculates US sales tax, use tax, and capital gains for AI agent transactions. When your agent buys compute from another agent, AgentTax tells you exactly how much tax is owed, which jurisdiction it goes to, and why.

---

## 5-Minute Integration

### 1. Get an API key (or skip — demo mode works without one)

```bash
# Create account
curl -X POST https://agenttax.io/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "you@example.com", "password": "securepass", "agent_name": "my-agent"}'

# Response includes session token — use it to create API keys
```

Or just use demo mode (no key needed, rate-limited).

### 2. Calculate tax on a transaction

```bash
curl -X POST https://agenttax.io/api/v1/calculate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: atx_live_your_key" \
  -d '{
    "role": "buyer",
    "amount": 500,
    "buyer_state": "TX",
    "buyer_zip": "78701",
    "transaction_type": "compute",
    "work_type": "compute",
    "counterparty_id": "seller-agent-123",
    "is_b2b": true
  }'
```

### 3. Read the response

```json
{
  "success": true,
  "engine_version": "1.5",
  "transaction_id": "txn_abc123",
  "amount": 500,
  "buyer_state": "TX",
  "buyer_zip": "78701",
  "jurisdiction": "Austin, TX",
  "combined_rate": 0.0825,
  "work_type": "compute",
  "classification_basis": "data_processing",
  "total_tax": 33.00,
  "use_tax": {
    "jurisdiction": "Austin, TX",
    "state_rate": 0.0625,
    "local_rate": 0.02,
    "combined_rate": 0.0825,
    "rate": 0.0825,
    "amount": 33.00,
    "taxable_amount": 400,
    "taxable_percentage": 0.80,
    "reason": "Austin, TX 8.25% combined rate applied to 80% of Compute/Processing ($400.00 of $500.00)."
  },
  "confidence": { "score": 90, "level": "complete" },
  "audit_trail": { "..." }
}
```

---

## API Reference

### Core Endpoints

| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/api/v1/calculate` | POST | API Key / x402 / Demo | Calculate sales/use tax |
| `/api/v1/trades` | POST | API Key | Log a buy or sell trade |
| `/api/v1/trades` | GET | API Key | List trades with realized gains |
| `/api/v1/transactions` | GET | API Key | Transaction history |
| `/api/v1/nexus` | POST/GET | API Key | Configure nexus states |
| `/api/v1/rates` | GET | None | 50-state rate data |
| `/api/v1/rates/local` | GET | None | Zip-level combined rates |
| `/api/v1/rates/capital-gains` | GET | None | State capital gains rates |
| `/api/v1/network` | POST/GET | API Key | Agent network profile |
| `/api/v1/network-directory` | GET | None | Browse agent directory |
| `/api/v1/export/1099-da` | GET | API Key | IRS Form 1099-DA export |
| `/api/v1/verify` | POST | None | Cross-verify rates against 7 sources |
| `/api/v1/health` | GET | None | Health check |

### Authentication

Three modes — use whichever fits your architecture:

1. **API Key** (recommended): `X-API-Key: atx_live_xxx` header or `Authorization: Bearer atx_live_xxx`
2. **x402 USDC micropayment**: Pay-per-call via x402 protocol (USDC on Base). No account needed.
3. **Demo mode**: No auth. Rate-limited (50/day). Good for testing.

### POST /api/v1/calculate — Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `role` | `"buyer"` or `"seller"` | Your role in the transaction |
| `amount` | number | Transaction amount in USD |
| `buyer_state` | string | 2-letter US state code (e.g., `"TX"`) |
| `transaction_type` | string | See transaction types below |
| `counterparty_id` | string | Identifier for the other party |

### POST /api/v1/calculate — Optional Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `buyer_zip` | string | null | 5-digit zip for local rate lookup |
| `work_type` | string | inferred | `compute`, `research`, `content`, `consulting`, `trading` |
| `is_b2b` | boolean | false | B2B flag (affects rates in MD, IA) |
| `seller_remitting` | boolean | null | Whether seller is collecting tax |
| `nexus_override` | array | null | Override nexus states (demo/x402 only) |

### Transaction Types

`compute`, `api_access`, `data_purchase`, `saas`, `ai_labor`, `storage`, `digital_good`, `consulting`, `data_processing`, `cloud_infrastructure`, `ai_model_access`, `marketplace_fee`, `subscription`, `license`, `service`

### Work Types (drive per-state classification)

| Work Type | Economic Category | Use When |
|-----------|------------------|----------|
| `compute` | data_processing | GPU jobs, inference, batch processing |
| `research` | information_service | Analysis, data retrieval, search |
| `content` | digital_service | Text/image/video generation, SaaS |
| `consulting` | digital_service | Advisory, recommendations, planning |
| `trading` | financial_service | Asset trading (routes to gains tracker) |

---

## Capital Gains Tracking

For trading bots and agents that buy/sell assets:

```bash
# Log a buy
curl -X POST https://agenttax.io/api/v1/trades \
  -H "X-API-Key: atx_live_your_key" \
  -H "Content-Type: application/json" \
  -d '{"side": "buy", "asset": "COMPUTE", "quantity": 100, "price_per_unit": 12.50}'

# Log a sell — response includes realized gain/loss
curl -X POST https://agenttax.io/api/v1/trades \
  -H "X-API-Key: atx_live_your_key" \
  -H "Content-Type: application/json" \
  -d '{"side": "sell", "asset": "COMPUTE", "quantity": 50, "price_per_unit": 18.00}'
```

Cost basis methods: FIFO (default), LIFO, Specific ID.

---

## Understanding the Response

### Audit Trail

Every response (authenticated) includes an `audit_trail` showing exactly how the tax was determined:

- **`jurisdiction_chain`**: Layered rate composition (state + local + special district)
- **`classification`**: How your `transaction_type` and `work_type` mapped to an economic category
- **`taxability`**: Which state rule determined taxability and at what rate
- **`exemptions_evaluated`**: Every exemption check that was run and its result
- **`policy_references`**: Which entries in the AgentTax Tax Policy Registry applied

### Confidence Scoring

Every response includes a confidence object with a score (0-100) and level (`complete`, `high`, `partial`, `minimal`). To maximize confidence:
- Provide `buyer_zip` (not just `buyer_state`)
- Provide `work_type` explicitly
- Configure nexus states via `/api/v1/nexus`

### Advisories

The `advisories` array flags edge cases: zip/state mismatches, nexus warnings, classification review suggestions, local tax advisories (e.g., Chicago's 9% cloud tax).

---

## Common Integration Patterns

### Pattern 1: Pre-transaction tax lookup (buyer)

```python
# Before purchasing compute, check tax obligation
import requests

response = requests.post("https://agenttax.io/api/v1/calculate", json={
    "role": "buyer",
    "amount": 1000,
    "buyer_state": "NY",
    "buyer_zip": "10001",
    "transaction_type": "compute",
    "work_type": "compute",
    "counterparty_id": "gpu-provider-42",
    "is_b2b": True
}, headers={"X-API-Key": "atx_live_your_key"})

tax = response.json()
total_cost = 1000 + tax["total_tax"]  # Factor tax into budget
```

### Pattern 2: Invoice tax collection (seller)

```python
# Calculate tax to add to invoice
response = requests.post("https://agenttax.io/api/v1/calculate", json={
    "role": "seller",
    "amount": 2500,
    "buyer_state": "TX",
    "buyer_zip": "75201",
    "transaction_type": "saas",
    "work_type": "content",
    "counterparty_id": "buyer-agent-99"
}, headers={"X-API-Key": "atx_live_your_key"})

tax = response.json()
invoice_total = 2500 + tax["total_tax"]
```

### Pattern 3: Multi-state compliance check

```python
# Check rates across states you operate in
for state in ["TX", "NY", "CA", "WA"]:
    r = requests.get(f"https://agenttax.io/api/v1/rates?state={state}")
    print(f"{state}: {r.json()['rate']*100}% — {r.json()['saasNote']}")
```

### Pattern 4: x402 micropayment (no account)

```python
# Pay per call with USDC — no API key needed
# Your x402-compatible HTTP client handles payment automatically
response = x402_client.post("https://agenttax.io/api/v1/calculate", json={...})
```

### Pattern 5: JavaScript / Node.js

```javascript
const response = await fetch("https://agenttax.io/api/v1/calculate", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "X-API-Key": "atx_live_your_key",
  },
  body: JSON.stringify({
    role: "buyer",
    amount: 750,
    buyer_state: "WA",
    buyer_zip: "98101",
    transaction_type: "ai_model_access",
    work_type: "compute",
    counterparty_id: "model-provider-7",
  }),
});

const tax = await response.json();
console.log(`Tax: $${tax.total_tax} (${(tax.combined_rate * 100).toFixed(2)}%)`);
```

---

## Key Concepts

- **Nexus**: You only need to collect sales tax in states where you have economic nexus. Configure via `/api/v1/nexus`.
- **Use tax**: If the seller doesn't collect, the buyer owes use tax. AgentTax calculates both.
- **Conservative default**: When law is ambiguous, AgentTax defaults to more tax, not less. Better to over-reserve than face penalties.
- **Local rates**: 105+ zip codes with city/county/district rates. Pass `buyer_zip` to get combined rates.
- **1099 tracking**: AgentTax tracks cumulative vendor payments and flags when the $600 threshold is crossed.

---

## Rate Limits

| Mode | Limit |
|------|-------|
| Demo (no key) | 50/day, 30/min |
| Free tier | 100 calls/month |
| Starter ($25/mo) | 10,000 calls/month |
| Growth ($99/mo) | 100,000 calls/month |
| Pro ($199/mo) | 1,000,000 calls/month |
| x402 | Unlimited (pay per call) |

---

## Error Handling

All errors return `{ "success": false, "error": "message", "agent_guide": "https://agenttax.io/api/v1/agents" }`. Common codes:

| Status | Meaning |
|--------|---------|
| 400 | Bad request — check `error` and `errors` fields |
| 401 | Invalid or missing API key |
| 402 | x402 payment required |
| 429 | Rate limited |
| 405 | Wrong HTTP method |

---

## Need Help?

- API docs: https://agenttax.io/?view=api-docs
- Health check: https://agenttax.io/api/v1/health
- Rate data: https://agenttax.io/api/v1/rates
- This guide (always current): https://agenttax.io/api/v1/agents
