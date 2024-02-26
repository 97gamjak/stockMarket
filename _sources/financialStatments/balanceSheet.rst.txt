Balance Sheet
*************

Basic KPIs
==========

.. list-table::
    :header-rows: 1
    :class: tight-table

    * - KPI
      - ID
      - Description
      - IBKR ID
    * - Equity
      - Equ
      - Equity represents the residual interest in the assets of the entity after deducting liabilities.
      - QTLE
    * - Total Liabilities
      - TotLia 
      - Total liabilities represent the total amount of debts and obligations owed by the entity.
      - LTLL
    * - Total Current Liabilities
      - TotCurLia
      - Total current liabilities represent the total amount of debts and obligations that are due within one year.
      - LTCL
    * - Total Assets
      - TotAss
      - Total assets represent the total value of all resources owned by the entity.
      - ATOT
    * - Total Outstanding Shares Common Stock
      - TotOutShares
      - Total outstanding shares common stock represents the total number of shares of common stock that have been issued by the entity and are held by shareholders.
      - QTCO
    * - Goodwill
      - Goodwill
      - Goodwill represents the excess of the purchase price of an acquired business over the fair value of its identifiable net assets.
      - AGWI
    * - Current Portion of Long Term Debt and Capital Lease Obligations
      - CurLongTermDebt\&CapLeaObl
      - Current portion of long term debt and capital lease obligations represents the portion of long term debt and capital lease obligations that are due within one year.
      - LCLD
    * - Short Term Debt
      - ShortTermDebt
      - Short term debt represents the debt that is due within one year.
      - LSTD
    * - Accrued Expenses
      - AccExp
      - Accrued expenses represent the expenses that have been incurred but not yet paid.
      - LAEX
    * - Total Long Term Debt
      - TotLongTermDebt
      - Total long term debt represents the debt that is due after one year.
      - LTLD
    * - Total Receivables Net
      - TotRecNet
      - Total receivables net represents the total amount of money owed to the entity by its customers, minus any allowances for doubtful accounts.
      - ATRC
    * - Total Inventory
      - TotInv
      - Total inventory represents the total value of goods held by the entity for sale.
      - AITL
    * - Other Current Assets
      - OthCurAss
      - Other current assets represent the value of assets that are expected to be converted into cash within one year.
      - SOCA
    * - Prepaid Expenses
      - PreExp
      - Prepaid expenses represent the expenses that have been paid in advance but not yet incurred.
      - APPY
    * - Cash
      - Cash
      - Cash represents the amount of money held by the entity in the form of currency or cash equivalents.
      - ACSH
    * - Cash Equivalents
      - CashEquiv
      - Cash equivalents represent highly liquid investments that are readily convertible into cash.
      - ACAE
    * - Short Term Investments
      - ShortTermInv
      - Short term investments represent investments that are expected to be converted into cash within one year.
      - ASTI
    * - Intangible Assets
      - IntAss
      - Intangible assets represent non-physical assets that have value to the entity.
      - AINT

Derived KPIs
============

.. list-table::
    :header-rows: 1
    :class: tight-table

    * - KPI
      - ID
      - Description
      - Formula
    * - Equity Ratio
      - EquityRatio
      - Equity Ratio measures the proportion of the entity's assets that are financed by equity.
      - :math:`\frac{Equ}{TotAss}`
    * - Goodwill Ratio
      - GoodwillRatio
      - Goodwill Ratio measures the proportion of the entity's assets that are represented by goodwill.
      - :math:`\frac{Goodwill}{TotAss}`
    * - Total Short Term Debt
      - TotShortTermDebt
      - Total Short Term Debt represents the total amount of debt that is due within one year.
      - :math:`CurLongTermDebt\&CapLeaObl + ShortTermDebt`
    * - Cash & Short Term Investments
      - Cash\&ShortTermInv
      - Cash & Short Term Investments represents the total amount of cash and short term investments held by the entity.  
      - :math:`Cash + CashEquiv + ShortTermInv`
    * - Total Debt
      - TotDebt
      - Total Debt represents the total amount of debt owed by the entity.
      - :math:`TotShortTermDebt + TotLongTermDebt`
    * - Gearing
      - Gearing
      - Gearing measures the proportion of the entity's assets that are financed by debt.
      - :math:`\frac{TotDebt - Cash\&ShortTermInv}{Equ}`
    * - Total Non Current Assets
      - TotNonCurAss
      - Total Non Current Assets represents the total amount of assets that are not expected to be converted into cash within one year.
      - :math:`TotAss - TotCurAss`  
    * - Asset Coverage Ratio
      - AssetCovRatio
      - Asset Coverage Ratio measures the proportion of the entity's non current assets that are financed by equity and long term debt.
      - :math:`\frac{Equ + TotLongTermDebt}{TotNonCurAss}`
    * - Third Order Liquidity
      - Liq3
      - Third Order Liquidity measures the entity's ability to meet its short term obligations.
      - :math:`\frac{TotCurAss}{TotCurLia}`
    * - Book Value
      - BookValue
      - Book Value represents the value of the entity's assets that are financed by equity.
      - :math:`\frac{Equ - Goodwill - IntAss}{TotOutShares}`
    * - Book Value Per Share
      - BookValuePerShare
      - Book Value Per Share represents the value of the entity's assets that are financed by equity per share of common stock.
      - :math:`\frac{BookValue}{TotOutShares}`
