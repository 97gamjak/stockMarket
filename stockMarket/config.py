from __future__ import annotations

from .screeningData import InfoScreener
from .screeningData import CashflowScreener
from .screeningData import RelationToSumScreener
from .screeningData import GrowthScreener
from .screeningData import CalendarScreener
from .screeningData import ThreeYearScreener

tickers_to_change_name = {
    "AVID": "CDMO",
    "BOMN": "BOC",
}

tickers_to_ignore = [
    "ONEM",  # bought by amazon
    "AERI",  # bought by Alcon
    "AJRD",  # bought by L3Harris
    "ANAT",  # bought by Core Specialty
    "ANGN",  # bought by Elicio Therapeutics
    "ATRS",  # bought by Halozyme Therapeutics
    "AAWW",  # bought by investor group
    "BPFH",  # bought by SVB Financial Group
    "EPAY",  # bought by Thoma Bravo
    "BRMK",  # bought by Ready Capital
    "BTX",   # bought by Resideo

    "ACBI",  # merged with South State
    "BXS",   # merged with Cadence Bancorporation
    "BCEI",  # merged with Extraction Oil & Gas
    "MNRL",  # merged with Sitio Royalties
    "ATCX",  # went private

    "NMTR",  # bankrupt
    "AMRS",  # bankrupt
    "ATNX",  # bankrupt
    "ATHX",  # bankrupt
    "AUD",   # bankrupt
    "AVYA",  # bankrupt

    "AGLE",  # not aviailable, penny stock

    # "AFIN",  # no idea why not available - some REIT
    # "HOME",  # no idea why not available
    # "BCOR",  # no idea why not available
    # "BVH",   # no idea why not available
]
