from tqdm import tqdm
import datetime
import pandas as pd

from .config import screening_data
from .emails import write_email


class EarningDates:
    def __init__(self, tickers):
        self.tickers = tickers

    def screen(self):

        self.long_names = screening_data['longName']
        self.long_names.set_data(self.tickers)

        self.sectors = screening_data['sector']
        self.sectors.set_data(self.tickers)

        self.market_caps = screening_data['marketCap']
        self.market_caps.set_data(self.tickers)

        self.get_earning_dates()

        self.combine_data()

        return self.data

    def get_earning_dates(self):
        self.dates = {}
        for ticker in tqdm(self.tickers):
            try:
                self.dates[ticker] = self.tickers[ticker].calendar['Earnings Date']
            except KeyError:
                self.dates[ticker] = None

        last_saturday = pd.Timestamp(self.find_last_saturday())
        next_friday = pd.Timestamp(self.find_next_friday())
        self.nearest_earnings = {}
        for ticker, date in self.dates.items():
            date = date
            if date is None or len(date) == 0:
                continue

            date = [pd.Timestamp(_date) for _date in date]
            if last_saturday <= date[0] <= next_friday:
                start_date = date[0].date()
                end_date = date[1].date() if len(date) > 1 else start_date
                self.nearest_earnings[ticker] = [start_date, end_date]

    def combine_data(self):
        self.data = {}
        for ticker in self.nearest_earnings:
            self.data[ticker] = {}
            self.data[ticker]['Name'] = self.long_names.data[ticker]
            self.data[ticker]['Sector'] = self.sectors.data[ticker]
            self.data[ticker]['Market Cap (B)'] = self.market_caps.data[ticker]
            start_date = self.nearest_earnings[ticker][0]
            end_date = self.nearest_earnings[ticker][1]

            self.data[ticker]['Start Date'] = start_date
            if start_date != end_date:
                self.data[ticker]['End Date'] = end_date

        self.data = pd.DataFrame(self.data).transpose()
        self.data = self.data.sort_values(
            by=['Start Date', 'Sector', 'Market Cap (B)'], ascending=[True, True, False])

        self.output_file = "earning_dates.csv"
        self.data.to_csv(self.output_file, sep='\t', encoding='utf-8', )

    def write_email(self, email_addresses=None):
        if email_addresses is not None:
            receiver_emails = email_addresses
        else:
            raise ValueError("No email addresses given")

        body = ""
        attachment = self.output_file

        subject = f"Next Important Earning Dates from {
            pd.Timestamp.today().strftime('%Y-%m-%d')}"

        write_email(email_addresses=receiver_emails, email_body=body, email_subject=subject,
                    email_attachment=attachment)

    def find_next_friday(self):
        today = datetime.date.today()
        next_friday = today + datetime.timedelta((4-today.weekday()) % 7)
        return next_friday

    def find_last_saturday(self):
        today = datetime.date.today()
        last_saturday = today - datetime.timedelta((today.weekday()+2) % 7)
        return last_saturday
