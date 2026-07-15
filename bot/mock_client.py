"""
Mock Binance Futures client for dry-run testing.
Mimics the response shape of python-binance's futures_create_order()
without making any network requests or requiring API credentials.
"""

import random
import time
from bot.logging_config import get_logger
from bot.client import BinanceClientError

logger = get_logger()

# Simulated market prices for common testnet symbols
MOCK_PRICES = {
    "BTCUSDT": 98250.00,
    "ETHUSDT": 3485.50,
    "BNBUSDT": 612.30,
    "SOLUSDT": 178.45,
    "XRPUSDT": 0.6250,
    "DOGEUSDT": 0.1185,
    "ADAUSDT": 0.4520,
}

# Symbols that simulate a Binance API error
INVALID_SYMBOLS = {"INVALIDUSDT", "FAKECOIN", "XXXYYY"}

# Symbols that simulate insufficient margin
LOW_MARGIN_SYMBOLS = {"LOWMARGINUSDT"}


class MockFuturesClient:
    """
    A mock client that behaves like python-binance's Client
    for futures order placement, but returns fake data.
    """

    def __init__(self):
        logger.info("[DRY-RUN] Mock Binance Futures client initialized (no real connection).")

    def futures_create_order(self, **kwargs) -> dict:
        """
        Simulates placing a futures order.
        Returns a realistic response dict or raises BinanceClientError
        to simulate API errors.
        """
        symbol = kwargs.get("symbol", "")
        side = kwargs.get("side", "")
        order_type = kwargs.get("type", "")
        quantity = kwargs.get("quantity", 0)
        price = kwargs.get("price")

        # Simulate invalid symbol error (-1121)
        if symbol in INVALID_SYMBOLS:
            logger.error("[DRY-RUN] Simulated Binance API error [-1121]: Invalid symbol.")
            raise BinanceClientError(
                "Binance API error (-1121): Invalid symbol."
            )

        # Simulate insufficient margin error (-2019)
        if symbol in LOW_MARGIN_SYMBOLS:
            logger.error("[DRY-RUN] Simulated Binance API error [-2019]: Margin is insufficient.")
            raise BinanceClientError(
                "Binance API error (-2019): Margin is insufficient."
            )

        # Generate a realistic mock response
        order_id = random.randint(100000000, 999999999)
        timestamp = int(time.time() * 1000)

        # Determine simulated price
        if order_type == "MARKET":
            sim_price = MOCK_PRICES.get(symbol, 100.00)
            # Add slight random variance (±0.5%)
            sim_price *= (1 + random.uniform(-0.005, 0.005))
            sim_price = round(sim_price, 2)
            status = "FILLED"
            executed_qty = str(quantity)
        else:
            # LIMIT orders are typically NEW (waiting to be filled)
            sim_price = float(price) if price else 0.0
            status = "NEW"
            executed_qty = "0"

        response = {
            "orderId": order_id,
            "symbol": symbol,
            "status": status,
            "clientOrderId": f"mock_{random.randint(10000, 99999)}",
            "price": str(sim_price) if order_type == "LIMIT" else "0",
            "avgPrice": str(sim_price) if order_type == "MARKET" else "0",
            "origQty": str(quantity),
            "executedQty": executed_qty,
            "cumQuote": str(round(sim_price * float(quantity), 2)),
            "timeInForce": "GTC" if order_type == "LIMIT" else "GTC",
            "type": order_type,
            "side": side,
            "stopPrice": "0",
            "workingType": "CONTRACT_PRICE",
            "origType": order_type,
            "updateTime": timestamp,
        }

        logger.info(
            "[DRY-RUN] Simulated %s %s order: orderId=%s, status=%s",
            side, order_type, order_id, status,
        )

        return response


def get_mock_futures_client() -> MockFuturesClient:
    """Returns an initialized mock client."""
    return MockFuturesClient()


def place_mock_futures_order(client: MockFuturesClient, order_params: dict) -> dict:
    """
    Places a mock futures order using the mock client.
    Mirrors the interface of client.place_futures_order().
    """
    kwargs = {
        "symbol": order_params["symbol"],
        "side": order_params["side"],
        "type": order_params["type"],
        "quantity": order_params["quantity"],
    }

    if order_params["type"] == "LIMIT":
        kwargs["price"] = str(order_params["price"])
        kwargs["timeInForce"] = "GTC"

    logger.info(
        "[DRY-RUN] Placing %s %s order: symbol=%s, qty=%s%s",
        order_params["side"],
        order_params["type"],
        order_params["symbol"],
        order_params["quantity"],
        f", price={order_params['price']}" if "price" in order_params else "",
    )

    try:
        response = client.futures_create_order(**kwargs)
        logger.info(
            "[DRY-RUN] Order simulated successfully: orderId=%s, status=%s",
            response.get("orderId"),
            response.get("status"),
        )
        return response

    except BinanceClientError:
        raise  # Already logged and formatted in futures_create_order
