"""
Binance Futures Testnet API client wrapper.
Handles connection setup and raw API calls. No knowledge of CLI or argparse.
"""

import os
from dotenv import load_dotenv
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException
from bot.logging_config import get_logger

logger = get_logger()

# Binance Futures Testnet base URLs
FUTURES_TESTNET_URL = "https://testnet.binancefuture.com"
FUTURES_TESTNET_API = "https://testnet.binancefuture.com/fapi"


class BinanceClientError(Exception):
    """Raised when the Binance client encounters an error."""
    pass


def _load_credentials() -> tuple[str, str]:
    """
    Loads API credentials from .env file.
    Raises BinanceClientError if keys are missing.
    """
    load_dotenv()

    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")

    if not api_key or not api_secret:
        raise BinanceClientError(
            "Missing API credentials. Ensure BINANCE_API_KEY and BINANCE_API_SECRET "
            "are set in your .env file."
        )

    return api_key, api_secret


def get_futures_client() -> Client:
    """
    Creates and returns a Binance client configured for Futures Testnet.
    """
    api_key, api_secret = _load_credentials()

    client = Client(api_key, api_secret, testnet=True)

    # Override the futures API URL to point to the testnet
    client.FUTURES_URL = FUTURES_TESTNET_API

    logger.info("Binance Futures Testnet client initialized successfully.")
    return client


def place_futures_order(client: Client, order_params: dict) -> dict:
    """
    Places a futures order using the provided client and validated parameters.

    Args:
        client: An initialized Binance Client instance.
        order_params: A dict with keys: symbol, side, type, quantity, and optionally price.

    Returns:
        The API response dict on success.

    Raises:
        BinanceClientError: On API errors or network failures.
    """
    # Build the API call kwargs
    kwargs = {
        "symbol": order_params["symbol"],
        "side": order_params["side"],
        "type": order_params["type"],
        "quantity": order_params["quantity"],
    }

    # LIMIT orders require price and timeInForce
    if order_params["type"] == "LIMIT":
        kwargs["price"] = str(order_params["price"])
        kwargs["timeInForce"] = "GTC"  # Good Till Cancelled

    logger.info(
        "Placing %s %s order: symbol=%s, qty=%s%s",
        order_params["side"],
        order_params["type"],
        order_params["symbol"],
        order_params["quantity"],
        f", price={order_params['price']}" if "price" in order_params else "",
    )

    try:
        response = client.futures_create_order(**kwargs)
        logger.info(
            "Order placed successfully: orderId=%s, status=%s",
            response.get("orderId"),
            response.get("status"),
        )
        return response

    except BinanceAPIException as e:
        logger.error("Binance API error [%s]: %s", e.code, e.message)
        raise BinanceClientError(
            f"Binance API error ({e.code}): {e.message}"
        ) from e

    except BinanceRequestException as e:
        logger.error("Binance request error: %s", str(e))
        raise BinanceClientError(
            f"Binance request failed: {str(e)}"
        ) from e

    except ConnectionError as e:
        logger.error("Network error: %s", str(e))
        raise BinanceClientError(
            "Network error: Could not connect to Binance. Check your internet connection."
        ) from e

    except Exception as e:
        logger.error("Unexpected error placing order: %s", str(e))
        raise BinanceClientError(
            f"Unexpected error: {str(e)}"
        ) from e
