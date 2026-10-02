import pandas as pd
from delivery.analysis import build_orders, seller_summary, summarize

def test_grain_lateness_and_missing(tmp_path):
    pd.DataFrame([
        ['a','c','delivered','2020-01-01','2020-01-03 18:00','2020-01-03'],
        ['b','c','delivered','2020-01-01','2020-01-05','2020-01-03'],
        ['x','c','canceled','2020-01-01',None,'2020-01-03']],
        columns=['order_id','customer_id','order_status','order_purchase_timestamp','order_delivered_customer_date','order_estimated_delivery_date']).to_csv(tmp_path/'olist_orders_dataset.csv',index=False)
    pd.DataFrame([['c','SP']],columns=['customer_id','customer_state']).to_csv(tmp_path/'olist_customers_dataset.csv',index=False)
    pd.DataFrame([['a',5],['a',3],['b',1]],columns=['order_id','review_score']).to_csv(tmp_path/'olist_order_reviews_dataset.csv',index=False)
    pd.DataFrame([['a','s'],['a','s'],['b','s'],['b','t']],columns=['order_id','seller_id']).to_csv(tmp_path/'olist_order_items_dataset.csv',index=False)
    orders,sellers=build_orders(tmp_path)
    assert len(orders)==3
    assert orders.set_index('order_id').loc['a','review_score']==4
    assert not orders.set_index('order_id').loc['a','late']
    summary=summarize(orders,'customer_state').iloc[0]
    assert summary.orders==2 and summary.late_orders==1 and summary.late_rate_pct==50
    assert seller_summary(orders,sellers).set_index('seller_id').loc['s','orders']==2
