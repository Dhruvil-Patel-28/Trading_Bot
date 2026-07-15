"""
CLI entry point for the Binance Futures Testnet Trading Bot.
Uses argparse to parse command-line arguments and delegates to the order execution pipeline.
"""

import argparse
import sys
from bot.orders import execute_order


def build_parser() -> argparse.ArgumentParser:
    """Builds and returns the argument parser."""
    parser = argparse.ArgumentParser(
        prog="trading_bot",
        description="Place orders on Binance Futures Testnet (USDT-M)",
        epilog=(
            "Examples:\n"
            "  Market Buy:   python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001\n"
            "  Limit Sell:   python cli.py --symbol ETHUSDT --side SELL --type LIMIT --quantity 0.01 --price 3500\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--symbol",
        required=True,
        help="Trading pair symbol (e.g., BTCUSDT, ETHUSDT)",
    )
    parser.add_argument(
        "--side",
        required=True,
        help="Order side: BUY or SELL",
    )
    parser.add_argument(
        "--type",
        required=True,
        dest="order_type",
        help="Order type: MARKET or LIMIT",
    )
    parser.add_argument(
        "--quantity",
        required=True,
        type=float,
        help="Order quantity (must be > 0)",
    )
    parser.add_argument(
        "--price",
        type=float,
        default=None,
        help="Order price (required for LIMIT orders, ignored for MARKET)",
    )

    return parser


def main():
    """Main entry point — parses args and executes the order."""
    parser = build_parser()
    args = parser.parse_args()

    print("\n🤖 Binance Futures Testnet Trading Bot")
    print("─" * 40)

    success = execute_order(
        symbol=args.symbol,
        side=args.side,
        order_type=args.order_type,
        quantity=args.quantity,
        price=args.price,
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
