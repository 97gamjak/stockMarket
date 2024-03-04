tot_revs_and_other = "total revenues and other"
tot_revs_and_other_inc = "total revenues and other income"
tot_revs_and_non_op_inc = "total revenues and non-operating income"
tot_revs = "total revenues"
tot_rev = "total revenue"
tot_net_revs = "total net revenues"
tot_op_revs = "total operating revenues"
tot_op_rev = "total operating revenue"
tot_prop_revs = "total property revenues"
total = "total"
revs_comma_net = "revenues, net"
revs = "revenues"
rev_contract_cust_incl_assessed_tax = "revenue from contract with customer, including assessed tax"
rev_contract_cust_excl_assessed_tax = "revenue from contract with customer, excluding assessed tax"
rev_contract_cust = "revenue from contract with customer"
rev = "revenue"
op_revs = "operating revenues"
sales_and_other_op_revs = "sales and other operating revenues"
sales_and_service_revs = "sales and service revenues"
sales = "sales"
service_revs = "service revenues"
rental_inc = "rental income"
net_revs = "net revenues"
net_rev = "net revenue"
net_sales = "net sales"
net_op_revs = "net operating revenues"
gross_revenues = "gross revenues"
other_prop_revs = "other property revenues"

special_ticker_revenue_combinations = {
    "AME": [
        [net_sales, total],
    ],
    "DTE": [
        [op_revs, total],
    ],
    "EXC": [
        [tot_op_revs, rev_contract_cust_incl_assessed_tax,
            rev_contract_cust_excl_assessed_tax]
    ],
    "GOOG": [
        [revs, total],
    ],
    "GOOGL": [
        [revs, total],
    ],
    "GRMN": [
        [net_sales, total],
    ],
}


revenue_key_combinations = [
    [tot_revs_and_other, tot_revs],
    [tot_revs_and_non_op_inc, sales_and_other_op_revs],
    [tot_revs_and_non_op_inc, sales],
    [tot_revs, tot_net_revs],
    [tot_revs, tot_op_revs],
    [tot_revs, tot_op_rev],
    [tot_revs, total],
    [tot_revs, revs_comma_net],
    [tot_revs, revs],
    [tot_revs, rev],
    [tot_revs, sales],
    [tot_revs, sales_and_service_revs],
    [tot_revs, net_sales],
    [tot_revs, net_revs],
    [tot_revs, service_revs],
    [tot_revs, rental_inc],
    [tot_revs, rev_contract_cust_excl_assessed_tax],
    [tot_revs, rev_contract_cust_incl_assessed_tax],
    [tot_rev, total],  # AES
    [tot_rev, sales],
    [tot_rev, net_sales],
    [tot_rev, net_rev],
    [tot_rev, revs],
    [tot_rev, rev],
    [tot_rev, rental_inc],
    [tot_op_revs, op_revs],
    [tot_op_revs, service_revs],
    [tot_op_revs, rev_contract_cust_incl_assessed_tax],
    [tot_op_revs, 'operating revenue'],
    [tot_op_revs, rev_contract_cust_excl_assessed_tax],
    [tot_op_rev, total],  # for EIX
    [tot_revs_and_other_inc, net_sales],
    [tot_revs_and_other_inc, sales_and_other_op_revs],
    [tot_prop_revs, other_prop_revs],
    [total, op_revs],
    [total, rev_contract_cust],
    [total, sales],
    [revs, total],  # for BR
    [revs, op_revs],
    [revs, net_revs],
    [revs, net_sales],
    [revs, rev_contract_cust_excl_assessed_tax],
    [revs, rev_contract_cust_incl_assessed_tax],
    [rev, revs],
    [rev, total],
    [rev_contract_cust_excl_assessed_tax, total],
    [net_sales, total],  # for AMAT
    [net_revs, net_sales],
    [net_revs, total],
    [sales, net_sales],
    [gross_revenues, net_revs],
    [gross_revenues, net_op_revs],
    [gross_revenues, 'total net revenues'],
    [service_revs, net_op_revs],
    ['total net revenue', revs],
    ['total sales and service revenues', service_revs],
    ['revenues and other income', sales_and_other_op_revs],
    ['gross operating revenues', net_op_revs],
    ['net sales and revenues', revs],
    ['net sales and revenues', total],  # for DE


    [tot_revs_and_other, tot_revs, rev_contract_cust_incl_assessed_tax],
    [tot_revs, net_revs, rev_contract_cust],
    [tot_revs, rental_inc, rev_contract_cust],
    [tot_revs, op_revs, sales_and_service_revs],
    [tot_revs, rev_contract_cust_incl_assessed_tax, tot_net_revs],  # AMP
    [tot_revs, total, revs],
    [tot_rev, total, sales],
    [tot_rev, total, net_rev],
    [tot_prop_revs, tot_op_revs, other_prop_revs],
    [rev_contract_cust_incl_assessed_tax, tot_op_revs,
        rev_contract_cust_excl_assessed_tax],
]

revenue_keys = {
    tot_revs_and_other,
    tot_revs_and_non_op_inc,
    tot_revs_and_other_inc,
    tot_revs,
    tot_rev,
    tot_net_revs,
    tot_op_revs,
    tot_op_rev,
    tot_prop_revs,
    revs_comma_net,
    revs,
    rev,
    op_revs,
    sales_and_service_revs,
    sales_and_other_op_revs,
    sales,
    net_sales,
    net_revs,
    net_rev,
    net_op_revs,
    service_revs,
    rental_inc,
    total,
    rev_contract_cust,
    rev_contract_cust_excl_assessed_tax,
    rev_contract_cust_incl_assessed_tax,
    other_prop_revs,

    "Service revenues and vehicle sales",
    "Customer services",
    "property revenues",
    "Rental and other property revenues",
    "processing and services revenues",
    "Railway operating revenues",
    "Segment sales to external customers",
    "Net service revenues",
    "income from rentals",
    "gross revenues",
    "gross operating revenues",
    "operating revenue",
    "net revenue:",
    "net revenues:",
    "revenue, net",
    "revenue*",
    "revenue, total",
    "Revenues and other income",
    "Revenue from product and services",
    "Revenue from operations",
    "Net revenues, including net interest income",
    "Net revenues, external",
    "NET SALES AND OPERATING REVENUES",
    "net sales and revenues",
    "Sales revenue net",
    "sales and revenues",
    "Sales to customers",
    "sales and other operating revenues:",
    "Total sales and service revenues",
    "Total revenues, net",
    "total net sales",
    "Total net sales and revenue",
    "total sales",
    "total net revenue",
    "total sales and revenues",
}
