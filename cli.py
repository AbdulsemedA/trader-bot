"""CLI entry point for the Binance Futures Testnet Trading Bot.

Usage examples:
    python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
    python cli.py --symbol BTCUSDT --side BUY --type LIMIT --quantity 0.001 --price 50000
    python cli.py --symbol ETHUSDT --side SELL --type STOP_LIMIT --quantity 0.01 --price 3000 --stop-price 2950
"""

import sys
from typing import Optional

import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from bot.client import BinanceAPIError
from bot.client import BinanceFuturesClient
from bot.logging_config import setup_logging
from bot.orders import place_limit_order
from bot.orders import place_market_order
from bot.orders import place_stop_limit_order
from bot.validators import validate_order_type
from bot.validators import validate_price
from bot.validators import validate_quantity
from bot.validators import validate_side
from bot.validators import validate_stop_price
from bot.validators import validate_symbol

import os

load_dotenv()

app = typer.Typer(
    name="trading-bot",
    help="🤖 Binance Futures Testnet Trading Bot — Place Market, Limit, and Stop-Limit orders.",
    add_completion=False,
)
console = Console()


def _print_order_summary(
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: float | None,
    stop_price: float | None,
) -> None:
    """Display a Rich panel summarizing the order request."""
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Field", style="bold cyan")
    table.add_column("Value", style="white")

    table.add_row("Symbol", symbol)
    table.add_row("Side", f"[green]{side}[/green]" if side == "BUY" else f"[red]{side}[/red]")
    table.add_row("Type", order_type)
    table.add_row("Quantity", str(quantity))

    if price is not None:
        table.add_row("Price", str(price))
    if stop_price is not None:
        table.add_row("Stop Price", str(stop_price))

    console.print(Panel(table, title="📋 Order Request", border_style="blue"))


def _print_order_response(result: dict) -> None:
    """Display a Rich table with the order response details."""
    table = Table(title="📊 Order Response", show_lines=True)
    table.add_column("Field", style="bold cyan", min_width=14)
    table.add_column("Value", style="white")

    status = result.get("status", "UNKNOWN")
    status_style = "green" if status in ("FILLED", "NEW") else "yellow"

    table.add_row("Order ID", str(result.get("orderId", "N/A")))
    table.add_row("Symbol", str(result.get("symbol", "N/A")))
    table.add_row("Side", str(result.get("side", "N/A")))
    table.add_row("Type", str(result.get("type", "N/A")))
    table.add_row("Status", f"[{status_style}]{status}[/{status_style}]")
    table.add_row("Original Qty", str(result.get("origQty", "N/A")))
    table.add_row("Executed Qty", str(result.get("executedQty", "N/A")))
    table.add_row("Avg Price", str(result.get("avgPrice", "N/A")))

    if result.get("price") and result["price"] != "N/A":
        table.add_row("Price", str(result["price"]))
    if result.get("stopPrice") and result["stopPrice"] != "N/A":
        table.add_row("Stop Price", str(result["stopPrice"]))

    console.print(table)


@app.command()
def place_order(
    symbol: str = typer.Option(..., "--symbol", "-s", help="Trading pair (e.g., BTCUSDT)"),
    side: str = typer.Option(..., "--side", "-d", help="Order side: BUY or SELL"),
    order_type: str = typer.Option(..., "--type", "-t", help="Order type: MARKET, LIMIT, or STOP_LIMIT"),
    quantity: float = typer.Option(..., "--quantity", "-q", help="Order quantity"),
    price: Optional[float] = typer.Option(None, "--price", "-p", help="Limit price (required for LIMIT/STOP_LIMIT)"),
    stop_price: Optional[float] = typer.Option(None, "--stop-price", "-sp", help="Stop price (required for STOP_LIMIT)"),
) -> None:
    """Place an order on Binance Futures Testnet."""
    # Initialize logging
    setup_logging()

    # --- Validate inputs ---
    try:
        symbol = validate_symbol(symbol)
        side = validate_side(side)
        order_type = validate_order_type(order_type)
        quantity = validate_quantity(quantity)
        price = validate_price(price, order_type)
        stop_price = validate_stop_price(stop_price, order_type)
    except ValueError as exc:
        console.print(f"[bold red]❌ Validation Error:[/bold red] {exc}")
        raise typer.Exit(code=1)

    # --- Print order summary ---
    _print_order_summary(symbol, side, order_type, quantity, price, stop_price)

    # --- Confirm with user ---
    if not typer.confirm("Do you want to proceed with this order?"):
        console.print("[yellow]⚠ Order cancelled by user.[/yellow]")
        raise typer.Exit(code=0)

    # --- Load API credentials ---
    api_key = os.getenv("BINANCE_API_KEY", "")
    api_secret = os.getenv("BINANCE_API_SECRET", "")

    if not api_key or not api_secret:
        console.print(
            "[bold red]❌ Missing API credentials.[/bold red] "
            "Set BINANCE_API_KEY and BINANCE_API_SECRET in your .env file."
        )
        raise typer.Exit(code=1)

    # --- Place the order ---
    try:
        client = BinanceFuturesClient(api_key, api_secret)

        if order_type == "MARKET":
            result = place_market_order(client, symbol, side, quantity)
        elif order_type == "LIMIT":
            result = place_limit_order(client, symbol, side, quantity, price)
        elif order_type == "STOP_LIMIT":
            result = place_stop_limit_order(client, symbol, side, quantity, price, stop_price)
        else:
            console.print(f"[bold red]❌ Unsupported order type: {order_type}[/bold red]")
            raise typer.Exit(code=1)

        _print_order_response(result)
        console.print("[bold green]✅ Order placed successfully![/bold green]")

    except BinanceAPIError as exc:
        console.print(f"[bold red]❌ API Error:[/bold red] {exc}")
        raise typer.Exit(code=2)
    except Exception as exc:
        console.print(f"[bold red]❌ Unexpected Error:[/bold red] {exc}")
        raise typer.Exit(code=2)


if __name__ == "__main__":
    app()
