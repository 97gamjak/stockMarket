from __future__ import annotations

import datetime as dt


class Period:
    def __init__(self, period: str | Period):
        if isinstance(period, str):
            self.period_string = period

            if period == "daily":
                self.period_time = dt.timedelta(days=1)
            elif period == "weekly":
                self.period_time = dt.timedelta(days=7)
            elif period == "monthly":
                self.period_time = dt.timedelta(days=30)
            elif period == "annual":
                self.period_time = dt.timedelta(days=365)
            elif period == "now":
                self.period_time = None
                self.period_string = None
            else:
                raise NotImplementedError(
                    "Only daily, weekly, monthly, annual and now are implemented")

        else:
            self.period_time = period.period_time
            self.period_string = period.period_string
