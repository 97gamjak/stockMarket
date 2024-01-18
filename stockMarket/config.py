from __future__ import annotations

from .screeningData import InfoScreener
from .screeningData import CashflowScreener
from .screeningData import FinancialsScreener
from .screeningData import BalancesheetScreener
from .screeningData import RelationToSumScreener
from .screeningData import GrowthScreener
from .screeningData import CalendarScreener
from .screeningData import ThreeYearScreener


screening_data = {}
screening_data["longName"] = InfoScreener(id="longName",
                                          title="Long Name")

screening_data["sector"] = InfoScreener(id="sector",
                                        title="Sector")

screening_data["price"] = InfoScreener(id="open",
                                       title="Price")

screening_data["marketCap"] = InfoScreener(id="marketCap",
                                           title="Market Cap (B)",
                                           multiplier=1/10**9)

screening_data["trailingPE"] = InfoScreener(id="trailingPE",
                                            title="Trailing PE")

screening_data["forwardPE"] = InfoScreener(id="forwardPE",
                                           title="Forward PE")

screening_data["dividendYield"] = InfoScreener(id="dividendYield",
                                               title="Dividend Yield %",
                                               multiplier=100,
                                               exception=0)

screening_data["payoutRatio"] = InfoScreener(id="payoutRatio",
                                             title="Payout Ratio %",
                                             multiplier=100)

screening_data["minNetIncome"] = ThreeYearScreener(id="Net Income",
                                                   title="Lowest Net Income (B)",
                                                   type="financials",
                                                   math_mode="min",
                                                   multiplier=1/10**9)

screening_data["maxNetIncome"] = ThreeYearScreener(id="Net Income",
                                                   title="Highest Net Income (B)",
                                                   type="financials",
                                                   math_mode="max",
                                                   multiplier=1/10**9)


screening_data["revenueGrowth"] = GrowthScreener(id="Total Revenue",
                                                 title="Revenue Growth %",
                                                 type="financials",
                                                 multiplier=100,
                                                 two_years=True)

screening_data["operatingCashflow"] = CashflowScreener(id="Operating Cash Flow",
                                                       title="Operating Cash Flow (B)",
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

screening_data["earningsDate"] = CalendarScreener(id="Earnings Date",
                                                  title="Earnings Date")

screening_data["exDividendDate"] = CalendarScreener(id="Ex-Dividend Date",
                                                    title="Ex-Dividend Date")
