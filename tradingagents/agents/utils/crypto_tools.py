"""Crypto-specific agent tools."""
from langchain_core.tools import tool
from typing import Annotated


@tool
def get_crypto_fundamentals(
    ticker: Annotated[str, "Crypto ticker symbol (e.g., BTC-USD, ETH-USD)"]
) -> str:
    """Get fundamental metrics for cryptocurrency including market cap, supply, ATH, etc."""
    from tradingagents.dataflows.interface import route_to_vendor
    try:
        return route_to_vendor("get_crypto_fundamentals", ticker)
    except Exception as e:
        return f"Error fetching crypto fundamentals: {str(e)}"


@tool
def get_defi_metrics(
    ticker: Annotated[str, "DeFi protocol or token ticker"]
) -> str:
    """Get DeFi metrics including TVL, TVL ratios, protocol statistics."""
    from tradingagents.dataflows.interface import route_to_vendor
    try:
        return route_to_vendor("get_defi_metrics", ticker)
    except Exception as e:
        return f"Error fetching DeFi metrics: {str(e)}"


@tool
def get_stablecoin_metrics(
    ticker: Annotated[str,
                      "Stablecoin ticker (e.g., USDT-USD, USDC-USD, DAI-USD)"]
) -> str:
    """Get stablecoin-specific metrics including peg deviation, collateralization, circulation."""
    from tradingagents.dataflows.interface import route_to_vendor
    try:
        return route_to_vendor("get_stablecoin_metrics", ticker)
    except Exception as e:
        return f"Error fetching stablecoin metrics: {str(e)}"


@tool
def get_memecoin_social_metrics(
    ticker: Annotated[str,
                      "Memecoin ticker (e.g., DOGE-USD, SHIB-USD, PEPE-USD)"]
) -> str:
    """Get social metrics for memecoins: Twitter, Telegram, Reddit activity, sentiment."""
    from tradingagents.dataflows.interface import route_to_vendor
    try:
        return route_to_vendor("get_memecoin_social_metrics", ticker)
    except Exception as e:
        return f"Error fetching memecoin social metrics: {str(e)}"


@tool
def get_crypto_on_chain_metrics(
    ticker: Annotated[str, "Crypto ticker"]
) -> str:
    """Get on-chain metrics: active addresses, transaction volume, network hash rate."""
    from tradingagents.dataflows.interface import route_to_vendor
    try:
        return route_to_vendor("get_crypto_on_chain_metrics", ticker)
    except Exception as e:
        return f"Error fetching on-chain metrics: {str(e)}"
