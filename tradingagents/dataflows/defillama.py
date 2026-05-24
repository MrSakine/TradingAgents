"""DeFiLlama data provider for DeFi protocols."""
import requests
from typing import Dict, Any

DEFILLAMA_BASE_URL = "https://api.llama.fi"


def get_protocol_tvl(protocol: str) -> Dict[str, Any]:
    """Fetch Total Value Locked for DeFi protocol"""
    url = f"{DEFILLAMA_BASE_URL}/protocol/{protocol}"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    return {
        "name": data["name"],
        "symbol": data.get("symbol", ""),
        "tvl": data["tvl"],
        "chain_tvls": data.get("chainTvls", {}),
        "change_1d": data.get("change_1d", 0),
        "change_7d": data.get("change_7d", 0),
        "mcap": data.get("mcap", 0),
        "fdv": data.get("fdv", 0),
    }


def get_stablecoin_data(stablecoin: str) -> Dict[str, Any]:
    """Fetch stablecoin circulation data"""
    url = f"{DEFILLAMA_BASE_URL}/stablecoin/{stablecoin}"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    return {
        "circulating": data.get("circulating", {}),
        "chains": data.get("chainCirculating", {}),
        "price": data.get("price", 1.0),
    }
