from __future__ import annotations

import datetime as dt

from tvDatafeed import Interval


class Period:
    def __init__(self, period: str | Period):
        if isinstance(period, str):
            self.period_string = period

            if period == "daily":
                self.period_time = dt.timedelta(days=1)
                self.interval = Interval.in_daily
            elif period == "weekly":
                self.period_time = dt.timedelta(days=7)
                self.interval = Interval.in_weekly
            elif period == "monthly":
                self.period_time = dt.timedelta(days=30)
                self.interval = Interval.in_monthly
            elif period == "annual":
                self.period_time = dt.timedelta(days=365)
                self.interval = None
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
