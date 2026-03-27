# AgentTax

**The tax API where AI agents are the customer.**

AI agents are transacting autonomously — purchasing compute, selling API access, trading tokens, subscribing to services. When Agent A (Delaware) sells to Agent B (Texas), someone owes Texas 8.25% sales tax. When a trading bot flips tokens, someone owes capital gains. No existing tax platform handles this. They all assume a human is in the loop.

AgentTax is built for machine-to-machine commerce. One API call, and your agent knows exactly what it owes, which jurisdiction it goes to, and why — with a full audit trail showing every rule that was applied.

## For AI Agents

**If you're an AI coding agent** integrating tax compliance, read [`AGENTS.md`](AGENTS.md) — it has everything you need to integrate in 5 minutes.

Or fetch the always-current version: `GET https://agenttax.io/api/v1/agents`

## Quick Start

```bash
curl -X POST https://agenttax.io/api/v1/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "role": "seller",
    "amount": 2500,
    "buyer_state": "TX",
    "buyer_zip": "78701",
    "transaction_type": "saas",
    "work_type": "content",
    "counterparty_id": "buyer-agent-42"
  }'
```

No API key needed for demo mode. [Sign up](https://agenttax.io) for full audit trails, transaction history, nexus monitoring, and capital gains tracking.

## What You Get Back

Every authenticated response includes:

- **Tax calculation** with combined state + local rates (51 jurisdictions, 105+ zip-level local rates)
- **Audit trail** showing the full jurisdiction chain, classification path, exemption checks, and policy references
- **Confidence score** reflecting input data completeness
- **Advisories** for edge cases (zip mismatches, local cloud taxes, classification review flags)
- **1099 tracking** with YTD vendor totals and threshold alerts

## Three Ways to Authenticate

1. **API Key**: `X-API-Key: atx_live_xxx` — standard, persistent state
2. **x402 micropayment**: Pay-per-call with USDC on Base — no account needed
3. **Demo mode**: No auth, rate-limited — try it right now

## Coverage

- **Sales tax**: 51 jurisdictions (all US states + DC), 105+ zip-level local rates
- **Taxability matrix**: Per-state, per-category rules (TX 80%, MD B2B/B2C split, CT 1% data processing, IA B2B exempt, and more)
- **Capital gains**: All 50 states + DC with short-term/long-term rates and exclusions
- **Work type classification**: compute, research, content, consulting, trading
- **1099 tracking**: Cumulative vendor payments with $600 threshold alerts
- **Nexus monitoring**: Per-state revenue tracking with economic nexus threshold alerts

## How It Works

AgentTax classifies AI agent work by economic category (`data_processing`, `information_service`, `digital_service`, `professional_service`) based on what the agent actually does. Each state taxes these categories differently. The engine resolves the correct rate through a jurisdiction dependency chain:

```
State base rate
  + Local add-on (city/county/district)
  + Special rules (TX 80%, MD B2B/B2C split, CT 1% data processing)
  - Exemptions (B2B statutory, no nexus, category exempt, buyer certificate)
  = Final tax obligation
```

Every response includes an `audit_trail` that shows this full chain.

## API Endpoints

| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/api/v1/calculate` | POST | Key / x402 / Demo | Calculate sales/use tax |
| `/api/v1/trades` | POST/GET | API Key | Capital gains tracking (FIFO/LIFO) |
| `/api/v1/transactions` | GET | API Key | Transaction history |
| `/api/v1/nexus` | POST/GET | API Key | Configure nexus states |
| `/api/v1/rates` | GET | None | 51-jurisdiction rate data |
| `/api/v1/rates/local` | GET | None | Zip-level combined rates |
| `/api/v1/rates/capital-gains` | GET | None | State capital gains rates |
| `/api/v1/network` | POST/GET | API Key | Agent network profile |
| `/api/v1/network-directory` | GET | None | Browse agent directory |
| `/api/v1/export/1099-da` | GET | API Key | IRS Form 1099-DA export |
| `/api/v1/agents` | GET | None | This integration guide (plain text) |
| `/api/v1/health` | GET | None | Health check |

Full API reference in [`AGENTS.md`](AGENTS.md) or at [agenttax.io](https://agenttax.io/?view=api-docs).

## Pricing

| Tier | Price | Calculations |
|------|-------|-------------|
| **Free** | $0 | 100/month |
| **Starter** | $25/mo | 10,000/month |
| **Growth** | $99/mo | 100,000/month |
| **Pro** | $199/mo | 1,000,000/month |
| **Enterprise** | Custom | Unlimited |
| **x402** | ~$0.001/call | Unlimited |

## Links

- **Website:** [agenttax.io](https://agenttax.io)
- **API Docs:** [agenttax.io/api-docs](https://agenttax.io/?view=api-docs)
- **Agent Guide:** [`AGENTS.md`](AGENTS.md)

---

Built by [Agentic Tax Solutions LLC](https://agenttax.io).
