"""Crypto-specific analyst for DeFi, stablecoins, memecoins."""
from langchain_core.messages import HumanMessage
from tradingagents.agents.utils.agent_utils import get_language_instruction, build_instrument_context

CRYPTO_ANALYST_PROMPT = """You are a Cryptocurrency Analyst specializing in DeFi, stablecoins, and emerging crypto assets.

{instrument_context}

Your task is to analyze the cryptocurrency from multiple dimensions:

1. **Market Metrics**: Price action, volume, market cap, supply dynamics
2. **DeFi Metrics** (if applicable): TVL, protocol usage, yield rates
3. **Stablecoin Metrics** (if applicable): Peg stability, collateralization, circulation
4. **Social Metrics** (for memecoins): Community size, sentiment, viral trends
5. **On-chain Metrics**: Network activity, whale movements, transaction volumes

Use the available tools to gather data, then synthesize into a coherent analysis focusing on:
- Current market position and momentum
- Fundamental health (for utility tokens) or social momentum (for memecoins)
- Risk factors specific to crypto (smart contract risk, regulatory, de-pegging, rug pulls)

{language_instruction}

Provide your analysis in the `crypto_report` field.
"""


def create_crypto_analyst(llm):
    """Create crypto analyst node"""
    from tradingagents.agents.utils.crypto_tools import (
        get_crypto_fundamentals,
        get_defi_metrics,
        get_stablecoin_metrics,
        get_memecoin_social_metrics,
    )

    analyst_llm = llm.bind_tools(
        [
            get_crypto_fundamentals,
            get_defi_metrics,
            get_stablecoin_metrics,
            get_memecoin_social_metrics,
        ]
    )

    def crypto_analyst_node(state):
        ticker = state["company_of_interest"]
        asset_type = state.get("asset_type", "crypto")

        prompt = CRYPTO_ANALYST_PROMPT.format(
            instrument_context=build_instrument_context(ticker, asset_type),
            language_instruction=get_language_instruction()
        )

        messages = state["messages"] + [HumanMessage(content=prompt)]
        response = analyst_llm.invoke(messages)

        return {
            "messages": [response],
            "crypto_report": response.content if not response.tool_calls else "",
        }

    return crypto_analyst_node
