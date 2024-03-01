import pandas as pd
import openpyxl as xl
import numpy as np


class FinancialReportReader:
    def __init__(self, filename):
        self.filename = filename
        wb = xl.load_workbook(filename)
        self.sheet_names = wb.sheetnames
        self.sheet_names_lower_case = [sheet.lower()
                                       for sheet in self.sheet_names]

    def read(self):
        self.read_income()
        # self.read_balance()
        # self.read_cashflow()

    def read_income(self):
        sheet_name = self._get_sheet_name(possible_income_sheet_names)

        df = self._read_sheet(sheet_name)

        key_column = df.columns[0]
        date = self._read_date(df)

        # higher weight on total revenue
        income_keys = {
            "revenue": {
                "sales": 1,
                "net sales": 1,
                "revenues": 1,
                "revenue": 1,
                "net revenues": 1,
                "net revenues:": 1,
                "total net revenues": 2,
                "total revenue": 2,
                "total revenues": 2,
            },
        }

        revenue = self._get_value_from_df(
            df, "revenue", key_column, income_keys)

        # print(revenue)

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

    def _get_value_from_df(self, df, key_to_find, key_column, key_dict):
        key_to_find_dict = {key.lower(): value for key,
                            value in key_dict[key_to_find].items()}
        df_keys = np.array([str(key).lower() for key in df[key_column].values])

        bool_array = [False for _ in df_keys]

        for i, key in enumerate(df_keys):
            if key not in key_to_find_dict.keys():
                continue

            values = np.array(df.iloc[i].values[1:])
            if not all([not isinstance(value, (int, float)) or np.isnan(value) for value in values]):
                bool_array[i] = True

        # extreme special case maybe remove this one and just use extra key in the dict
        if not any(bool_array):
            bool_array = []
            for key in df_keys:
                is_in_list = False
                for ref_key in key_to_find_dict.keys():
                    if key.startswith(ref_key + " ("):
                        is_in_list = True
                        break
                bool_array.append(is_in_list)

        found_keys = set([key for key in df_keys[bool_array]])

        if len(found_keys) > 1:
            max_priority = max([key_to_find_dict[key] for key in found_keys])
            found_keys = set(
                [key for key in found_keys if key_to_find_dict[key] == max_priority])
            if len(found_keys) == 1:
                key_value_pairs = df.loc[df_keys == list(found_keys)[0]].values
            else:
                raise ValueError(
                    f"Ambiguous revenue keys found in file {self.filename}")
        else:
            key_value_pairs = df[bool_array].values

        values = []
        for key_value_pair in key_value_pairs:
            single_key_values = [
                value for value in key_value_pair[1:] if isinstance(value, (int, float)) and not np.isnan(value)]
            values.append(single_key_values)

        if len(values) == 0:
            raise ValueError(
                f"No revenue found for file {self.filename}")
        elif len(values) > 1:
            values = [value[0] for value in values]
            if 2*max(values) == sum(values):
                value = max(values)
            else:
                raise ValueError(
                    f"Multiple revenues found for file {self.filename}")
        else:
            value = values[0][0]

        return value

    def _get_sheet_name(self, possible_sheet_names):
        sheet_dict = {sheet.lower(): value for sheet,
                      value in possible_sheet_names.items()}
        found_sheets = set([sheet for sheet in sheet_dict.keys()
                            if sheet in self.sheet_names_lower_case])

        if len(found_sheets) == 0:
            raise ValueError(
                f"No income statement found in file {self.filename}")
        elif len(found_sheets) > 1:
            sheets_priority = {sheet: sheet_dict[sheet]
                               for sheet in found_sheets}
            max_priority = max(sheets_priority.values())
            found_sheets = set(
                [sheet for sheet in found_sheets if sheets_priority[sheet] == max_priority])
            if len(found_sheets) == 1:
                sheet_name = list(found_sheets)[0]
            else:
                raise ValueError(
                    f"Multiple income statements found in file {self.filename}")
        else:
            sheet_name = list(found_sheets)[0]

        sheet_index = self.sheet_names_lower_case.index(sheet_name)
        sheet_name = self.sheet_names[sheet_index]

        return sheet_name

    def _read_sheet(self, sheet_name):
        return pd.read_excel(self.filename, sheet_name=sheet_name)

    def _read_date(self, df):
        try:
            date = pd.Timestamp(df.columns[1])
        except ValueError:
            date = pd.Timestamp(df.iloc[0].iloc[1])

        date = date.to_pydatetime().date()
        return date


# higher weight on all *incom sheet names
possible_income_sheet_names = {
    "Consolidated Statement of Incom": 2,
    "Consolidated_Statement_of_Inco": 2,
    "Consolidated Statements of Inco": 2,
    "Consolidated_Statements_Of_Inc": 2,
    "Consolidated Statements of Oper": 2,
    "Consolidated_Statements_of_Ope": 2,
    "income statements": 2,
    "Consolidated Statements Of Earn": 2,
    "Consolidated_Statements_Of_Ear": 2,
    "Consolidated Statements of Comp": 1,
    "Consolidated_Statements_of_Com": 1,
}
