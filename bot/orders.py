"""Order placement logic for Market, Limit, and Stop-Limit orders."""

import logging

from bot.client import BinanceFuturesClient

logger = logging.getLogger("trading_bot.orders")


def _format_response(response: dict) -> dict:
    """Extract and format key fields from the API order response.

    Args:
        response: Raw API response dict.

    Returns:
        Dict with the most important order details.
    """
    return {
        "orderId": response.get("orderId"),
        "symbol": response.get("symbol"),
        "side": response.get("side"),
        "type": response.get("type"),
        "status": response.get("status"),
        "origQty": response.get("origQty"),
        "executedQty": response.get("executedQty"),
        "avgPrice": response.get("avgPrice", "N/A"),
        "price": response.get("price", "N/A"),
        "stopPrice": response.get("stopPrice", "N/A"),
    }


def place_market_order(
    client: BinanceFuturesClient,
    symbol: str,
    side: str,
    quantity: float,
) -> dict:
    """Place a market order.

    Args:
        client: Authenticated Binance client.
        symbol: Trading pair (e.g., BTCUSDT).
        side: BUY or SELL.
        quantity: Order quantity.

    Returns:
        Formatted order response.
    """
    logger.info("Preparing MARKET %s order: %s qty=%s", side, symbol, quantity)

    response = client.place_order(
        symbol=symbol,
        side=side,
        type="MARKET",
        quantity=quantity,
    )

    return _format_response(response)


def place_limit_order(
    client: BinanceFuturesClient,
    symbol: str,
    side: str,
    quantity: float,
    price: float,
) -> dict:
    """Place a limit order.

    Args:
        client: Authenticated Binance client.
        symbol: Trading pair (e.g., BTCUSDT).
        side: BUY or SELL.
        quantity: Order quantity.
        price: Limit price.

    Returns:
        Formatted order response.
    """
    logger.info(
        "Preparing LIMIT %s order: %s qty=%s price=%s", side, symbol, quantity, price
    )

    response = client.place_order(
        symbol=symbol,
        side=side,
        type="LIMIT",
        quantity=quantity,
        price=price,
        timeInForce="GTC",
    )

    return _format_response(response)


def place_stop_limit_order(
    client: BinanceFuturesClient,
    symbol: str,
    side: str,
    quantity: float,
    price: float,
    stop_price: float,
) -> dict:
    """Place a stop-limit order (bonus feature).

    Args:
        client: Authenticated Binance client.
        symbol: Trading pair (e.g., BTCUSDT).
        side: BUY or SELL.
        quantity: Order quantity.
        price: Limit price (executed when stop triggers).
        stop_price: Stop trigger price.

    Returns:
        Formatted order response.
    """
    logger.info(
        "Preparing STOP_LIMIT %s order: %s qty=%s price=%s stopPrice=%s",
        side,
        symbol,
        quantity,
        price,
        stop_price,
    )

    response = client.place_order(
        symbol=symbol,
        side=side,
        type="STOP",
        quantity=quantity,
        price=price,
        stopPrice=stop_price,
        timeInForce="GTC",
    )

    return _format_response(response)
