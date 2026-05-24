"""CoinMarketCap data provider."""
import requests
import os
from typing import Dict, Any

CMC_BASE_URL = "https://pro-api.coinmarketcap.com/v2"
CMC_API_KEY = os.getenv("COINMARKETCAP_API_KEY", "")


def get_crypto_quotes(symbol: str) -> Dict[str, Any]:
    """Fetch real-time crypto quotes"""
    url = f"{CMC_BASE_URL}/cryptocurrency/quotes/latest"
    headers = {"X-CMC_PRO_API_KEY": CMC_API_KEY}
    params = {"symbol": symbol.split("-")[0]}  # BTC-USD -> BTC

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()["data"][params["symbol"]][0]

    return {
        "price": data["quote"]["USD"]["price"],
        "volume_24h": data["quote"]["USD"]["volume_24h"],
        "volume_change_24h": data["quote"]["USD"]["volume_change_24h"],
        "percent_change_1h": data["quote"]["USD"]["percent_change_1h"],
        "percent_change_24h": data["quote"]["USD"]["percent_change_24h"],
        "percent_change_7d": data["quote"]["USD"]["percent_change_7d"],
        "market_cap": data["quote"]["USD"]["market_cap"],
        "market_cap_dominance": data["quote"]["USD"]["market_cap_dominance"],
        "circulating_supply": data["circulating_supply"],
        "total_supply": data["total_supply"],
    }
