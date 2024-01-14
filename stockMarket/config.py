from __future__ import annotations

from .screeningData import InfoScreener, CashflowScreener, FinancialsScreener, BalancesheetScreener, RelationToSumScreener, GrowthScreener


screening_data = {}
screening_data["longName"] = InfoScreener(id="longName",
                                          title="Long Name")

screening_data["sector"] = InfoScreener(id="sector",
                                        title="Sector")

screening_data["dividendYield"] = InfoScreener(id="dividendYield",
                                               title="Dividend Yield %",
                                               multiplier=100,
                                               exception=0)

screening_data["price"] = InfoScreener(id="open",
                                       title="Price")

screening_data["trailingPE"] = InfoScreener(id="trailingPE",
                                            title="Trailing PE")

screening_data["forwardPE"] = InfoScreener(id="forwardPE",
                                           title="Forward PE")

screening_data["revenueGrowth"] = GrowthScreener(id="Total Revenue",
                                                 title="Revenue Growth %",
                                                 type="financials",
                                                 multiplier=100,
                                                 two_years=True)

screening_data["operatingCashflow"] = InfoScreener(id="operatingCashflow",
                                                   title="Operating Cash Flow (B)",
                                                   multiplier=1/10**9)

screening_data["marketCap"] = InfoScreener(id="marketCap",
                                           title="Market Cap (B)",
                                           multiplier=1/10**9)

screening_data["grossMargin"] = InfoScreener(id="grossMargins",
                                             title="Gross Margin %",
                                             multiplier=100)

screening_data["ebitdaMargin"] = InfoScreener(id="ebitdaMargins",
                                              title="EBITDA Margin %",
                                              multiplier=100)

screening_data["equityRatio"] = RelationToSumScreener(type1="balancesheet",
                                                      id1="Common Stock Equity",
                                                      type2="balancesheet",
                                                      id2="Total Debt",
                                                      title="Equity Ratio %",
                                                      multiplier=100)
