.. _general:

*******
General
*******

If any of the following derived KPIs contain a growth rate, it is assumed that the growth rate is not fixed to a certain time period. Therefore, the growth rate is always noramlized to a yearly growth rate. This can be achieved by the following formula:

.. math::
        Growth(KPI, n_{\text{years}}) = \frac{KPI_{\text{new}}}{KPI_{\text{old}}}^{1/n_{\text{years}}} - 1

============
Derived KPIs
============

.. list-table::
    :header-rows: 1
    :class: tight-table

    * - KPI
      - ID
      - Description
      - Formula
    * - Earnings Per Share
      - EPS
      - Net Income divided by Total Outstanding Shares Common Stock
      - :math:`\frac{NetInc}{TotOutShares}`
    * - Revenue Per Share
      - RPS
      - Revenue divided by Total Outstanding Shares Common Stock
      - :math:`\frac{Rev}{TotOutShares}`
    * - Operating Cash Flow Per Share
      - OpCFPS
      - Operating Cash Flow divided by Total Outstanding Shares Common Stock
      - :math:`\frac{OpCF}{TotOutShares}`
    * - Free Cash Flow Per Share
      - FreeCFPS
      - Free Cash Flow divided by Total Outstanding Shares Common Stock
      - :math:`\frac{FreeCF}{TotOutShares}`
    * - EBITDA
      - EBITDA
      - EBIT + Depreciation & Amortization
      - :math:`EBIT + D\&A`
    * - EBITDA Margin
      - EBITDAMargin
      - EBITDA divided by Revenue
      - :math:`\frac{EBITDA}{Rev}`
    * - Return On Assets
      - RetOnAss
      - Return on Assets is a measure of how effectively a company uses its assets to generate earnings
      - :math:`\frac{NetInc}{TotAss}`
    * - Price/Earnings
      - P/E
      - Price divided by Earnings Per Share
      - :math:`\frac{Price}{EPS}`
    * - Price/Revenue
      - P/R
      - Price divided by Revenue Per Share
      - :math:`\frac{Price}{RPS}`
    * - Price/Operating Cash Flow
      - P/OpCF
      - Price divided by Operating Cash Flow Per Share
      - :math:`\frac{Price}{OpCFPS}`
    * - Price/Free Cash Flow
      - P/FreeCF
      - Price divided by Free Cash Flow Per Share
      - :math:`\frac{Price}{FreeCFPS}`
    * - Price/Book Value
      - P/B
      - Price divided by Book Value Per Share
      - :math:`\frac{Price}{BPS}`
    * - Price To Earnings Growth
      - PEG
      - Price To Earnings divided by Growth(EPS, n)
      - :math:`\frac{P/E}{Growth(EPS)}`
    * - Price To Revenue Growth
      - PRG
      - Price To Revenue divided by Growth(RPS, n)
      - :math:`\frac{P/R}{Growth(RPS)}`
    * - Price To Operating Cash Flow Growth
      - POCG
      - Price To Operating Cash Flow divided by Growth(OpCFPS, n)
      - :math:`\frac{P/OpCF}{Growth(OpCFPS)}`
    * - Price To Free Cash Flow Growth
      - PFCG
      - Price To Free Cash Flow divided by Growth(FreeCFPS, n)
      - :math:`\frac{P/FreeCF}{Growth(FreeCFPS)}`
    * - Price To Book Value Growth
      - PBG
      - Price To Book Value divided by Growth(BPS, n)
      - :math:`\frac{P/B}{Growth(BPS)}`