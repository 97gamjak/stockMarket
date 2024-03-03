con_sts_oper = "Consolidated Statements of Oper"
con_st_opera = "Consolidated Statement of Opera"
con_st_incom = "Consolidated Statement of Incom"
con_sts_inco = "Consolidated Statements of Inco"
con_sts_comp = "Consolidated Statements of Comp"
con_sts_earn = "Consolidated Statements of Earn"
cond_con_statemen = "Condensed Consolidated Statemen"
_con_sts_com = "Consolidated_Statements_of_Com"
_con_sts_ope = "Consolidated_Statements_of_Ope"
_con_sts_ear = "Consolidated_Statements_of_Ear"
_con_sts_inc = "Consolidated_Statements_of_Inc"
_cond_con_stateme = "Condensed_Consolidated_Stateme"

# special combinations if they collide with other sheet combinations
special_ticker_income_sheet_combinations = {
    "TMUS": [
        [con_sts_comp, cond_con_statemen],
    ]
}

possible_income_sheet_combinations = [
    [cond_con_statemen, con_sts_comp],
    [con_sts_oper, con_sts_comp],
    [con_sts_oper, con_st_opera],
    [con_st_opera, con_sts_comp],
    [con_sts_inco, con_sts_comp],
    [con_sts_inco, cond_con_statemen],
    [con_st_incom, con_sts_comp],
    [con_st_incom, cond_con_statemen],
    [con_sts_earn, con_sts_comp],
    [con_sts_earn, cond_con_statemen],
    [_con_sts_ope, _con_sts_com],
    [_con_sts_ope, _cond_con_stateme],
    [_con_sts_ear, _con_sts_com],
    [_con_sts_ear, _cond_con_stateme],
    [_con_sts_inc, _con_sts_com],
    [_con_sts_inc, _cond_con_stateme],
    ['CONSOLIDATED_CONDENSED_STATEME', _con_sts_inc],
    ['CONSOLIDATED INCOME STATEMENTS', con_sts_comp],
    ['Consolidated_Income_Statements', _con_sts_com],
    ['CONSOLIDATED STATEMENTS OF (LOS', con_sts_comp],
    ['Consolidated Results of Operati', con_sts_comp],
    ['Consolidated Statement of Earni', con_sts_comp],
    ['Consolidated_Results_of_Operat', _con_sts_com],
    ['Consolidated_and_Combined_Inco', 'CONSOLIDATED_AND_COMBINED_STAT'],

    [con_sts_oper, con_sts_comp, cond_con_statemen],
    [con_st_incom, con_sts_inco, con_sts_comp],
    [con_sts_inco, con_sts_comp, cond_con_statemen],
    [con_sts_earn, 'Consolidated Statement of Earni', con_sts_comp],
    [_con_sts_ope, _cond_con_stateme, _con_sts_com],
    [_con_sts_ope, _con_sts_com, 'Consolidated_Statement_of_Oper'],
    [_con_sts_inc, _con_sts_com, _cond_con_stateme],
    [_con_sts_ear, 'Consolidated_Statement_of_Earn', _con_sts_com],
]

possible_income_sheet_names = {
    con_st_incom,
    con_sts_inco,
    "Consolidated_Statement_of_Inco",
    _con_sts_inc,

    con_sts_oper,
    con_st_opera,
    _con_sts_ope,
    "Consolidated_Statement_of_Oper",
    "CONSOLDIATED_STATEMENTS_OF_OPE",

    con_sts_earn,
    "Consolidated Statement of Earni",
    _con_sts_ear,
    "Consolidated_Statement_of_Earn",

    con_sts_comp,
    _con_sts_com,

    "CONSOLIDATED STATEMENTS OF (LOS",
    "Consolidated Statement of (Loss",

    "CONSOLIDATED INCOME STATEMENTS",
    "Consolidated Income Statement",
    "Consolidated_Income_Statements",
    "Consolidated_Income_Statement",

    "CONSOLIDATED_CONDENSED_STATEME",
    "Consolidated Condensed Statemen",

    "Consolidated_Results_of_Operat",
    "Consolidated Results of Operati",

    "Consolidated Comprehensive Stat",
    "Consolidated_Comprehensive_Sta",

    "CONSOLIDATED_AND_SECTOR_INCOME",
    "CONSOLIDATED AND SECTOR INCOME ",

    "CONSOLIDATED_AND_COMBINED_STAT",
    "CONSOLIDATED AND COMBINED STATE",
    "Consolidated_and_Combined_Inco",

    "Combined and Consolidated State",
    "Combined_Consolidated_Statemen",

    cond_con_statemen,
    _cond_con_stateme,

    "Statements Of Consolidated Earn",
    "Statements_Of_Consolidated_Ear",

    "STATEMENT OF CONSOLIDATED OPERA",
    "STATEMENTS OF CONSOLIDATED OPER",
    "Statement_of_Consolidated_Oper",
    "STATEMENTS_OF_CONSOLIDATED_OPE",

    "STATEMENTS OF CONSOLIDATED INCO",
    "STATEMENT OF CONSOLIDATED INCOM",
    "STATEMENTS_OF_CONSOLIDATED_INC",
    "Statement_of_Consolidated_Inco",

    "Statement_of_Earnings",
    "Statement of Earnings",
    "STATEMENT OF EARNINGS (LOSS)",

    "Statement of Income",
    "Statements Of Income",
    "Statement_of_Income",
    "Statements_Of_Income",

    "Statements of Operations",
    "Statements_Of_Operations",

    "income statements",
    "INCOME_STATEMENTS",

    "10-K Consolidated Statements Of",

    "Carnival Corporation & PLC Cons",
    "Carnival_Corporation_Plc_Conso",
    "EPT - Consolidated Statements o",
    "VICI PROPERTIES INC. CONSOLID_3",
    "BorgWarner Inc. and Consolida_2",
    "BorgWarner Inc. and Consolidat3",
    "BorgWarner_Inc_and_Consolidate1",
    "CMS Energy Corporation Consolid",

    "UNAUDITED CONDENSED CONSOLIDATE",  # for BALL
}
