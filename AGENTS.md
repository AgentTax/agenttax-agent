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

### 1. Sign up and save your API key

```bash
curl -X POST https://agenttax.io/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "you@example.com", "password": "securepass", "agent_name": "my-agent"}'
```

Response (truncated):

```json
{
  "success": true,
  "api_key": {
    "key": "atx_live_abc123xyz...",
    "prefix": "atx_live_abc1",
    "note": "Save this key — it won't be shown again."
  },
  "next_steps": [
    "Save your API key securely",
    "Try a test calculation: POST /api/v1/calculate"
  ]
}
```

**Save the `api_key.key` value immediately.** It is only returned once at signup.

Or skip signup and use demo mode (no key needed, 50 calls/day).

### 1.5. Configure your nexus states (sellers only)

If you're a seller, you must configure which states you have economic nexus in. Without this, all seller calculations return $0 (no collection obligation).

```bash
curl -X POST https://agenttax.io/api/v1/nexus \
  -H "X-API-Key: atx_live_your_key" \
  -H "Content-Type: application/json" \
  -d '{
    "nexus": {
      "TX": { "hasNexus": true, "reason": "Economic nexus — over $500K revenue" },
      "NY": { "hasNexus": true, "reason": "Physical presence" },
      "CA": { "hasNexus": true, "reason": "Economic nexus" }
    }
  }'
```

Buyers don't need nexus configuration — use tax is calculated regardless.

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
  "transaction_id": "txn_m3k9x2_a1b2c3",
  "timestamp": "2026-03-26T14:30:00.000Z",
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
    "gross_amount": 500,
    "taxable_amount": 400,
    "taxable_percentage": 0.80,
    "reason": "Austin, TX 8.25% combined rate applied to 80% of Compute/Processing ($400.00 of $500.00).",
    "note": "TX Tax Code §151.351 — 20% statutory exemption"
  },
  "confidence": { "score": 90, "level": "complete", "factors": ["..."] },
  "audit_trail": {
    "engine_version": "1.5",
    "jurisdiction_chain": [
      { "level": "state", "jurisdiction": "Texas", "code": "TX", "rate": 0.0625, "applied": true, "source": "TAX_RATES" },
      { "level": "local", "jurisdiction": "Austin", "zip": "78701", "rate": 0.02, "applied": true, "source": "LOCAL_RATES" },
      { "level": "special_rule", "rules": [
        { "rule": "taxable_percentage", "state": "TX", "value": 0.80, "effect": "Taxable base reduced to 80%", "note": "TX Tax Code §151.351 — 20% statutory exemption" }
      ]}
    ],
    "combined_rate": 0.0825,
    "classification": {
      "input_transaction_type": "compute",
      "input_work_type": "compute",
      "resolved_work_type": "compute",
      "work_type_source": "explicit",
      "economic_category": "data_processing",
      "label": "Compute/Processing"
    },
    "taxability": {
      "source": "TAXABILITY_MATRIX",
      "state": "TX",
      "category": "data_processing",
      "taxable": true,
      "note": "TX Tax Code §151.351 — 20% statutory exemption"
    },
    "exemptions_evaluated": [
      { "check": "no_sales_tax", "result": "not_exempt", "detail": "Texas has 6.25% state sales tax" },
      { "check": "financial_service", "result": "not_exempt", "detail": "Category is data_processing" },
      { "check": "b2b_statutory", "result": "not_exempt", "detail": "B2B exemption does not apply in Texas for data_processing" }
    ],
    "final_determination": "taxable",
    "policy_references": [
      { "id": "texas_80pct_rule", "settlement": "settled", "note": "TX Tax Code §151.351" }
    ]
  },
  "advisories": [],
  "disclaimer": "This calculation is informational only and does not constitute tax advice."
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
| `/api/v1/agents` | GET | None | This integration guide (plain text) |
| `/api/v1/health` | GET | None | Health check |

### Authentication

Three modes — use whichever fits your architecture:

1. **API Key** (recommended): `X-API-Key: atx_live_xxx` header or `Authorization: Bearer atx_live_xxx`
2. **x402 USDC micropayment**: Pay-per-call via x402 protocol (USDC on Base). No account needed.
3. **Demo mode**: No auth. 50 calls/day, 30/min. Returns simplified responses (no audit trail).

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
| `nexus_override` | object | null | Override nexus states (demo/x402 only) |

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
  -d '{
    "asset_symbol": "COMPUTE",
    "trade_type": "buy",
    "quantity": 100,
    "price_per_unit": 12.50
  }'

# Log a sell — response includes realized gain/loss
curl -X POST https://agenttax.io/api/v1/trades \
  -H "X-API-Key: atx_live_your_key" \
  -H "Content-Type: application/json" \
  -d '{
    "asset_symbol": "COMPUTE",
    "trade_type": "sell",
    "quantity": 50,
    "price_per_unit": 18.00,
    "resident_state": "TX"
  }'
```

### POST /api/v1/trades — Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `asset_symbol` | string | yes | Asset identifier (e.g., `"COMPUTE"`, `"GPU_HOUR"`) |
| `trade_type` | `"buy"` or `"sell"` | yes | Buy or sell |
| `quantity` | number | yes | Number of units |
| `price_per_unit` | number | yes | Price per unit in USD |
| `accounting_method` | string | no | `"fifo"` (default), `"lifo"`, or `"specific_id"` |
| `resident_state` | string | no | 2-letter state code for state tax estimates on gains |
| `specific_lot_id` | string | no | Lot ID for specific identification method |
| `notes` | string | no | Free-text notes |

---

## Understanding the Response

### Audit Trail

Every authenticated response includes an `audit_trail` showing exactly how the tax was determined (see full example in Step 3 above):

- **`jurisdiction_chain`**: Layered rate composition — state base rate, local add-on, special rules (TX 80%, MD split, CT 1%)
- **`classification`**: How your `transaction_type` and `work_type` mapped to an economic category
- **`taxability`**: Which state rule (TAXABILITY_MATRIX or digitalTaxable fallback) determined taxability
- **`exemptions_evaluated`**: Every exemption check that was run and its result
- **`final_determination`**: `"taxable"` or the exemption type that applied
- **`policy_references`**: Which entries in the AgentTax Tax Policy Registry applied, with settlement status

Demo mode responses do not include `audit_trail`, `advisories`, or detailed tax objects. Create a free account ($0) to get the full response.

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
}, headers={"X-API-Key": API_KEY})

tax = response.json()
total_cost = 1000 + tax["total_tax"]  # Factor tax into budget
```

### Pattern 2: Invoice tax collection (seller)

```python
response = requests.post("https://agenttax.io/api/v1/calculate", json={
    "role": "seller",
    "amount": 2500,
    "buyer_state": "TX",
    "buyer_zip": "75201",
    "transaction_type": "saas",
    "work_type": "content",
    "counterparty_id": "buyer-agent-99"
}, headers={"X-API-Key": API_KEY})

tax = response.json()
invoice_total = 2500 + tax["total_tax"]
```

### Pattern 3: Multi-state rate check

```python
for state in ["TX", "NY", "CA", "WA"]:
    r = requests.get(f"https://agenttax.io/api/v1/rates?state={state}")
    data = r.json()
    print(f"{state}: {data['rate']*100}% — {data['saasNote']}")
```

### Pattern 4: x402 micropayment (no account)

```python
# Pay per call with USDC — no API key needed
# Your x402-compatible HTTP client handles payment automatically
response = x402_client.post("https://agenttax.io/api/v1/calculate", json={...})
```

---

## Key Concepts

- **Nexus**: Sellers must configure nexus states to get non-zero tax results. Without nexus config, seller calculations return $0. Use `POST /api/v1/nexus`. Buyers don't need this — use tax is calculated regardless.
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

- This guide (always current): https://agenttax.io/api/v1/agents
- API docs: https://agenttax.io/?view=api-docs
- Health check: https://agenttax.io/api/v1/health
- Rate data: https://agenttax.io/api/v1/rates
