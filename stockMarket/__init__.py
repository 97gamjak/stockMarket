from pathlib import Path
from beartype.claw import beartype_this_package

beartype_this_package()

__base_path__ = Path(__file__).parent
__data_path__ = __base_path__.joinpath("../data")
