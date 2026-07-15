"""
Order placement logic.
Orchestrates validation, API calls, logging, and output formatting.
No knowledge of argparse or CLI concerns.
"""

from bot.client import get_futures_client, place_futures_order, BinanceClientError
from bot.validators import validate_order_params, ValidationError
from bot.logging_config import get_logger

logger = get_logger()


def format_order_summary(params: dict) -> str:
    """Formats a human-readable order request summary."""
    lines = [
        "",
        "═" * 50,
        "  ORDER REQUEST SUMMARY",
        "═" * 50,
        f"  Symbol:     {params['symbol']}",
        f"  Side:       {params['side']}",
        f"  Type:       {params['type']}",
        f"  Quantity:   {params['quantity']}",
    ]
    if "price" in params:
        lines.append(f"  Price:      {params['price']}")
    lines.append("═" * 50)
    return "\n".join(lines)


def format_order_response(response: dict) -> str:
    """Formats a human-readable order response."""
    lines = [
        "",
        "═" * 50,
        "  ORDER RESPONSE",
        "═" * 50,
        f"  Order ID:       {response.get('orderId', 'N/A')}",
        f"  Status:         {response.get('status', 'N/A')}",
        f"  Symbol:         {response.get('symbol', 'N/A')}",
        f"  Side:           {response.get('side', 'N/A')}",
        f"  Type:           {response.get('type', 'N/A')}",
        f"  Orig Qty:       {response.get('origQty', 'N/A')}",
        f"  Executed Qty:   {response.get('executedQty', 'N/A')}",
    ]

    # Include average price if available
    avg_price = response.get("avgPrice")
    if avg_price and avg_price != "0":
        lines.append(f"  Avg Price:      {avg_price}")

    # Include price for LIMIT orders
    price = response.get("price")
    if price and price != "0":
        lines.append(f"  Price:          {price}")

    lines.append("═" * 50)
    return "\n".join(lines)


def execute_order(symbol: str, side: str, order_type: str, quantity, price=None) -> bool:
    """
    Full order execution pipeline:
    1. Validate inputs
    2. Print order summary
    3. Place order via API
    4. Print response details
    5. Return True on success, False on failure

    All errors are caught and presented as readable messages (no raw stack traces).
    """
    # Step 1: Validate inputs
    try:
        params = validate_order_params(symbol, side, order_type, quantity, price)
    except ValidationError as e:
        logger.warning("Validation failed: %s", str(e))
        print(f"\n❌ Validation Error: {e}")
        return False

    # Step 2: Print order summary
    summary = format_order_summary(params)
    print(summary)
    logger.info("Order request: %s %s %s qty=%s%s",
                params["side"], params["type"], params["symbol"],
                params["quantity"],
                f" price={params['price']}" if "price" in params else "")

    # Step 3: Place order via API
    try:
        client = get_futures_client()
        response = place_futures_order(client, params)
    except BinanceClientError as e:
        print(f"\n❌ Order Failed: {e}")
        return False

    # Step 4: Print response and success message
    response_output = format_order_response(response)
    print(response_output)

    status = response.get("status", "UNKNOWN")
    order_id = response.get("orderId", "N/A")

    if status in ("NEW", "FILLED", "PARTIALLY_FILLED"):
        print(f"\n✅ Order placed successfully! (ID: {order_id}, Status: {status})")
        logger.info("Order success: orderId=%s, status=%s", order_id, status)
        return True
    else:
        print(f"\n⚠️  Order submitted but status is '{status}'. (ID: {order_id})")
        logger.warning("Order submitted with unexpected status: orderId=%s, status=%s", order_id, status)
        return True
