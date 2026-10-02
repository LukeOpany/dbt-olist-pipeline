# Olist delivery findings

Population: 96,470 eligible delivered orders of 99,441 source orders; 2,971 excluded.
Order purchase period: 2016-09-15 to 2018-08-29.

- Late deliveries: 6,534 (6.77%).
- Largest late-order destination: SP, with 1,820 late orders out of 40,494 (4.49%).
- Mean order-level review: 2.27/5 for late orders (n=6,381) and 4.29/5 for on-time orders (n=89,443); difference -2.02 points.
- Seller with most associated late orders: `4a3ca9315b744ce9f8e9374361493884` (172/1,772; 9.71%).

## Recommended investigation

Start with the destination and seller groups contributing the most late orders. Compare their late rates and volumes before prioritizing an operational review. Examine carrier handoffs and promised delivery dates before attributing fault to a seller.

## Definitions and limitations

- Late means actual delivery calendar date is after the estimated delivery calendar date.
- Eligible orders are delivered, have usable purchase/actual/estimated timestamps, and have no delivery or promise before purchase. Other orders remain excluded, not on-time.
- Multiple reviews are averaged within each order first; missing reviews are excluded from review averages.
- Multi-seller orders appear once per associated seller. Seller counts overlap and must not be summed to obtain total orders.
- The review difference is an association, not a causal effect. This historical dataset does not establish current marketplace performance.
- Figures are descriptive; no profit gains or predictive performance are claimed.
