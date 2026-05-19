"""Cobalt Advisory Co-Pilot — mock scenario data.

Reused across every notebook so readers see the same client get
progressively better service as we add layers of the Microsoft AI agents stack.

Nothing here is real. Avery Chen is a synthetic persona; holdings and
prices are illustrative only and must not be used for investment decisions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


@dataclass(frozen=True)
class ClientProfile:
    client_id: str
    name: str
    age: int
    occupation: str
    location: str
    risk_tolerance: str          # conservative | moderate | moderate-aggressive | aggressive
    investment_horizon_years: int
    annual_income_usd: int
    liquid_assets_usd: int
    aum_with_firm_usd: int
    goals: list[str]
    constraints: list[str]
    last_review: date


@dataclass(frozen=True)
class Holding:
    symbol: str
    name: str
    asset_class: str             # equity | fixed_income | etf | cash | alt
    shares: float
    cost_basis_usd: float
    market_value_usd: float


CLIENT_PROFILE = ClientProfile(
    client_id="CA-00471",
    name="Avery Chen",
    age=47,
    occupation="Engineering Director, mid-cap SaaS company",
    location="Seattle, WA",
    risk_tolerance="moderate-aggressive",
    investment_horizon_years=18,
    annual_income_usd=385_000,
    liquid_assets_usd=210_000,
    aum_with_firm_usd=1_420_000,
    goals=[
        "Retire by 65 with $5M portfolio (today's dollars)",
        "Fund two undergraduate degrees starting 2032 and 2034",
        "Maintain 6-month emergency reserve outside brokerage",
    ],
    constraints=[
        "Avoid single-stock concentration > 10% of portfolio",
        "ESG-tilted: exclude tobacco, thermal coal, controversial weapons",
        "Tax-aware: harvest losses, prefer ETFs over mutual funds in taxable",
    ],
    last_review=date(2026, 2, 12),
)


HOLDINGS: list[Holding] = [
    Holding("VTI",  "Vanguard Total Stock Market ETF",       "etf",          1_180.0,  198.40,  290_500.00),
    Holding("VXUS", "Vanguard Total International Stock ETF", "etf",            980.0,   58.10,   62_720.00),
    Holding("BND",  "Vanguard Total Bond Market ETF",         "etf",          1_450.0,   72.95,  103_950.00),
    Holding("MSFT", "Microsoft Corporation",                  "equity",         420.0,  280.10,  198_240.00),
    Holding("AAPL", "Apple Inc.",                             "equity",         540.0,  155.75,  142_560.00),
    Holding("NVDA", "NVIDIA Corporation",                     "equity",         190.0,  410.20,  168_150.00),
    Holding("AVGO", "Broadcom Inc.",                          "equity",          85.0,  812.40,   95_115.00),
    Holding("QQQM", "Invesco NASDAQ 100 ETF",                 "etf",            520.0,  165.20,  118_560.00),
    Holding("SCHD", "Schwab US Dividend Equity ETF",          "etf",            680.0,   76.40,   65_280.00),
    Holding("USFR", "WisdomTree Floating Rate Treasury ETF",  "etf",          1_300.0,   50.20,   65_650.00),
    Holding("CASH", "Sweep cash (USD)",                       "cash",        109_275.0,    1.00,  109_275.00),
]


WATCHLIST = ["AMD", "GOOGL", "META", "TSM", "LIN", "NEE"]


# Inputs the Co-Pilot has access to in later notebooks; introduced here for orientation.
DATA_SOURCES = {
    "research_library":  "PDFs + notes in SharePoint (mocked in earlier notebooks)",
    "market_data":       "Public APIs (yfinance / Yahoo) — read-only",
    "client_email":      "Outlook via Agent 365 Work IQ MCP (notebook #7 only)",
    "client_meetings":   "Teams + Outlook calendar via Agent 365 (notebook #7 only)",
    "compliance_policy": "Firm policy doc in SharePoint via Agent 365 (notebook #7 only)",
}


def portfolio_summary() -> dict:
    """Convenience aggregation for use in any notebook."""
    total_mv = sum(h.market_value_usd for h in HOLDINGS)
    total_cost = sum(h.cost_basis_usd * h.shares if h.symbol != "CASH" else h.market_value_usd for h in HOLDINGS)
    by_class: dict[str, float] = {}
    for h in HOLDINGS:
        by_class[h.asset_class] = by_class.get(h.asset_class, 0.0) + h.market_value_usd
    return {
        "total_market_value_usd": round(total_mv, 2),
        "approx_unrealized_gain_usd": round(total_mv - total_cost, 2),
        "allocation_by_asset_class_pct": {
            k: round(100 * v / total_mv, 2) for k, v in by_class.items()
        },
    }
