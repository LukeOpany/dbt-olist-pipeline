from pathlib import Path
import pandas as pd


def build_orders(directory):
    """Read four original Olist CSVs; collapse reviews before joining orders."""
    root = Path(directory)
    orders = pd.read_csv(root/'olist_orders_dataset.csv')
    customers = pd.read_csv(root/'olist_customers_dataset.csv')
    reviews = pd.read_csv(root/'olist_order_reviews_dataset.csv')
    items = pd.read_csv(root/'olist_order_items_dataset.csv')
    if orders.order_id.isna().any() or orders.order_id.duplicated().any():
        raise ValueError('orders must have unique non-null order_id')
    if customers.customer_id.isna().any() or customers.customer_id.duplicated().any():
        raise ValueError('customers must have unique non-null customer_id')
    reviews['review_score'] = pd.to_numeric(reviews.review_score, errors='raise')
    if not reviews.review_score.dropna().between(1,5).all():
        raise ValueError('review_score must be 1 through 5')
    # One average per order gives each reviewed order equal influence.
    scores = reviews.groupby('order_id', as_index=False).agg(review_score=('review_score','mean'))
    frame = orders.merge(customers[['customer_id','customer_state']], on='customer_id', how='left', validate='many_to_one')
    frame = frame.merge(scores,on='order_id',how='left',validate='one_to_one')
    for col in ('order_purchase_timestamp','order_delivered_customer_date','order_estimated_delivery_date'):
        frame[col] = pd.to_datetime(frame[col],errors='coerce',format='mixed')
    frame['customer_state'] = frame.customer_state.fillna('Unknown')
    # Promises are calendar dates; same-day delivery is on time regardless of hour.
    frame['delay_days'] = (frame.order_delivered_customer_date.dt.normalize()-frame.order_estimated_delivery_date.dt.normalize()).dt.days
    frame['eligible'] = (frame.order_status.eq('delivered') & frame.delay_days.notna()
                         & frame.order_purchase_timestamp.notna()
                         & (frame.order_delivered_customer_date >= frame.order_purchase_timestamp)
                         & (frame.order_estimated_delivery_date >= frame.order_purchase_timestamp.dt.normalize()))
    frame['late'] = frame.delay_days.gt(0)
    frame['month'] = frame.order_purchase_timestamp.dt.strftime('%Y-%m')
    sellers = items[['order_id','seller_id']].dropna().drop_duplicates()
    return frame, sellers


def summarize(frame, key):
    rows = frame[frame.eligible]
    result = rows.groupby(key,dropna=False).agg(
        orders=('order_id','size'), late_orders=('late','sum'),
        reviewed_orders=('review_score','count'), mean_review=('review_score','mean')).reset_index()
    result['late_rate_pct'] = result.late_orders / result.orders * 100
    return result


def seller_summary(frame, sellers):
    joined = frame[frame.eligible].merge(sellers,on='order_id',how='inner',validate='one_to_many')
    result = summarize(joined,'seller_id')
    return result.sort_values(['late_orders','orders'],ascending=False)


def memo(frame, sellers):
    valid = frame[frame.eligible]
    if valid.empty: return '# Delivery findings\n\nNo eligible delivered orders in this selection.\n'
    states = summarize(frame,'customer_state').sort_values('late_orders',ascending=False)
    seller = seller_summary(frame,sellers)
    late = valid[valid.late].review_score.dropna()
    ontime = valid[~valid.late].review_score.dropna()
    lines = ['# Olist delivery findings', '',
      f'Population: {len(valid):,} eligible delivered orders of {len(frame):,} source orders; {len(frame)-len(valid):,} excluded.',
      f'Order purchase period: {valid.order_purchase_timestamp.min().date()} to {valid.order_purchase_timestamp.max().date()}.', '',
      f'- Late deliveries: {int(valid.late.sum()):,} ({valid.late.mean()*100:.2f}%).',
      f'- Largest late-order destination: {states.iloc[0].customer_state}, with {int(states.iloc[0].late_orders):,} late orders '
      f'out of {int(states.iloc[0].orders):,} ({states.iloc[0].late_rate_pct:.2f}%).']
    if len(late) and len(ontime):
        lines.append(f'- Mean order-level review: {late.mean():.2f}/5 for late orders (n={len(late):,}) '
                     f'and {ontime.mean():.2f}/5 for on-time orders (n={len(ontime):,}); '
                     f'difference {late.mean()-ontime.mean():.2f} points.')
    if not seller.empty:
        top = seller.iloc[0]
        lines.append(f'- Seller with most associated late orders: `{top.seller_id}` '
                     f'({int(top.late_orders):,}/{int(top.orders):,}; {top.late_rate_pct:.2f}%).')
    lines += ['', '## Recommended investigation', '',
      'Start with the destination and seller groups contributing the most late orders. Compare their late rates and volumes before prioritizing an operational review. Examine carrier handoffs and promised delivery dates before attributing fault to a seller.', '',
      '## Definitions and limitations', '',
      '- Late means actual delivery calendar date is after the estimated delivery calendar date.',
      '- Eligible orders are delivered, have usable purchase/actual/estimated timestamps, and have no delivery or promise before purchase. Other orders remain excluded, not on-time.',
      '- Multiple reviews are averaged within each order first; missing reviews are excluded from review averages.',
      '- Multi-seller orders appear once per associated seller. Seller counts overlap and must not be summed to obtain total orders.',
      '- The review difference is an association, not a causal effect. This historical dataset does not establish current marketplace performance.',
      '- Figures are descriptive; no profit gains or predictive performance are claimed.', '']
    return '\n'.join(lines)
