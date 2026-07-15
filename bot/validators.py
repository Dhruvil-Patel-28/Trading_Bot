"""
Input validators for order parameters.
Validates symbol, side, order type, quantity, and price before any API call is made.
"""

import re


class ValidationError(Exception):
    """Raised when order input validation fails."""
    pass


def validate_symbol(symbol: str) -> str:
    """
    Validates the trading symbol.
    Must be a non-empty uppercase alphanumeric string (e.g., BTCUSDT).
    """
    if not symbol or not isinstance(symbol, str):
        raise ValidationError("Symbol is required and must be a non-empty string.")

    symbol = symbol.upper().strip()

    if not re.match(r"^[A-Z0-9]{2,20}$", symbol):
        raise ValidationError(
            f"Invalid symbol '{symbol}'. Must be 2-20 uppercase alphanumeric characters (e.g., BTCUSDT)."
        )

    return symbol


def validate_side(side: str) -> str:
    """
    Validates the order side.
    Must be either 'BUY' or 'SELL'.
    """
    if not side or not isinstance(side, str):
        raise ValidationError("Side is required and must be 'BUY' or 'SELL'.")

    side = side.upper().strip()

    if side not in ("BUY", "SELL"):
        raise ValidationError(
            f"Invalid side '{side}'. Must be 'BUY' or 'SELL'."
        )

    return side


def validate_order_type(order_type: str) -> str:
    """
    Validates the order type.
    Must be either 'MARKET' or 'LIMIT'.
    """
    if not order_type or not isinstance(order_type, str):
        raise ValidationError("Order type is required and must be 'MARKET' or 'LIMIT'.")

    order_type = order_type.upper().strip()

    if order_type not in ("MARKET", "LIMIT"):
        raise ValidationError(
            f"Invalid order type '{order_type}'. Must be 'MARKET' or 'LIMIT'."
        )

    return order_type


def validate_quantity(quantity) -> float:
    """
    Validates the order quantity.
    Must be a positive number.
    """
    if quantity is None:
        raise ValidationError("Quantity is required.")

    try:
        qty = float(quantity)
    except (ValueError, TypeError):
        raise ValidationError(
            f"Invalid quantity '{quantity}'. Must be a positive number."
        )

    if qty <= 0:
        raise ValidationError(
            f"Invalid quantity '{qty}'. Must be greater than 0."
        )

    return qty


def validate_price(price, order_type: str) -> float | None:
    """
    Validates the price.
    Required and must be > 0 for LIMIT orders.
    Ignored for MARKET orders.
    """
    if order_type == "MARKET":
        return None

    # LIMIT order — price is required
    if price is None:
        raise ValidationError("Price is required for LIMIT orders.")

    try:
        p = float(price)
    except (ValueError, TypeError):
        raise ValidationError(
            f"Invalid price '{price}'. Must be a positive number."
        )

    if p <= 0:
        raise ValidationError(
            f"Invalid price '{p}'. Must be greater than 0 for LIMIT orders."
        )

    return p


def validate_order_params(symbol: str, side: str, order_type: str, quantity, price=None) -> dict:
    """
    Validates all order parameters and returns a clean, normalized dict.
    Raises ValidationError with a clear message if any parameter is invalid.
    """
    validated_symbol = validate_symbol(symbol)
    validated_side = validate_side(side)
    validated_type = validate_order_type(order_type)
    validated_qty = validate_quantity(quantity)
    validated_price = validate_price(price, validated_type)

    params = {
        "symbol": validated_symbol,
        "side": validated_side,
        "type": validated_type,
        "quantity": validated_qty,
    }

    if validated_price is not None:
        params["price"] = validated_price

    return params
