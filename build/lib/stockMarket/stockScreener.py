import pandas as pd

from tqdm import tqdm

from .config import screening_data
from .emails import write_email


class StockScreener:

    def __init__(self, stock_data):
        self.stock_data = stock_data
        self.index = stock_data.index
        self.tickers = stock_data.tickers
        self.screening_data = screening_data

        self.collect_data()

    def collect_data(self):
        for key, value in tqdm(self.screening_data.items()):
            value.set_data(self.tickers)

    def screen(self, screen_information):
        self.screen_information = screen_information
        self.selected_tickers = {}
        self.tickers_without_data = {}

        self.discard_reasons = {}
        for info in self.screen_information:
            self.discard_reasons[info + '_lower_limit'] = 0
            self.discard_reasons[info + '_upper_limit'] = 0

        print()
        print("Removing companies that do not meet the screening criteria...")
        print()
        for company in tqdm(self.tickers):
            self.to_discard = False
            self.missing_data = False

            for info in self.screen_information:
                self._screen(company, self.screening_data[info].data,
                             info, self.screening_data['sector'].data[company])

            if not self.to_discard:
                self.selected_tickers[company] = self.tickers[company]

            if self.missing_data:
                self.tickers_without_data[company] = self.tickers[company]

        return self._finalize_screen()

    def _finalize_screen(self):

        self.summary = f"""
A total of {len(self.selected_tickers)} out of {len(self.tickers)} companies were selected.
For a total of {len(self.tickers_without_data)} companies, data was missing.

A short summary of the reasons for discarding companies is given below:

"""

        for reason in self.discard_reasons:
            short_reason = reason.split('_')[0]
            self.summary += f"{reason}     {self.discard_reasons[reason]} with limits [{
                self.screen_information[short_reason][0]}{self.screen_information[short_reason][1]}]\n"

        self.summary += """
        
The selected companies are:
            
"""

        dictionary = {}
        for info, data in self.screening_data.items():
            dictionary[data.title] = {
                ticker: data.data[ticker] for ticker in self.selected_tickers}

        df = pd.DataFrame.from_dict(dictionary)
        df = df.sort_values(
            by=['Sector', 'EBITDA Margin %'], ascending=[True, False])

        self.output_file = "selected_companies.csv"
        df.to_csv(self.output_file, sep='\t', encoding='utf-8', )

        print(self.summary)
        print(df)

        return self.selected_tickers

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

    def screen_lower_limit_ebitda_margin(self, company, data, key, sector):
        if sector != 'Financial Services':
            self.screen_lower_limit(company, data, key)

    def write_email(self, email_addresses=None):
        if email_addresses is not None:
            receiver_emails = email_addresses
        else:
            raise ValueError("No email addresses given")

        body = self.summary
        attachment = self.output_file

        subject = f"Financial Data for {self.index} of {
            pd.Timestamp.today().strftime('%Y-%m-%d')}"

        write_email(email_addresses=receiver_emails, email_body=body, email_subject=subject,
                    email_attachment=attachment)
