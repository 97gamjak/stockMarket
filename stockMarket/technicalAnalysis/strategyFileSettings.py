import glob
import shutil

from pathlib import Path
from beartype.typing import Optional, List

from .strategyObjects import StrategyObject, RuleEnum
from .enums import StrategyStoringBehavior


class StrategyFileSettings:
    def __init__(self,
                 storing_behavior: StrategyStoringBehavior | str = StrategyStoringBehavior.NUMERICAL,
                 base_path: str = "strategy_testing",
                 template_xlsx_path: Optional[str] = None,
                 template_xlsx_file: str = "template.xlsx",
                 xlsx_file: str = "screening.xlsx",
                 json_file: str = "strategy.json",
                 trades_json_file: str = "trades.json",
                 ) -> None:

        self.storing_behavior = StrategyStoringBehavior(storing_behavior)
        self.base_path = Path(base_path)
        self.template_xlsx_path = template_xlsx_path
        self.template_xlsx_file = template_xlsx_file
        self.xlsx_file = xlsx_file
        self.json_file = json_file
        self.trades_json_file = trades_json_file

    def setup(self,
              strategy_objects: List[StrategyObject],
              rule_enums: List[RuleEnum],
              ) -> None:
        self.initialize_storing_behavior(strategy_objects, rule_enums)

        if self.template_xlsx_path is not None:
            self.template_xlsx_path = Path(self.template_xlsx_path)
        else:
            self.template_xlsx_path = Path(__file__).parent / "templates"

        self.template_xlsx_file = str(
            self.template_xlsx_path / self.template_xlsx_file
        )
        self.xlsx_filename = str(self.dir_path / self.xlsx_file)

        self.json_file = str(self.dir_path / self.json_file)
        self.trades_json_file = str(self.dir_path / self.trades_json_file)

    def initialize_storing_behavior(self,
                                    strategy_objects: List[StrategyObject],
                                    rule_enums: List[RuleEnum]
                                    ) -> None:

        self.rule_enums = rule_enums

        strategy_names = [
            strategy_object.strategy_name for strategy_object in strategy_objects]
        self.dir_name = "_".join([name for name in sorted(strategy_names)])

        if not self.base_path.exists():
            self.base_path.mkdir()

        self.dir_path = self.base_path / self.dir_name

        if self.storing_behavior == StrategyStoringBehavior.NUMERICAL:
            self.numerical_storing_behavior()
        elif self.storing_behavior == StrategyStoringBehavior.ABORT:
            self.abort_storing_behavior()
        elif self.storing_behavior == StrategyStoringBehavior.FULL_OVERWRITE:
            self.full_overwrite_storing_behavior()
        else:
            raise NotImplementedError(
                f"Storing behavior not implemented, possible values are: {StrategyStoringBehavior.member_repr()} or {StrategyStoringBehavior.value_repr()}")

        self.dir_path.mkdir()

    def numerical_storing_behavior(self):

        if self.dir_path.exists():
            reserved_dir_names = glob.glob(
                str(self.dir_path) + "_*")
            reserved_dir_names = [
                name for name in reserved_dir_names if name.split("_")[-1].isdigit()]
            dir_numbers = sorted([int(name.split("_")[-1])
                                  for name in reserved_dir_names])
            if dir_numbers == []:
                self.dir_path = Path(str(self.dir_path) + "_1")
            else:
                self.dir_path = Path(
                    str(self.dir_path) + f"_{dir_numbers[-1] + 1}")

    def abort_storing_behavior(self):
        if self.dir_path.exists():
            raise FileExistsError(
                f"Directory {self.dir_path} already exists, aborting")

    def full_overwrite_storing_behavior(self):
        if self.dir_path.exists():
            shutil.rmtree(self.dir_path)

    def to_json(self):
        return {
            "storing_behavior": self.storing_behavior.value,
            "base_path": str(self.base_path),
            "dir_path": str(self.dir_path),
            "template_xlsx_path": str(self.template_xlsx_path),
            "template_xlsx_file": self.template_xlsx_file,
            "xlsx_file": self.xlsx_file,
            "json_file": self.json_file,
            "trades_json_file": self.trades_json_file,
        }

    @classmethod
    def init_from_json(cls, json: dict) -> "StrategyFileSettings":
        file_settings = cls()
        file_settings.storing_behavior = json["storing_behavior"]
        file_settings.base_path = json["base_path"]
        file_settings.dir_path = json["dir_path"]
        file_settings.template_xlsx_path = json["template_xlsx_path"]
        file_settings.template_xlsx_file = json["template_xlsx_file"]
        file_settings.xlsx_file = json["xlsx_file"]
        file_settings.json_file = json["json_file"]
        file_settings.trades_json_file = json["trades_json_file"]

        return file_settings
