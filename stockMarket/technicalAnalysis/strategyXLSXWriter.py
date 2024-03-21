import pandas as pd

from openpyxl import load_workbook
from beartype.typing import Dict, List, Optional

from .trade import Trade, TradeOutcome, TradeSettings


class StrategyXLSXWriter:
    def __init__(self,
                 template_xlsx_filename: str,
                 xlsx_filename: str,
                 trade_settings: TradeSettings,
                 start_date: pd.Timestamp,
                 end_date: pd.Timestamp,
                 batch_size: pd.Timedelta,
                 ) -> None:

        self.template_xlsx_filename = template_xlsx_filename
        self.xlsx_filename = xlsx_filename
        self.trade_settings = trade_settings
        self.start_date = start_date
        self.end_date = end_date
        self.batch_size = batch_size

    def write_xlsx_file(self,
                        trades: Dict[str, List[Trade]],
                        earnings_calendar: Dict[str, pd.Timestamp] = {}
                        ) -> None:

        start_date = self.start_date
        while True:
            end_date = start_date + self.batch_size

            # this way no only one fotal screening file is created
            if start_date == self.start_date and end_date > self.end_date:
                break

            self.write_single_xlsx_file(
                trades,
                earnings_calendar,
                start_date,
                end_date
            )

            start_date = end_date

            if start_date >= self.end_date:
                break

        self.write_single_xlsx_file(
            trades,
            earnings_calendar,
            filename=self.xlsx_filename.split(".")[0] + "_total.xlsx"
        )

    def write_single_xlsx_file(self,
                               trades: Dict[str, List[Trade]],
                               earnings_calendar: Dict[str, pd.Timestamp] = {},
                               start_date: pd.Timestamp = None,
                               end_date: pd.Timestamp = None,
                               filename: Optional[str] = None,
                               ) -> None:

        self.xlsx_file = load_workbook(self.template_xlsx_filename)

        self.write_all_possible_trades(
            trades,
            earnings_calendar,
            start_date,
            end_date
        )
        self.write_analytics_to_xlsx(
            trades,
            start_date,
            end_date
        )
        self.write_trade_settings_to_xlsx(
            start_date,
            end_date
        )

        if filename is None:
            xlsx_filename = self.xlsx_filename.split(".")[0] + \
                "_" + date_to_string(start_date) + "_"

            if end_date > self.end_date:
                xlsx_filename += date_to_string(self.end_date) + ".xlsx"
            else:
                xlsx_filename += date_to_string(end_date -
                                                pd.Timedelta(days=1)) + ".xlsx"
        else:
            xlsx_filename = filename

        self.xlsx_file.save(xlsx_filename)

    def write_all_possible_trades(self,
                                  trades: Dict[str, List[Trade]],
                                  earnings_calendar: Dict[str,
                                                          List[pd.Timestamp]] = {},
                                  start_date: pd.Timestamp = None,
                                  end_date: pd.Timestamp = None
                                  ) -> None:

        xlsx_sheet = self.xlsx_file["stocks"]
        headers = list(pd.read_excel(
            self.template_xlsx_filename, sheet_name="stocks").iloc[0])

        row = 3

        for trades in trades.values():
            for trade in trades:
                if not check_is_within_date_range(trade.TC_date, start_date, end_date):
                    continue

                TICKER = trade.ticker
                TICKER_index = header_index(headers, "Ticker")

                TC_date = trade.TC_date
                TC_date_index = header_index(headers, "Entry Candle")

                ENTRY_date = trade.ENTRY_date
                ENTRY_date_index = header_index(headers, "Entry Date")
                ENTRY = trade.ENTRY
                ENTRY_index = header_index(headers, "Entry")
                R_ENTRY = trade.R_ENTRY
                R_ENTRY_index = header_index(headers, "Real Entry")

                SL = trade.SL
                SL_index = header_index(headers, "Stop Loss")

                TP_date = trade.TP_date
                TP_date_index = header_index(headers, "Target Date")
                TP = trade.TP
                TP_index = header_index(headers, "Target")

                EXIT_date = trade.EXIT_date
                EXIT_date_index = header_index(headers, "Exit Date")
                EXIT = trade.EXIT
                EXIT_index = header_index(headers, "Exit")

                STATUS = trade.trade_status.value
                STATUS_index = header_index(headers, "Status")

                EARNINGS_index = header_index(headers, "Days to Earnings")

                #fmt: off
                xlsx_sheet.cell(row=row, column=TICKER_index).value = TICKER
                xlsx_sheet.cell(row=row, column=TC_date_index).value = TC_date
                xlsx_sheet.cell(row=row, column=ENTRY_date_index).value = ENTRY_date
                xlsx_sheet.cell(row=row, column=ENTRY_index).value = ENTRY
                xlsx_sheet.cell(row=row, column=R_ENTRY_index).value = R_ENTRY

                xlsx_sheet.cell(row=row, column=SL_index).value = SL
                xlsx_sheet.cell(row=row, column=TP_date_index).value = TP_date
                xlsx_sheet.cell(row=row, column=TP_index).value = TP
                xlsx_sheet.cell(row=row, column=EXIT_date_index).value = EXIT_date
                xlsx_sheet.cell(row=row, column=EXIT_index).value = EXIT

                xlsx_sheet.cell(row=row, column=STATUS_index).value = STATUS

                if earnings_calendar != {}:
                    _, days_until_earnings = self.find_next_earnings_date(
                        trade.candle_date,
                        earnings_calendar[trade.ticker]
                    )[1]

                    xlsx_sheet.cell(row=row, column=EARNINGS_index).value = days_until_earnings

                #fmt: on

                row += 1

    def find_next_earnings_date(self,
                                date: pd.Timestamp,
                                earnings_dates: List[pd.Timestamp],
                                ):
        date = pd.Timestamp(date).date()
        for earnings_date in earnings_dates:
            if earnings_date > date:
                return earnings_date, (earnings_date - date).days
        return "No earnings date found", None

    def write_analytics_to_xlsx(self,
                                trades: Dict[str, List[Trade]],
                                start_date: pd.Timestamp,
                                end_date: pd.Timestamp
                                ):

        xlsx_sheet = self.xlsx_file["analytics"]
        headers = list(pd.read_excel(
            self.template_xlsx_filename, sheet_name="analytics").iloc[0])

        row = 3

        for trades in trades.values():
            for trade in trades:
                if not check_is_within_date_range(trade.TC_date, start_date, end_date):
                    continue

                TICKER = trade.ticker
                TICKER_index = header_index(headers, "Ticker")

                xlsx_sheet.cell(row=row, column=TICKER_index).value = TICKER

                if trade.outcome != TradeOutcome.WIN and trade.outcome != TradeOutcome.LOSS:
                    row += 1
                    continue

                #fmt: off
                SL = trade.ENTRY - trade.SL
                SL_index = header_index(headers, "Stop Loss")
                SL_REAL = trade.R_ENTRY - trade.SL
                SL_REAL_index = header_index(headers, "Stop Loss Real")

                TP = trade.TP - trade.ENTRY
                TP_index = header_index(headers, "Target")
                TP_REAL = trade.TP - trade.R_ENTRY
                TP_REAL_index = header_index(headers, "Target Real")

                PL = TP / SL
                PL_index = header_index(headers, "P/L")
                PL_REAL = TP_REAL / SL_REAL
                PL_REAL_index = header_index(headers, "P/L Real")

                WL = "W" if trade.outcome == TradeOutcome.WIN else "L"
                WL_index = header_index(headers, "W/L")

                SHARES_TO_BUY = 1 / SL
                SHARES_TO_BUY_index = header_index(headers, "Shares 2 Buy")

                PRED_INVEST = trade.ENTRY / SL
                PRED_INVEST_index = header_index(headers, "Predicted Investment")
                INVEST = trade.INVESTMENT
                INVEST_index = header_index(headers, "Investment")
                DELTA_INVEST = INVEST - PRED_INVEST
                DELTA_INVEST_index = header_index(headers, "Delta Investment")

                PRED_OUTCOME = (trade.EXIT - trade.ENTRY) / SL
                PRE_OUTCOME_index = header_index(headers, "Predicted Outcome")
                OUTCOME = (trade.EXIT - trade.R_ENTRY) / SL
                OUTCOME_index = header_index(headers, "Outcome")

                TOTAL_DAYS = (trade.EXIT_date - trade.ENTRY_date).days + 1
                TOTAL_DAYS_index = header_index(headers, "Total Days")
                REQ_CAPITAL = INVEST * TOTAL_DAYS
                REQ_CAPITAL_index = header_index(headers, "Required Capital")


                xlsx_sheet.cell(row=row, column=SL_index).value = SL
                xlsx_sheet.cell(row=row, column=SL_REAL_index).value = SL_REAL
                xlsx_sheet.cell(row=row, column=TP_index).value = TP
                xlsx_sheet.cell(row=row, column=TP_REAL_index).value = TP_REAL
                xlsx_sheet.cell(row=row, column=PL_index).value = PL
                xlsx_sheet.cell(row=row, column=PL_REAL_index).value = PL_REAL

                xlsx_sheet.cell(row=row, column=WL_index).value = WL

                xlsx_sheet.cell(row=row, column=SHARES_TO_BUY_index).value = SHARES_TO_BUY
                xlsx_sheet.cell(row=row, column=PRED_INVEST_index).value = PRED_INVEST
                xlsx_sheet.cell(row=row, column=INVEST_index).value = INVEST
                xlsx_sheet.cell(row=row, column=DELTA_INVEST_index).value = DELTA_INVEST

                xlsx_sheet.cell(row=row, column=PRE_OUTCOME_index).value = PRED_OUTCOME
                xlsx_sheet.cell(row=row, column=OUTCOME_index).value = OUTCOME
                xlsx_sheet.cell(row=row, column=TOTAL_DAYS_index).value = TOTAL_DAYS
                xlsx_sheet.cell(row=row, column=REQ_CAPITAL_index).value = REQ_CAPITAL

                #fmt: on
                row += 1

    def write_trade_settings_to_xlsx(self,
                                     start_date: pd.Timestamp = None,
                                     end_date: pd.Timestamp = None,
                                     ):
        xlsx_sheet = self.xlsx_file["overview"]

        if start_date is None:
            start_date = self.start_date
        if end_date is None:
            end_date = self.end_date

        xlsx_sheet.cell(row=1, column=1).value = "Start Date"
        xlsx_sheet.cell(row=1, column=2).value = start_date
        xlsx_sheet.cell(row=2, column=1).value = "End Date"
        xlsx_sheet.cell(row=2, column=2).value = end_date

        row = 4

        for key, value in self.trade_settings.to_json().items():
            xlsx_sheet.cell(row=row, column=1).value = key
            xlsx_sheet.cell(row=row, column=2).value = value

            row += 1


def header_index(headers: List[str], header: str):
    headers = [header.lower().strip() for header in headers]
    return headers.index(header.lower()) + 1


def date_to_string(date: pd.Timestamp):
    return date.strftime("%d%m%Y")


def check_is_within_date_range(date: pd.Timestamp, start_date: pd.Timestamp, end_date: pd.Timestamp):
    if start_date is None:
        return True

    return start_date <= date < end_date
