import os
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import streamlit as st
import altair as alt
import pandas as pd
from delivery.analysis import build_orders, summarize, seller_summary, memo

st.set_page_config(page_title='Olist delivery decisions',layout='wide')
st.title('Olist delivery decisions')
st.caption('Historical marketplace orders · delivery reliability and customer reviews')
folder=st.sidebar.text_input('Folder containing the four Olist CSVs',os.getenv('OLIST_DATA_DIR','data/raw'))
try:
    frame,sellers=build_orders(folder)
except (FileNotFoundError,ValueError,KeyError) as error:
    st.info('Provide orders, customers, order items, and order reviews CSVs. See README for the public source and setup.')
    st.caption(str(error));st.stop()
months=sorted(frame.month.dropna().unique())
states=sorted(frame.customer_state.unique())
chosen_states=st.sidebar.multiselect('Customer states',states)
chosen_months=st.sidebar.multiselect('Purchase months',months)
if chosen_states: frame=frame[frame.customer_state.isin(chosen_states)]
if chosen_months: frame=frame[frame.month.isin(chosen_months)]
valid=frame[frame.eligible]
if valid.empty: st.info('No eligible delivered orders in this selection.');st.stop()
a,b,c=st.columns(3)
a.metric('Eligible delivered orders',f'{len(valid):,}')
b.metric('Late deliveries',f'{valid.late.mean()*100:.1f}%')
c.metric('Orders with a review',f'{valid.review_score.notna().sum():,}')
st.caption(f'{len(frame)-len(valid):,} source orders excluded. Late = delivered after the promised calendar date. Same-day delivery is on time.')
left,right=st.columns(2)
with left:
    st.subheader('Late-order volume by destination')
    by_state=summarize(frame,'customer_state').sort_values('late_orders',ascending=False)
    st.bar_chart(by_state.rename(columns={'customer_state':'State','late_orders':'Late orders'}),x='State',y='Late orders',sort=False)
    st.dataframe(by_state.round(2).rename(columns={'customer_state':'State','orders':'Orders','late_orders':'Late orders','reviewed_orders':'Reviewed orders','mean_review':'Mean review','late_rate_pct':'Late rate (%)'}),hide_index=True)
with right:
    st.subheader('Late rate over purchase months')
    monthly=summarize(frame,'month').sort_values('month')
    monthly['date']=pd.to_datetime(monthly['month'])
    chart=alt.Chart(monthly).mark_circle(size=65).encode(
        x=alt.X('date:T',title='Purchase month'), y=alt.Y('late_rate_pct:Q',title='Late rate (%)',scale=alt.Scale(domain=[0,100])),
        tooltip=[alt.Tooltip('month:N',title='Month'),alt.Tooltip('orders:Q',title='Eligible orders'),
                 alt.Tooltip('late_orders:Q',title='Late orders'),alt.Tooltip('late_rate_pct:Q',title='Late rate (%)',format='.2f')])
    st.altair_chart(chart,use_container_width=True)
    st.caption(f"{int((monthly.orders<30).sum())} months have fewer than 30 eligible orders; hover to inspect denominators.")
    st.caption('Each rate uses eligible delivered orders purchased in that month. Missing months have no observations.')
    st.subheader('Reviews: late versus on time')
    comparison=valid.assign(delivery=valid.late.map({True:'Late',False:'On time'})).groupby('delivery').agg(
        mean_review=('review_score','mean'),reviewed_orders=('review_score','count')).reset_index()
    st.bar_chart(comparison.rename(columns={'delivery':'Delivery','mean_review':'Mean review (1–5)'}),x='Delivery',y='Mean review (1–5)')
    st.dataframe(comparison.round(2),hide_index=True)
    st.caption('One average review per order; missing scores excluded. Association does not establish causation.')
st.subheader('Seller investigation queue')
minimum=st.slider('Minimum associated delivered orders',1,100,20)
by_seller=seller_summary(frame,sellers)
queue=by_seller[by_seller.orders>=minimum].head(25)
st.dataframe(queue.round(2),hide_index=True)
st.caption('Sorted by late-order volume. Multi-seller orders count once per seller; these counts overlap. This is an investigation queue, not proof of seller fault.')
st.download_button('Download filtered findings',memo(frame,sellers),'delivery-findings.md','text/markdown')
st.download_button('Download seller queue',queue.to_csv(index=False),'seller-queue.csv','text/csv')
with st.expander('Source and method'):
    st.markdown('Source: [Olist public data](https://github.com/olist/work-at-olist-data/tree/master/datasets). '
                'Only delivered orders with valid purchase, promised, and actual delivery dates are eligible. '
                'Promises/actual deliveries before purchase are excluded. Multiple review rows are averaged within each order before joining. '
                'State and month filters intersect and apply to all charts and exports; minimum seller volume applies only to the queue.')
