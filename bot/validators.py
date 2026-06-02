"""Input validation for trading bot parameters."""

import re

VALID_SIDES = ("BUY", "SELL")
VALID_ORDER_TYPES = ("MARKET", "LIMIT", "STOP_LIMIT")
SYMBOL_PATTERN = re.compile(r"^[A-Z]{2,20}$")


def validate_symbol(symbol: str) -> str:
    """Validate and normalize a trading symbol.

    Args:
        symbol: Trading pair symbol (e.g., BTCUSDT).

    Returns:
        Uppercase symbol string.

    Raises:
        ValueError: If symbol is empty or has invalid characters.
    """
    symbol = symbol.strip().upper()
    if not symbol:
        raise ValueError("Symbol cannot be empty.")
    if not SYMBOL_PATTERN.match(symbol):
        raise ValueError(
            f"Invalid symbol '{symbol}'. Must be 2-20 uppercase letters (e.g., BTCUSDT)."
        )
    return symbol


def validate_side(side: str) -> str:
    """Validate order side.

    Args:
        side: Order side (BUY or SELL).

    Returns:
        Uppercase side string.

    Raises:
        ValueError: If side is not BUY or SELL.
    """
    side = side.strip().upper()
    if side not in VALID_SIDES:
        raise ValueError(f"Invalid side '{side}'. Must be one of: {', '.join(VALID_SIDES)}.")
    return side


def validate_order_type(order_type: str) -> str:
    """Validate order type.

    Args:
        order_type: Order type (MARKET, LIMIT, or STOP_LIMIT).

    Returns:
        Uppercase order type string.

    Raises:
        ValueError: If order type is not recognized.
    """
    order_type = order_type.strip().upper()
    if order_type not in VALID_ORDER_TYPES:
        raise ValueError(
            f"Invalid order type '{order_type}'. Must be one of: {', '.join(VALID_ORDER_TYPES)}."
        )
    return order_type


def validate_quantity(quantity: float) -> float:
    """Validate order quantity.

    Args:
        quantity: Order quantity.

    Returns:
        Validated quantity.

    Raises:
        ValueError: If quantity is not positive.
    """
    if quantity <= 0:
        raise ValueError(f"Quantity must be greater than 0, got {quantity}.")
    return quantity


def validate_price(price: float | None, order_type: str) -> float | None:
    """Validate price based on order type.

    Args:
        price: Order price (required for LIMIT and STOP_LIMIT).
        order_type: The order type.

    Returns:
        Validated price or None for MARKET orders.

    Raises:
        ValueError: If price is missing for LIMIT/STOP_LIMIT or provided for MARKET.
    """
    if order_type == "MARKET":
        if price is not None:
            raise ValueError("Price should not be specified for MARKET orders.")
        return None

    if price is None:
        raise ValueError(f"Price is required for {order_type} orders.")
    if price <= 0:
        raise ValueError(f"Price must be greater than 0, got {price}.")
    return price


def validate_stop_price(stop_price: float | None, order_type: str) -> float | None:
    """Validate stop price for STOP_LIMIT orders.

    Args:
        stop_price: Stop trigger price.
        order_type: The order type.

    Returns:
        Validated stop price or None.

    Raises:
        ValueError: If stop price is missing for STOP_LIMIT or provided for other types.
    """
    if order_type != "STOP_LIMIT":
        if stop_price is not None:
            raise ValueError(f"Stop price should not be specified for {order_type} orders.")
        return None

    if stop_price is None:
        raise ValueError("Stop price is required for STOP_LIMIT orders.")
    if stop_price <= 0:
        raise ValueError(f"Stop price must be greater than 0, got {stop_price}.")
    return stop_price
