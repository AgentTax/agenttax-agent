#!/bin/bash
# AgentTax — curl Examples
# All examples work in demo mode (no API key). Add -H "X-API-Key: atx_live_xxx" for authenticated access.

# ── Calculate sales tax (buyer in Austin, TX) ──
curl -s -X POST https://agenttax.io/api/v1/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "role": "buyer",
    "amount": 500,
    "buyer_state": "TX",
    "buyer_zip": "78701",
    "transaction_type": "compute",
    "work_type": "compute",
    "counterparty_id": "seller-123"
  }' | jq .

# ── Calculate sales tax (seller with nexus in NY) ──
curl -s -X POST https://agenttax.io/api/v1/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "role": "seller",
    "amount": 2500,
    "buyer_state": "NY",
    "buyer_zip": "10001",
    "transaction_type": "saas",
    "work_type": "content",
    "counterparty_id": "buyer-456",
    "nexus_override": {"NY": {"hasNexus": true}}
  }' | jq .

# ── Get all state rates ──
curl -s https://agenttax.io/api/v1/rates | jq .summary

# ── Get single state rate with explanation ──
curl -s "https://agenttax.io/api/v1/rates?state=TX&explain=true" | jq .

# ── Health check ──
curl -s https://agenttax.io/api/v1/health | jq .

# ── Fetch the agent integration guide ──
curl -s https://agenttax.io/api/v1/agents
