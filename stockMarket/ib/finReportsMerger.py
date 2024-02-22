import glob
import os

from stockMarket import __data_path__


class FinReportsMerger:
    statement_path = __data_path__ / "fin_statements"
    backup_path = statement_path / "backup"

    def merge(self):
        files_to_merge = glob.glob(str(self.backup_path / "*"))
        for file in files_to_merge:
            with open(file, "r") as f:
                backup_data = f.read()
                backup_data = backup_data.split("\n")

            new_file = file.replace("/backup/", "/")

            if os.path.exists(new_file):
                with open(new_file, "r") as f:
                    new_data = f.read()
                    new_data = new_data.split("\n")

                fiscal_periods = [
                    line for line in new_data if line.startswith("<FiscalPeriod Type=")]
                backup_fiscal_periods = [
                    line for line in backup_data if line.startswith("<FiscalPeriod Type=")]

                diff_lines = []
                for line in backup_fiscal_periods:
                    if line not in fiscal_periods:
                        diff_lines.append(line)

                annual_diff_lines = [
                    line for line in diff_lines if "Annual" in line]
                interims_diff_lines = [
                    line for line in diff_lines if "Interim" in line]

                new_merged_data = []
                for line in new_data:
                    if line.startswith("</AnnualPeriods>"):
                        new_merged_data += self.add_old_fiscal_data(
                            annual_diff_lines, backup_data)

                    if line.startswith("</InterimPeriods>"):
                        new_merged_data += self.add_old_fiscal_data(
                            interims_diff_lines, backup_data)

                    new_merged_data.append(line)

                with open(new_file, "w") as f:
                    f.write("\n".join(new_merged_data))

            os.remove(file)

    def clean_up(self):
        files_to_clean = glob.glob(str(self.statement_path / "*.xml"))
        for file in files_to_clean:
            with open(file, "r") as f:
                data = f.read()
                data = data.split("\n")

            new_data = []
            first_occurrence = True
            end_encountered = False
            first_fiscal_period = []
            inc_found = False
            bal_found = False
            cas_found = False
            for line in data:
                if first_occurrence and line.startswith("<FiscalPeriod Type="):
                    first_occurrence = False

                if not first_occurrence and not end_encountered:
                    first_fiscal_period.append(line)
                else:
                    new_data.append(line)

                if not end_encountered and line.startswith("</FiscalPeriod>"):
                    end_encountered = True

                    if any([line == "<Statement Type=\"INC\">" for line in first_fiscal_period]):
                        inc_found = True
                    if any([line == "<Statement Type=\"BAL\">" for line in first_fiscal_period]):
                        bal_found = True
                    if any([line == "<Statement Type=\"CAS\">" for line in first_fiscal_period]):
                        cas_found = True

                    if inc_found and bal_found and cas_found:
                        new_data = new_data + first_fiscal_period

            with open(file, "w") as f:
                f.write("\n".join(new_data))

    def add_old_fiscal_data(self, annual_diff_lines, backup_data):
        new_data = []
        append_data = False
        for line in annual_diff_lines:
            append_data = False
            for data_line in backup_data:
                if data_line == line:
                    append_data = True

                if append_data:
                    new_data.append(data_line)

                if data_line.startswith("</FiscalPeriod>") and append_data:
                    break

        return new_data
