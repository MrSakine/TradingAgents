"""CoinGecko data provider for crypto assets."""
import requests
from typing import Dict, Any, Optional
import pandas as pd
from datetime import datetime, timedelta

COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"


def get_crypto_price_data(symbol: str, days: int = 90) -> Dict[str, Any]:
    """Fetch crypto OHLCV data from CoinGecko

    Args:
        symbol: Crypto ticker (e.g., "BTC-USD", "ETH-USD")
        days: Historical days to fetch
    """
    # Convert ticker format (BTC-USD -> bitcoin)
    coin_id = _symbol_to_coingecko_id(symbol)

    url = f"{COINGECKO_BASE_URL}/coins/{coin_id}/market_chart"
    params = {
        "vs_currency": "usd",
        "days": days,
        "interval": "daily"
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    # Format as DataFrame
    df = pd.DataFrame({
        "timestamp": [item[0] for item in data["prices"]],
        "close": [item[1] for item in data["prices"]],
        "volume": [item[1] for item in data["total_volumes"]],
        "market_cap": [item[1] for item in data["market_caps"]],
    })
    df["date"] = pd.to_datetime(df["timestamp"], unit="ms")

    return {
        "data": df.to_dict("records"),
        "symbol": symbol,
        "source": "coingecko"
    }


def get_crypto_fundamentals(symbol: str) -> Dict[str, Any]:
    """Fetch crypto fundamental metrics"""
    coin_id = _symbol_to_coingecko_id(symbol)

    url = f"{COINGECKO_BASE_URL}/coins/{coin_id}"
    params = {
        "localization": "false",
        "tickers": "false",
        "community_data": "true",
        "developer_data": "true"
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    return {
        "market_cap": data["market_data"]["market_cap"]["usd"],
        "total_volume_24h": data["market_data"]["total_volume"]["usd"],
        "circulating_supply": data["market_data"]["circulating_supply"],
        "total_supply": data["market_data"]["total_supply"],
        "max_supply": data["market_data"]["max_supply"],
        "ath": data["market_data"]["ath"]["usd"],
        "ath_date": data["market_data"]["ath_date"]["usd"],
        "price_change_24h": data["market_data"]["price_change_percentage_24h"],
        "price_change_7d": data["market_data"]["price_change_percentage_7d"],
        "price_change_30d": data["market_data"]["price_change_percentage_30d"],
        "market_cap_rank": data["market_cap_rank"],
        # Community metrics
        "twitter_followers": data.get("community_data", {}).get("twitter_followers", 0),
        "reddit_subscribers": data.get("community_data", {}).get("reddit_subscribers", 0),
        # Developer metrics
        "github_stars": data.get("developer_data", {}).get("stars", 0),
        "github_forks": data.get("developer_data", {}).get("forks", 0),
    }


def get_defi_metrics(symbol: str) -> Dict[str, Any]:
    """Fetch DeFi-specific metrics"""
    coin_id = _symbol_to_coingecko_id(symbol)

    url = f"{COINGECKO_BASE_URL}/coins/{coin_id}"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    return {
        "total_value_locked": data.get("market_data", {}).get("total_value_locked", {}),
        "fdv_to_tvl_ratio": data.get("market_data", {}).get("fdv_to_tvl_ratio"),
        "mcap_to_tvl_ratio": data.get("market_data", {}).get("mcap_to_tvl_ratio"),
    }


def get_stablecoin_metrics(symbol: str) -> Dict[str, Any]:
    """Fetch stablecoin-specific metrics (peg deviation, collateral)"""
    coin_id = _symbol_to_coingecko_id(symbol)

    url = f"{COINGECKO_BASE_URL}/coins/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": 7}

    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    # Calculate peg deviation
    prices = [item[1] for item in data["prices"]]
    avg_price = sum(prices) / len(prices)
    max_deviation = max(abs(p - 1.0) for p in prices)

    return {
        "avg_price_7d": avg_price,
        "max_peg_deviation_7d": max_deviation,
        "current_price": prices[-1],
        "is_pegged": abs(prices[-1] - 1.0) < 0.01,  # Within 1% of $1
    }


def get_memecoin_social_metrics(symbol: str) -> Dict[str, Any]:
    """Fetch social metrics for memecoins"""
    coin_id = _symbol_to_coingecko_id(symbol)

    url = f"{COINGECKO_BASE_URL}/coins/{coin_id}"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    community = data.get("community_data", {})

    return {
        "twitter_followers": community.get("twitter_followers", 0),
        "telegram_users": community.get("telegram_channel_user_count", 0),
        "reddit_subscribers": community.get("reddit_subscribers", 0),
        "reddit_active_users": community.get("reddit_accounts_active_48h", 0),
        "alexa_rank": data.get("public_interest_stats", {}).get("alexa_rank"),
        "sentiment_votes_up": data.get("sentiment_votes_up_percentage", 0),
        "sentiment_votes_down": data.get("sentiment_votes_down_percentage", 0),
    }


def _symbol_to_coingecko_id(symbol: str) -> str:
    """Convert ticker symbol to CoinGecko ID"""
    mapping = {
        "BTC-USD": "bitcoin",
        "ETH-USD": "ethereum",
        "USDT-USD": "tether",
        "USDC-USD": "usd-coin",
        "DAI-USD": "dai",
        "DOGE-USD": "dogecoin",
        "SHIB-USD": "shiba-inu",
        "PEPE-USD": "pepe",
        # Add more mappings
    }

    # If exact match, use it
    if symbol in mapping:
        return mapping[symbol]

    # Try to extract base symbol (BTC-USD -> BTC)
    base = symbol.split("-")[0].lower()

    # API call to search for ID
    search_url = f"{COINGECKO_BASE_URL}/search"
    params = {"query": base}
    response = requests.get(search_url, params=params)

    if response.ok:
        results = response.json().get("coins", [])
        if results:
            return results[0]["id"]

    # Fallback
    return base
