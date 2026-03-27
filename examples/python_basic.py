"""
AgentTax — Basic Python Integration
Calculate sales tax for an AI agent transaction.
"""

import requests

API_KEY = "atx_live_your_key"  # or omit for demo mode
BASE_URL = "https://agenttax.io"


def calculate_tax(role, amount, buyer_state, transaction_type, counterparty_id,
                  buyer_zip=None, work_type=None, is_b2b=False):
    """Calculate sales/use tax for a transaction."""
    payload = {
        "role": role,
        "amount": amount,
        "buyer_state": buyer_state,
        "transaction_type": transaction_type,
        "counterparty_id": counterparty_id,
    }
    if buyer_zip:
        payload["buyer_zip"] = buyer_zip
    if work_type:
        payload["work_type"] = work_type
    if is_b2b:
        payload["is_b2b"] = True

    headers = {"Content-Type": "application/json"}
    if API_KEY != "atx_live_your_key":
        headers["X-API-Key"] = API_KEY

    resp = requests.post(f"{BASE_URL}/api/v1/calculate", json=payload, headers=headers)
    return resp.json()


def log_trade(trade_type, asset_symbol, quantity, price_per_unit, resident_state=None):
    """Log a buy or sell for capital gains tracking."""
    payload = {
        "trade_type": trade_type,
        "asset_symbol": asset_symbol,
        "quantity": quantity,
        "price_per_unit": price_per_unit,
    }
    if resident_state:
        payload["resident_state"] = resident_state
    resp = requests.post(f"{BASE_URL}/api/v1/trades", json=payload,
                         headers={"X-API-Key": API_KEY})
    return resp.json()


if __name__ == "__main__":
    # Example: buyer in Austin, TX purchasing compute
    result = calculate_tax(
        role="buyer",
        amount=500,
        buyer_state="TX",
        buyer_zip="78701",
        transaction_type="compute",
        work_type="compute",
        counterparty_id="gpu-provider-42",
        is_b2b=True,
    )

    print(f"Tax: ${result['total_tax']}")
    print(f"Rate: {result['combined_rate'] * 100:.2f}%")
    print(f"Confidence: {result['confidence']['level']}")
