import pandas as pd
import openpyxl as xl
import numpy as np
import datetime as dt
import collections
import re

from ._sheet_config import (
    possible_income_sheet_combinations,
    possible_income_sheet_names,
    special_ticker_income_sheet_combinations,
)

from ._revenue_config import (
    revenue_keys,
    revenue_key_combinations,
    special_ticker_revenue_combinations,
)


class FinancialReportReader:
    def __init__(self, filename):
        self.filename = filename
        self.ticker = filename.split("/")[-4]
        wb = xl.load_workbook(filename)
        self.sheet_names = wb.sheetnames
        self.sheet_names_lower_case = [sheet.lower()
                                       for sheet in self.sheet_names]

    def read(self):
        self.read_income()
        # self.read_balance()
        # self.read_cashflow()

    def read_income(self):
        self.sheet_name = self._get_sheet_name(possible_income_sheet_names)
        df = self._read_sheet(self.sheet_name)

        key_column = df.columns[0]

        date = self._read_date(df)

        revenue = self._get_value_from_df(
            df, "revenue", key_column, revenue_keys, strategy="max")

        dictionary = {"revenue": revenue}

        first_key_column_entry = df[key_column].values[0]
        first_key_column_entry = first_key_column_entry.lower() if isinstance(
            first_key_column_entry, str) else ""
        first_key_column_entry = re.sub(
            r"share data in [a-z]{8}", "", first_key_column_entry)

        if "$ in thousands" in key_column.lower() or "in thousands" in first_key_column_entry:
            dictionary = {key: value/1000 for key, value in dictionary.items()}
        elif "$ in millions" in key_column.lower() or "in millions" in first_key_column_entry:
            dictionary = {key: value for key, value in dictionary.items()}
        else:
            dictionary = {key: value/1000000 for key,
                          value in dictionary.items()}

        return date, dictionary

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

    def _get_value_from_df(self, df, key_to_find, key_column, possible_keys, strategy=None):
        possible_keys = {key.lower() for key in possible_keys}
        df_keys = df[key_column].str.lower()
        # df_keys = df_keys.str.replace(r" \(.*", "", regex=True)
        df_keys = df_keys.str.replace(r" 1 & 2.*", "", regex=True)

        bool_array = np.array([False]*len(df_keys))

        for i, key in enumerate(df_keys):
            if key not in possible_keys:
                continue

            values = np.array(df.iloc[i].values[1:])
            if not all([not isinstance(value, (int, float)) or np.isnan(value) for value in values]):
                bool_array[i] = True

        found_keys = set(df_keys[bool_array].values)
        self.key_combinations = []

        if len(found_keys) > 1:
            found_key = None

            for combination in special_ticker_revenue_combinations.get(self.ticker, []):
                if compare(combination, found_keys):
                    found_key = combination[0]
                    break

            if not found_key:
                for combination in revenue_key_combinations:
                    if compare(combination, found_keys):
                        found_key = combination[0]
                        break

            if found_key:
                key_value_pairs = df.loc[df_keys == found_key].values
            else:
                raise ValueError(
                    f"Ambiguous {key_to_find} keys found in file {self.filename}: found keys {found_keys}")
        else:
            key_value_pairs = df[bool_array].values

        values = []
        for key_value_pair in key_value_pairs:
            single_key_values = [
                value for value in key_value_pair[1:] if isinstance(value, (int, float)) and not np.isnan(value)]
            if single_key_values:
                values.append(single_key_values)

        if not values:
            raise ValueError(
                f"No {key_to_find} found in sheet {self.sheet_name} for file {self.filename}")
        elif len(values) > 1:
            values = [value[0] for value in values]
            if strategy == "max":
                value = max(values)
            elif np.isclose(2*max(values), sum(values), rtol=1e-4):
                value = max(values)
            else:
                raise ValueError(
                    f"Multiple {key_to_find}s found for file {self.filename}: found keys {found_keys} with values {values}")
        else:
            value = values[0][0]

        return float(value)

    def _get_sheet_name(self, possible_sheet_names):
        found_sheets = {
            sheet for sheet in possible_sheet_names if sheet.lower() in self.sheet_names_lower_case
        }

        if not found_sheets:
            raise ValueError(
                f"No income statement found in file {self.filename}")
        elif len(found_sheets) > 1:
            sheet_name = None

            if self.ticker in special_ticker_income_sheet_combinations.keys():
                for combination in special_ticker_income_sheet_combinations[self.ticker]:
                    if compare(combination, found_sheets):
                        sheet_name = combination[0]
                        break

            if not sheet_name:
                for combination in possible_income_sheet_combinations:
                    if compare(combination, found_sheets):
                        sheet_name = combination[0]
                        break

            if sheet_name is None:
                raise ValueError(
                    f"Multiple income statements found in file {self.filename}: found sheets {found_sheets}")
        else:
            sheet_name = next(iter(found_sheets))

        sheet_index = self.sheet_names_lower_case.index(sheet_name.lower())
        sheet_name = self.sheet_names[sheet_index]

        return sheet_name

    def _read_sheet(self, sheet_name):
        df = pd.read_excel(self.filename, sheet_name=sheet_name)
        columns = df.columns
        column_indices_to_remove = []

        for i in range(12):
            column_indices_to_remove += self.get_columns_to_remove_months_ended(
                i, columns)

        df = df.drop(columns=df.columns[column_indices_to_remove])

        return df

    def get_columns_to_remove_months_ended(self, months, columns):
        column_indices_to_remove = []
        index = 0
        months_ended = False
        while index < len(columns):
            if f"{months} months ended" in columns[index].lower() and "12 months" not in columns[index].lower():
                column_indices_to_remove.append(index)
                months_ended = True
                index += 1
                continue

            if months_ended and "unnamed" in columns[index].lower():
                column_indices_to_remove.append(index)
            elif months_ended:
                break

            index += 1

        return column_indices_to_remove

    def _read_date(self, df):
        try:
            columns = [column for column in df.columns[1:] if (isinstance(
                column, dt.datetime) or isinstance(column, str)) and "unnamed" not in column.lower()]
            # filter all columns that contain a date with pattern "aaa. dd, yyyy" as a substring
            # and remove all characters that are not part of substring
            columns = [re.sub(r".*?(\w{3}\. \d{1,2}, \d{4}).*", r"\1", column)
                       for column in columns if re.match(r".*?(\w{3}\. \d{1,2}, \d{4}).*", column)]
            columns = [pd.Timestamp(column) for column in columns]
            date = max(columns)
        except Exception:
            new_df = df.replace(r"USD.*", "", regex=True)
            values = new_df.iloc[0].values[1:]
            values = [value for value in values if isinstance(
                value, str) or isinstance(value, dt.datetime)]

            date = pd.Timestamp(
                re.sub(r".*?(\w{3}\. \d{1,2}, \d{4}).*", r"\1", values[0]))

        date = date.to_pydatetime().date()
        return date


def compare(x, y): return collections.Counter(x) == collections.Counter(y)
