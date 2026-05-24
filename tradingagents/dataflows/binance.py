"""Binance data provider for cryptocurrency market data.

Binance API documentation: https://binance-docs.github.io/apidocs/spot/en/
Free tier available with rate limits (1200 requests/minute for most endpoints)
"""
import requests
import pandas as pd
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import os

BINANCE_BASE_URL = "https://api.binance.com/api/v3"
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY", "")
BINANCE_SECRET_KEY = os.getenv("BINANCE_SECRET_KEY", "")


def _normalize_ticker(ticker: str) -> str:
    """Convert ticker format to Binance symbol format.

    Examples:
        BTC-USD -> BTCUSDT
        ETH-USD -> ETHUSDT
        BTC-USDT -> BTCUSDT
    """
    # Remove common separators
    ticker = ticker.replace("-", "").replace("_", "").upper()

    # If already ends with USDT, return as-is
    if ticker.endswith("USDT"):
        return ticker

    # Replace USD with USDT (Binance standard)
    if ticker.endswith("USD"):
        return ticker[:-3] + "USDT"

    # If no quote currency, assume USDT
    return ticker + "USDT"


def get_binance_ticker_price(ticker: str) -> Dict[str, Any]:
    """Get current ticker price and 24hr statistics.

    Args:
        ticker: Ticker symbol (e.g., BTC-USD, ETH-USD)

    Returns:
        Dictionary with current price, volume, and 24hr statistics
    """
    symbol = _normalize_ticker(ticker)
    url = f"{BINANCE_BASE_URL}/ticker/24hr"
    params = {"symbol": symbol}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        return {
            "symbol": ticker,
            "binance_symbol": symbol,
            "price": float(data["lastPrice"]),
            "price_change_24h": float(data["priceChange"]),
            "price_change_percent_24h": float(data["priceChangePercent"]),
            "high_24h": float(data["highPrice"]),
            "low_24h": float(data["lowPrice"]),
            "volume_24h": float(data["volume"]),
            "quote_volume_24h": float(data["quoteVolume"]),
            "trades_24h": int(data["count"]),
            "open_price": float(data["openPrice"]),
            "weighted_avg_price": float(data["weightedAvgPrice"]),
            "timestamp": datetime.fromtimestamp(data["closeTime"] / 1000).isoformat(),
            "source": "binance"
        }
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400:
            return {"error": f"Invalid symbol: {symbol}. Make sure the trading pair exists on Binance."}
        raise
    except Exception as e:
        return {"error": f"Error fetching Binance ticker: {str(e)}"}


def get_binance_klines(
    ticker: str,
    interval: str = "1d",
    limit: int = 90,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None
) -> Dict[str, Any]:
    """Get historical klines/candlestick data (OHLCV).

    Args:
        ticker: Ticker symbol
        interval: Kline interval (1m, 5m, 15m, 1h, 4h, 1d, 1w, 1M)
        limit: Number of candles to fetch (max 1000)
        start_time: Start time (YYYY-MM-DD)
        end_time: End time (YYYY-MM-DD)

    Returns:
        Dictionary with OHLCV data
    """
    symbol = _normalize_ticker(ticker)
    url = f"{BINANCE_BASE_URL}/klines"

    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": min(limit, 1000)  # Binance max is 1000
    }

    # Convert date strings to timestamps if provided
    if start_time:
        start_dt = datetime.strptime(start_time, "%Y-%m-%d")
        params["startTime"] = int(start_dt.timestamp() * 1000)

    if end_time:
        end_dt = datetime.strptime(end_time, "%Y-%m-%d")
        params["endTime"] = int(end_dt.timestamp() * 1000)

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        # Parse klines data
        df = pd.DataFrame(data, columns=[
            "open_time", "open", "high", "low", "close", "volume",
            "close_time", "quote_volume", "trades", "taker_buy_base",
            "taker_buy_quote", "ignore"
        ])

        # Convert types
        df["date"] = pd.to_datetime(df["open_time"], unit="ms")
        df["open"] = df["open"].astype(float)
        df["high"] = df["high"].astype(float)
        df["low"] = df["low"].astype(float)
        df["close"] = df["close"].astype(float)
        df["volume"] = df["volume"].astype(float)
        df["quote_volume"] = df["quote_volume"].astype(float)
        df["trades"] = df["trades"].astype(int)

        # Select relevant columns
        df = df[["date", "open", "high", "low", "close",
                 "volume", "quote_volume", "trades"]]

        return {
            "symbol": ticker,
            "binance_symbol": symbol,
            "interval": interval,
            "data": df.to_dict("records"),
            "count": len(df),
            "source": "binance"
        }
    except Exception as e:
        return {"error": f"Error fetching Binance klines: {str(e)}"}


def get_binance_orderbook(ticker: str, limit: int = 100) -> Dict[str, Any]:
    """Get current orderbook depth.

    Args:
        ticker: Ticker symbol
        limit: Depth (5, 10, 20, 50, 100, 500, 1000, 5000)

    Returns:
        Dictionary with bids and asks
    """
    symbol = _normalize_ticker(ticker)
    url = f"{BINANCE_BASE_URL}/depth"
    params = {"symbol": symbol, "limit": limit}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        # Parse order book
        bids = [[float(price), float(qty)] for price, qty in data["bids"][:10]]
        asks = [[float(price), float(qty)] for price, qty in data["asks"][:10]]

        return {
            "symbol": ticker,
            "binance_symbol": symbol,
            "best_bid": bids[0][0] if bids else None,
            "best_ask": asks[0][0] if asks else None,
            "spread": asks[0][0] - bids[0][0] if bids and asks else None,
            "spread_percent": ((asks[0][0] - bids[0][0]) / asks[0][0] * 100) if bids and asks else None,
            "bids_top10": bids,
            "asks_top10": asks,
            "total_bids": len(data["bids"]),
            "total_asks": len(data["asks"]),
            "source": "binance"
        }
    except Exception as e:
        return {"error": f"Error fetching Binance orderbook: {str(e)}"}


def get_binance_exchange_info(ticker: Optional[str] = None) -> Dict[str, Any]:
    """Get exchange trading rules and symbol information.

    Args:
        ticker: Optional ticker to get specific symbol info

    Returns:
        Dictionary with exchange/symbol information
    """
    url = f"{BINANCE_BASE_URL}/exchangeInfo"
    params = {}

    if ticker:
        symbol = _normalize_ticker(ticker)
        params["symbol"] = symbol

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if ticker:
            symbols = data.get("symbols", [])
            if symbols:
                symbol_info = symbols[0]
                return {
                    "symbol": ticker,
                    "binance_symbol": symbol_info["symbol"],
                    "status": symbol_info["status"],
                    "base_asset": symbol_info["baseAsset"],
                    "quote_asset": symbol_info["quoteAsset"],
                    "is_spot_trading_allowed": symbol_info.get("isSpotTradingAllowed", False),
                    "is_margin_trading_allowed": symbol_info.get("isMarginTradingAllowed", False),
                    "permissions": symbol_info.get("permissions", []),
                    "source": "binance"
                }

        return {
            "timezone": data.get("timezone"),
            "server_time": datetime.fromtimestamp(data["serverTime"] / 1000).isoformat(),
            "total_symbols": len(data.get("symbols", [])),
            "source": "binance"
        }
    except Exception as e:
        return {"error": f"Error fetching Binance exchange info: {str(e)}"}


def get_binance_trades(ticker: str, limit: int = 100) -> Dict[str, Any]:
    """Get recent trades.

    Args:
        ticker: Ticker symbol
        limit: Number of trades (max 1000)

    Returns:
        Dictionary with recent trades
    """
    symbol = _normalize_ticker(ticker)
    url = f"{BINANCE_BASE_URL}/trades"
    params = {"symbol": symbol, "limit": min(limit, 1000)}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        trades = []
        for trade in data[-20:]:  # Last 20 trades
            trades.append({
                "price": float(trade["price"]),
                "quantity": float(trade["qty"]),
                "time": datetime.fromtimestamp(trade["time"] / 1000).isoformat(),
                "is_buyer_maker": trade["isBuyerMaker"]
            })

        return {
            "symbol": ticker,
            "binance_symbol": symbol,
            "recent_trades": trades,
            "total_trades": len(data),
            "source": "binance"
        }
    except Exception as e:
        return {"error": f"Error fetching Binance trades: {str(e)}"}


# Wrapper functions for interface integration

def get_crypto_price_data_binance(ticker: str, days: int = 90) -> Dict[str, Any]:
    """Get crypto OHLCV data from Binance."""
    return get_binance_klines(ticker, interval="1d", limit=days)


def get_crypto_fundamentals_binance(ticker: str) -> Dict[str, Any]:
    """Get crypto market metrics from Binance."""
    ticker_data = get_binance_ticker_price(ticker)
    exchange_info = get_binance_exchange_info(ticker)

    if "error" in ticker_data:
        return ticker_data

    return {
        **ticker_data,
        "exchange_info": exchange_info,
        "source": "binance"
    }


def get_binance_market_depth_metrics(ticker: str) -> Dict[str, Any]:
    """Get market depth and liquidity metrics."""
    orderbook = get_binance_orderbook(ticker, limit=100)
    trades = get_binance_trades(ticker, limit=100)

    if "error" in orderbook:
        return orderbook

    return {
        **orderbook,
        "recent_trades_summary": {
            "count": trades.get("total_trades", 0),
            "sample": trades.get("recent_trades", [])[:5]
        },
        "source": "binance"
    }
