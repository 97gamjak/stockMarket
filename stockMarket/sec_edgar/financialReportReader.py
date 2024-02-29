import pandas as pd


class FinancialReportReader:
    def __init__(self, filename):
        self.filename = filename

    def read(self):
        self.read_income()
        self.read_balance()
        self.read_cashflow()

    def read_income(self):
        sheet_name = "Consolidated Statements of Inco"

        df = self._read_sheet(sheet_name)

        key_column = df.columns[0]
        date = self._read_date(df)

        income_keys = {
            "revenue": ["sales", "net sales"],
        }

        bool_array = [str(key).lower() in income_keys["revenue"]
                      for key in df[key_column]]
        value = df[bool_array].values[0][1]
        print(value)

    def read_balance(self):
        sheet_name = "Consolidated Balance Sheets"

        df = self._read_sheet(sheet_name)

        key_column = df.columns[0]
        date = self._read_date(df)

    def read_cashflow(self):
        sheet_name = "Consolidated Statements of Cash"

        df = self._read_sheet(sheet_name)

        key_column = df.columns[0]
        date = self._read_date(df)

    def _read_sheet(self, sheet_name):
        return pd.read_excel(self.filename, sheet_name=sheet_name)

    def _read_date(self, df):
        try:
            date = pd.Timestamp(df.columns[1])
        except ValueError:
            date = pd.Timestamp(df.iloc[0][1])

        date = date.to_pydatetime().date()
        print(date)
        return date
