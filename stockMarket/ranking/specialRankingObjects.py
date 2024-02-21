import operator

from .rankingObject import RangeRankingObject, ValueRankingConstraint


def create_equity_ratio_ranker(cutoffs=[10, 30], scores=[0, 1, 2]):
    return RangeRankingObject("Equity Ratio", lambda x: x.equity_ratio, cutoffs, scores)


def create_netto_margin_ranker(cutoffs=[10, 20], scores=[0, 1, 2]):
    return RangeRankingObject("Netto Margin", lambda x: x.netto_margin, cutoffs, scores)


def create_return_on_assets_ranker(cutoffs=[5, 10], scores=[0, 1, 2]):
    return RangeRankingObject("Return on Assets", lambda x: x.return_on_assets, cutoffs, scores)


def create_goodwill_ranker(cutoffs=[0, 30], scores=[0, 1, 0]):
    return RangeRankingObject("Goodwill", lambda x: x.goodwill_ratio, cutoffs, scores)


def create_gearing_ranker(cutoffs=[20, 60], scores=[2, 1, 0]):
    return RangeRankingObject("Gearing", lambda x: x.gearing, cutoffs, scores)


def create_dynamic_gearing_ranker(cutoffs=[2, 5], scores=[2, 1, 0]):
    return RangeRankingObject("Dynamic Gearing", lambda x: x.dynamic_gearing, cutoffs, scores)


def create_asset_coverage_ratio_ranker(cutoffs=[100, 200], scores=[0, 1, 2]):
    return RangeRankingObject("Asset Coverage Ratio", lambda x: x.asset_coverage_ratio, cutoffs, scores)


def create_peg_ranker(growth_years, cutoffs=[0.8, 1.2], scores=[2, 1, 0], date=None, years_back=0):
    pe_constraint = ValueRankingConstraint(
        lambda x: x.price_to_earnings(years_back=years_back), operator.gt, 0)

    growth_eps_constraint = ValueRankingConstraint(
        lambda x: x.earnings_per_share_growth(growth_years), operator.gt, 0)

    peg_ranking = RangeRankingObject(
        "PEG",
        lambda x: x.peg(growth_years, date=date, years_back=years_back),
        cutoffs,
        scores,
        constraints=[pe_constraint, growth_eps_constraint]
    )

    return peg_ranking


def create_prg_ranker(growth_years, cutoffs=[0.8, 1.2], scores=[2, 1, 0], date=None, years_back=0):
    pr_constraint = ValueRankingConstraint(
        lambda x: x.price_to_revenue(years_back=years_back), operator.gt, 0)

    growth_pr_constraint = ValueRankingConstraint(
        lambda x: x.revenue_per_share_growth(growth_years), operator.gt, 0)

    prg_ranking = RangeRankingObject(
        "PRG",
        lambda x: x.prg(growth_years, date=date, years_back=years_back),
        cutoffs,
        scores,
        constraints=[pr_constraint, growth_pr_constraint]
    )

    return prg_ranking


def create_pfcg_ranker(growth_years, cutoffs=[0.8, 1.2], scores=[2, 1, 0], date=None, years_back=0):
    pfc_constraint = ValueRankingConstraint(
        lambda x: x.price_to_free_cashflow(years_back=years_back), operator.gt, 0)

    growth_pfc_constraint = ValueRankingConstraint(
        lambda x: x.free_cashflow_per_share_growth(growth_years), operator.gt, 0)

    pfcg_ranking = RangeRankingObject(
        "PFCG",
        lambda x: x.pfcg(growth_years, date=date, years_back=years_back),
        cutoffs,
        scores,
        constraints=[pfc_constraint, growth_pfc_constraint]
    )

    return pfcg_ranking


def create_pbg_ranker(growth_years, cutoffs=[0.8, 1.2], scores=[2, 1, 0], date=None, years_back=0):
    pb_constraint = ValueRankingConstraint(
        lambda x: x.price_to_book(years_back=years_back), operator.gt, 0)

    growth_pbg_constraint = ValueRankingConstraint(
        lambda x: x.book_value_per_share_growth(growth_years), operator.gt, 0)

    pbg_ranking = RangeRankingObject(
        "PBG",
        lambda x: x.pbg(growth_years, date=date, years_back=years_back),
        cutoffs,
        scores,
        constraints=[pb_constraint, growth_pbg_constraint]
    )

    return pbg_ranking
