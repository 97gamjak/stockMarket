headers = {
    "User-Agent": 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'}


tickers_to_change_name = {
    "ENOB": "RENB",
    "CENTA": "CENT",
    "LILAK": "LILA",
    "TUI1.F": "TUI",
}

tickers_to_ignore = [
    "CWEN",
    "RuSHB",
    "UONEK",
    "UONE",
    "GOOG, GOOGL",

    "HUH1V.HE",     # from Euro Stoxx 600
    "TIGO-SDB.ST",  # from Euro Stoxx 600
    "INDU-C.ST",    # from Euro Stoxx 600
    "EFE.F",        # from Euro Stoxx 600
    "QGEN",         # from Euro Stoxx 600
    "SGBAF",        # from Euro Stoxx 600
    "VOLVBS.XC",    # from Euro Stoxx 600
    "WRT1V.HE",     # from Euro Stoxx 600
    "NDA-SE.ST",    # from Euro Stoxx 600
    "LISP.SW",      # from Euro Stoxx 600
    "SRT3.DE",      # from Euro Stoxx 600
    "UMG.AS",       # from Euro Stoxx 600

    "AJRD",   # bought by L3Harris
    "ARGO",   # bought by Brookfield Reinsurance
    "ARNC",   # bought by Apollo Funds
    "AVTA",   # bought by Cetera
    "AVID",   # bought by STG
    "BVH",    # bought by Hilton Grand Vacations
    "CCF",    # bought by KKR
    "CELL",   # bought by Bruker
    "CIR",    # bought by KKR
    "CTIC",   # bought by Orphan Biovitrum
    "CVT",    # bought by Blackstone
    "DEN",    # bought by Exxon
    "DICE",   # bought by Eli Lilly
    "DSEY",   # bought by Solenis
    "EQRX",   # bought by Revolution Medicines
    "ESMT",   # bought by Vista Equity Partners
    "ESTE",   # bought by Permian Resources
    "FOCS",   # bought by Clayton,Dubilier & Rice
    "FORG",   # bought by Thoma Bravo
    "HCCI",   # bought by J.F. Lehman & Company
    "HMPT",   # bought by Mr. Cooper Group
    "ICPT",   # bought by Alfasigma
    "INDT",   # bought by Centerbridge Partners and GIC
    "ISEE",   # bought by Astellas
    "KDNY",   # bought by Novartis
    "KLR",    # bought by Tata Communications
    "LVOX",   # bought by NICE
    "NXGN",   # bought by Thoma Bravo
    "PFSW",   # bought by GXO
    "PLM",    # bought by Glencore
    "PNT",    # bought by Eli Lilly
    "PRDS",   # bought by Medi Pacific
    "QUOT",   # bought by Neptune Retail Solutions
    "RETA",   # bought by Biogen
    "ROCC",   # bought by Baytex Energy
    "RPT",    # bought by Kimco Reality
    "RXDX",   # bought by Merck & CO
    "SCU",    # bought by Rithm Capital Corp
    "TFM",    # bought by Cencosud
    "THRN",   # bought by L. Catterton
    "TRTN",   # bought by Brookfield Infrastructure
    "TWNK",   # bought by J.M. Smucker
    "UBA",    # bought by Regency Centers
    "VRTV",   # bought by CD&R

    "GRNA",  # merged with LLC
    "LTHM",  # merged with Allkem
    "NETI",  # merged with Cadeler
    "NEX",   # merged with Patterson-UTI
    "NUVA",  # merged with Globus Medical
    "RTL",   # merged with  Global NET Lease
    "SLGC",  # merged with Somat Logic Inc


    "RADI",  # went private
    "HT",    # went private
    "CHS",   # went private
    "FRG",   # went private
    "PDLI",  # went private

    "AMRS",  # bankrupt
    "APPH",  # bankrupt
    "EBIX",  # bankrupt
    "IRNT",  # bankrupt
    "PTRA",  # bankrupt
    "RAD",   # bankrupt
    "RIDE",  # bankrupt
    "SUNL",  # bankrupt
    "TTCF",  # bankrupt
    "VRAY",  # bankrupt
    "ZEV",   # bankrupt
    "OSTK",   # bankrupt


    "AGLE",  # not aviailable, penny stock

    "FIBK",   # no idea why not available
]
