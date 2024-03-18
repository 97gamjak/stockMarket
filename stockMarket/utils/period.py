from __future__ import annotations

import datetime as dt

from tvDatafeed import Interval


class Period:
    def __init__(self, period: str | Period, amount: int = 1):
        self.amount = amount
        if isinstance(period, str):
            self.period_string = period

            if period == "daily":
                self.period_time = dt.timedelta(days=1) * self.amount
                self.interval = Interval.in_daily
                self.yf_interval = "1d"
            elif period == "weekly":
                self.period_time = dt.timedelta(days=7) * self.amount
                self.interval = Interval.in_weekly
                self.yf_interval = "1wk"
            elif period == "monthly":
                self.period_time = dt.timedelta(days=30) * self.amount
                self.interval = Interval.in_monthly
                self.yf_interval = "1mo"
            elif period == "annual":
                self.period_time = dt.timedelta(days=365) * self.amount
                self.interval = "yearly"
                self.yf_interval = "1y"
            elif period == "now":
                self.period_time = None
                self.period_string = None
                self.interval = None
            else:
                raise NotImplementedError(
                    "Only daily, weekly, monthly, annual and now are implemented")

        else:
            self.period_time = period.period_time
            self.period_string = period.period_string
            self.interval = period.interval
