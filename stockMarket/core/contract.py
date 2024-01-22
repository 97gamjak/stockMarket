from __future__ import annotations

from dataclasses import dataclass, field

from .financialStatement import Income, BalanceSheet, CashFlowStatement


@dataclass(kw_only=True)
class Contract:
    ticker: str
    income: Income = field(default_factory=Income)
    balance: BalanceSheet = field(default_factory=BalanceSheet)
    cashflow: CashFlowStatement = field(default_factory=CashFlowStatement)
