import pandas as pd

from .config import screening_data
from .emails import write_email
from .stockData import StockData


class StockScreener:

    def __init__(self, stock_data, is_stock_screener_child: bool = False):
        self.stock_data = stock_data
        self.index = stock_data.index
        self.tickers = stock_data.tickers
        self.screening_data = screening_data
        self.is_stock_screener_child = is_stock_screener_child
        self.discard_reasons = {}
        self.summary = ""
        self.summary_body = ""

        self.collect_data()

    def collect_data(self):
        for key, value in self.screening_data.items():
            value.set_data(self.tickers)

    def continuous_screen(self, screen_information):
        self.screen_information = screen_information
        self.selected_tickers = self.tickers
        self.tickers_without_data = {}

        for info_key, info_value in self.screen_information.items():
            new_stock_data = StockData(self.index, self.selected_tickers)

            stock_screener = StockScreener(
                new_stock_data, is_stock_screener_child=True)

            new_screen_information = {info_key: info_value}
            stock_screener.screen(screen_information=new_screen_information)

            self.summary_body += stock_screener.summary_body

            self.selected_tickers = stock_screener.selected_tickers

            for key, value in stock_screener.tickers_without_data.items():
                self.tickers_without_data[key] = value

        self._finalize_summary()

    def screen(self, screen_information):
        self.screen_information = screen_information
        self.selected_tickers = {}
        self.tickers_without_data = {}

        for info in self.screen_information:
            self.discard_reasons[info + '_lower_limit'] = 0
            self.discard_reasons[info + '_upper_limit'] = 0

        for company in self.tickers:
            self.to_discard = False
            self.missing_data = False

            for info in self.screen_information:
                self._screen(company, self.screening_data[info].data,
                             info, self.screening_data['sector'].data[company])

            if not self.to_discard:
                self.selected_tickers[company] = self.tickers[company]

            if self.missing_data:
                self.tickers_without_data[company] = self.tickers[company]

        for reason in self.discard_reasons:
            short_reason = reason.split('_')[0]
            self.summary_body += f"{reason}     {self.discard_reasons[reason]} with limits [{self.screen_information[short_reason][0]}, {self.screen_information[short_reason][1]}]\n"

        self._finalize_summary()

    def _finalize_summary(self):
        if not self.is_stock_screener_child:
            self.summary += f"""
A total of {len(self.selected_tickers)} out of {len(self.tickers)} companies were selected.
For a total of {len(self.tickers_without_data)} companies, data was missing.

A short summary of the reasons for discarding companies is given below:

"""
            self.summary += self.summary_body

    def _screen(self, company, data, key, sector=None):
        if sector == 'Financial Services' and key == 'ebitdaMargin':
            return

        lower_limit = self.screen_information[key][0]
        upper_limit = self.screen_information[key][1]

        if key not in self.screen_information:
            return

        if data[company] is None:
            self.to_discard = True
            self.missing_data = True
            return

        if lower_limit is not None and float(data[company]) < self.screen_information[key][0]:
            self.to_discard = True
            self.discard_reasons[key + '_lower_limit'] += 1

        if upper_limit is not None and float(data[company]) > self.screen_information[key][1]:
            self.to_discard = True
            self.discard_reasons[key + '_upper_limit'] += 1

    def write_email(self, email_addresses=None):
        dictionary = {}
        for info, data in self.screening_data.items():
            dictionary[data.title] = {
                ticker: data.data[ticker] for ticker in self.selected_tickers}

        df = pd.DataFrame.from_dict(dictionary)
        df = df.sort_values(
            by=['Sector', 'Market Cap (B)'], ascending=[True, False])

        self.output_file = "selected_companies.csv"
        df.to_csv(self.output_file, sep='\t', encoding='utf-8', )

        if email_addresses is not None:
            receiver_emails = email_addresses
        else:
            raise ValueError("No email addresses given")

        body = self.summary
        attachment = self.output_file

        subject = f"Financial Data for {self.index} of {pd.Timestamp.today().strftime('%Y-%m-%d')}"

        write_email(email_addresses=receiver_emails, email_body=body, email_subject=subject,
                    email_attachment=attachment)
