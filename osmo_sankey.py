# -*- coding: utf-8 -*-
"""
Created on Tue Aug 16 00:42:24 2022

@author: Jordi Garcia Ruspira
"""


import streamlit as st
import pandas as pd
import requests
import json
import time
import plotly.graph_objects as go
import random
import plotly.io as pio 
import plotly.express as px
import plotly.graph_objects as go
import datetime as dt 
import matplotlib.pyplot as plt
import numpy as np
from plotly.subplots import make_subplots
from PIL import Image 
import datetime 
import streamlit_autorefresh

try:
    st.set_page_config(
        page_title="Osmosis x Regen network - Deep dive",
        page_icon=":atom_symbol:",
        layout="wide",
        menu_items=dict(About="It's a work of Jordi"),
    )


    st.title(":atom_symbol: Osmosis x Regen network :atom_symbol:")

    im_col1, im_col2 = st.columns(2) 
    im_col1.image(
        "https://i.ibb.co/jJhVvNK/osmo.png" 
    )


    im_col2.image(
        "https://i.ibb.co/tqy8QcX/regen.jpg" 
    )

    st.text("")
    st.subheader('Dashboard by [Jordi R](https://twitter.com/RuspiTorpi/). Powered by Flipsidecrypto')
    st.text("")
    st.markdown('The goal of this dashboard is to introduce Regen Network and the news seen at Cosmoverse, and to see whether it had an effect or not on the related Osmosis pools. Appart from that I`ve displayed user behavior, retention rate and a brief introduction to mesh security.' )   
    st.markdown('This dashboard queries data from different APIs and is still a first version, so please be patient when loading. If it shows an error, refreshing the page might solve it.' )   

    st.markdown(
            f"""
    <style>
        .reportview-container .main .block-container{{
            max-width: 90%;
            padding-top: 5rem;
            padding-right: 5rem;
            padding-left: 5rem;
            padding-bottom: 5rem;
        }}
        img{{
            max-width:40%;
            margin-bottom:40px;
        }}
    </style>
    """,
            unsafe_allow_html=True,
        ) 
    pio.renderers.default = 'browser'




    API_KEY = st.secrets["API_KEY"]

    SQL_QUERY_0 = """  select to_date(block_timestamp) as date, count(distinct trader) as num_traders, count(distinct tx_id) as num_transactions from  osmosis.core.fact_swaps, table(flatten(input => pool_ids))
    where tx_status = 'SUCCEEDED'
    and block_timestamp >= '2022-07-01'
    group by date 
    order by date 

    """  

    SQL_QUERY = """  select to_date(block_timestamp) as date, count(distinct trader) as num_traders, count(distinct tx_id) as num_transactions from  osmosis.core.fact_swaps, table(flatten(input => pool_ids))
    where value = 42
    and tx_status = 'SUCCEEDED'
    and block_timestamp >= '2022-07-01'
    group by date 
    order by date 

    """  

    SQL_QUERY_2 = """  select to_date(block_timestamp) as date, count(distinct trader) as num_traders, count(distinct tx_id) as num_transactions from  osmosis.core.fact_swaps, table(flatten(input => pool_ids))
    where value = 22
    and tx_status = 'SUCCEEDED'
    and block_timestamp >= '2022-07-01'
    group by date 
    order by date 

    """  


    SQL_QUERY_3 = """  with swappers_osmo_regen as (select distinct to_date(block_timestamp) as date,  trader  from  osmosis.core.fact_swaps, table(flatten(input => pool_ids))
    where value = 42
    and tx_status = 'SUCCEEDED'
    and block_timestamp >= '2022-07-01'
    order by date ),

    num_traders_osmosis as (
    select to_date(block_timestamp) as date, count(distinct trader) as num_traders, count(distinct tx_id) as num_transactions from  osmosis.core.fact_swaps, table(flatten(input => pool_ids))
    where value = 42
    and tx_status = 'SUCCEEDED'
    and block_timestamp >= '2022-07-01'
    group by date 
    order by date ),

    num_traders_atom as (
    select to_date(block_timestamp) as date, count(distinct trader) as num_traders, count(distinct tx_id) as num_transactions from  osmosis.core.fact_swaps, table(flatten(input => pool_ids))
    where value = 22
    and tx_status = 'SUCCEEDED'
    and block_timestamp >= '2022-07-01'
    group by date 
    order by date),


    swappers_atom_regen as (select distinct to_date(block_timestamp) as date,trader  from  osmosis.core.fact_swaps, table(flatten(input => pool_ids))
    where value = 22
    and tx_status = 'SUCCEEDED'
    and block_timestamp >= '2022-07-01'
    order by date ),



    -- Common traders osmosis-regen and atom-regen 
    common_osmo_regen_atom as (
    select a.date, count(distinct a.trader ) as common_traders from swappers_osmo_regen  a 
    where (a.date, a.trader) in (select * from swappers_atom_regen) 
    group by a.date),

    -- Common traders osmosis-regen and atom-regen 
    common_atom_regen_osmo as (
    select a.date, count(distinct a.trader ) as common_traders from swappers_atom_regen  a 
    where (a.date, a.trader) in (select * from swappers_osmo_regen) 
    group by a.date)

    select a.date, a.num_traders, b.common_traders from num_traders_osmosis a 
    left join common_osmo_regen_atom b 
    on a.date = b.date 


    """  

    SQL_QUERY_4 = """  with total_val_shares as (select sum(raw_metadata[0]:"delegator_shares"/pow(10,6)) as total_shares from osmosis.core.dim_labels
    where address <> 'osmovaloper12l0vwef7w0xmkgktyqdzgd05jyq0lcuuqy2m8v'
    and raw_metadata[0]:"jailed" = 'false'
    and address in (select distinct validator_address from osmosis.core.fact_staking  )  
    )


    select address, label, raw_metadata[0]:"delegator_shares"/pow(10,6) as shares, RANK() OVER (ORDER BY shares DESC) AS RANK, (shares/b.total_shares)*100 as percentage_voting_osmosis from osmosis.core.dim_labels 
    join total_val_shares b 
    where address <> 'osmovaloper12l0vwef7w0xmkgktyqdzgd05jyq0lcuuqy2m8v'
    and raw_metadata[0]:"jailed" = 'false'
    and address in (select distinct validator_address from osmosis.core.fact_staking  )  


    """  

    #SQL_QUERY_5_AUX = """  select distinct to_date(block_timestamp) as date,  trader  from  osmosis.core.fact_swaps, table(flatten(input => pool_ids)) where tx_status = 'SUCCEEDED' and block_timestamp >= '2022-01-01' and value = '"""  


    SQL_QUERY_6 = """  
    with table_0 as (select distinct to_date(block_timestamp) as date_transaction,  trader  as from_address from  osmosis.core.fact_swaps, table(flatten(input => pool_ids)) where tx_status = 'SUCCEEDED' and block_timestamp >= '2022-01-01' and value = '22'

    ),

    table_1 as (

    Select first,
    SUM(CASE WHEN month_number = 0 THEN 1 ELSE 0 END) AS cohort_0,
    SUM(CASE WHEN month_number = 1 THEN 1 ELSE 0 END) AS cohort_1,
    SUM(CASE WHEN month_number = 2 THEN 1 ELSE 0 END) AS cohort_2,
    SUM(CASE WHEN month_number = 3 THEN 1 ELSE 0 END) AS cohort_3,
    SUM(CASE WHEN month_number = 4 THEN 1 ELSE 0 END) AS cohort_4,
    SUM(CASE WHEN month_number = 5 THEN 1 ELSE 0 END) AS cohort_5,
    SUM(CASE WHEN month_number = 6 THEN 1 ELSE 0 END) AS cohort_6,
    SUM(CASE WHEN month_number = 7 THEN 1 ELSE 0 END) AS cohort_7,
    SUM(CASE WHEN month_number = 8 THEN 1 ELSE 0 END) AS cohort_8
    from (

    select m.from_address,m.login_month,n.first as first,
    m.login_month-first as month_number  from   (SELECT
    from_address, date_part(month,date_transaction) AS login_month FROM table_0 
    GROUP BY from_address,date_part(month,date_transaction)) m,(SELECT from_address, 
    min(date_part(month,date_transaction)) AS first FROM table_0 GROUP BY from_address) 
    n where m.from_address = n.from_address) as with_month_number
    group by first order by first )

    select
    case when first = 1 then 'January'
    when first = 2 then 'February'
    when first = 3 then 'March'
    when first = 4 then 'April'
    when first = 5 then 'May'
    when first = 6 then 'June'
    when first = 7 then 'July'
    when first = 8 then 'August'
    when first = 9 then 'September'
    when first = 10 then 'October'
    when first = 11 then 'November'
    when first = 12 then 'December'
    else 'other'
    end as month, (a.cohort_1/a.cohort_0)*100 as cohort_index_1, 
    (a.cohort_2/a.cohort_0)*100 as cohort_index_2,
    (a.cohort_3/a.cohort_0)*100 as cohort_index_3,
    (a.cohort_4/a.cohort_0)*100 as cohort_index_4,
    (a.cohort_5/a.cohort_0)*100 as cohort_index_5,
    (a.cohort_6/a.cohort_0)*100 as cohort_index_6,
    (a.cohort_7/a.cohort_0)*100 as cohort_index_7,
    (a.cohort_8/a.cohort_0)*100 as cohort_index_8
    from table_1 a 
    """  


    SQL_QUERY_7 = """  
    with table_0 as (select distinct to_date(block_timestamp) as date_transaction,  trader  as from_address from  osmosis.core.fact_swaps, table(flatten(input => pool_ids)) where tx_status = 'SUCCEEDED' and block_timestamp >= '2022-01-01' and value = '42'

    ),

    table_1 as (

    Select first,
    SUM(CASE WHEN month_number = 0 THEN 1 ELSE 0 END) AS cohort_0,
    SUM(CASE WHEN month_number = 1 THEN 1 ELSE 0 END) AS cohort_1,
    SUM(CASE WHEN month_number = 2 THEN 1 ELSE 0 END) AS cohort_2,
    SUM(CASE WHEN month_number = 3 THEN 1 ELSE 0 END) AS cohort_3,
    SUM(CASE WHEN month_number = 4 THEN 1 ELSE 0 END) AS cohort_4,
    SUM(CASE WHEN month_number = 5 THEN 1 ELSE 0 END) AS cohort_5,
    SUM(CASE WHEN month_number = 6 THEN 1 ELSE 0 END) AS cohort_6,
    SUM(CASE WHEN month_number = 7 THEN 1 ELSE 0 END) AS cohort_7,
    SUM(CASE WHEN month_number = 8 THEN 1 ELSE 0 END) AS cohort_8
    from (

    select m.from_address,m.login_month,n.first as first,
    m.login_month-first as month_number  from   (SELECT
    from_address, date_part(month,date_transaction) AS login_month FROM table_0 
    GROUP BY from_address,date_part(month,date_transaction)) m,(SELECT from_address, 
    min(date_part(month,date_transaction)) AS first FROM table_0 GROUP BY from_address) 
    n where m.from_address = n.from_address) as with_month_number
    group by first order by first )

    select
    case when first = 1 then 'January'
    when first = 2 then 'February'
    when first = 3 then 'March'
    when first = 4 then 'April'
    when first = 5 then 'May'
    when first = 6 then 'June'
    when first = 7 then 'July'
    when first = 8 then 'August'
    when first = 9 then 'September'
    when first = 10 then 'October'
    when first = 11 then 'November'
    when first = 12 then 'December'
    else 'other'
    end as month, (a.cohort_1/a.cohort_0)*100 as cohort_index_1, 
    (a.cohort_2/a.cohort_0)*100 as cohort_index_2,
    (a.cohort_3/a.cohort_0)*100 as cohort_index_3,
    (a.cohort_4/a.cohort_0)*100 as cohort_index_4,
    (a.cohort_5/a.cohort_0)*100 as cohort_index_5,
    (a.cohort_6/a.cohort_0)*100 as cohort_index_6,
    (a.cohort_7/a.cohort_0)*100 as cohort_index_7,
    (a.cohort_8/a.cohort_0)*100 as cohort_index_8
    from table_1 a """  


    # Unique new users pool 42
    SQL_QUERY_8 = """  select 
    TO_CHAR(date_trunc('day', first_appearance), 'YYYY-MM-DD') AS daily, 
    COUNT(DISTINCT trader) AS unique_new_users,
    sum(unique_new_users) over (order by daily) as cumulative_new_users_daily
    from (SELECT t.*,
          MIN(date_trunc('day', block_timestamp)) OVER(PARTITION BY trader) AS first_appearance
          FROM osmosis.core.fact_swaps t,  table(flatten(input => pool_ids))
    where value = 42
      and   to_date(block_timestamp) >= '2022-07-01'
         ) t
    GROUP BY daily 
      """  



    # Unique new users pool 22
    SQL_QUERY_9 = """  select 
    TO_CHAR(date_trunc('day', first_appearance), 'YYYY-MM-DD') AS daily, 
    COUNT(DISTINCT trader) AS unique_new_users,
    sum(unique_new_users) over (order by daily) as cumulative_new_users_daily
    from (SELECT t.*,
          MIN(date_trunc('day', block_timestamp)) OVER(PARTITION BY trader) AS first_appearance
          FROM osmosis.core.fact_swaps t,  table(flatten(input => pool_ids))
    where value = 22
      and   to_date(block_timestamp) >= '2022-07-01'
         ) t
    GROUP BY daily 
      """  

    # Unique new users OSMOSIS overall
    SQL_QUERY_10 = """  select 
    TO_CHAR(date_trunc('day', first_appearance), 'YYYY-MM-DD') AS daily, 
    COUNT(DISTINCT trader) AS unique_new_users,
    sum(unique_new_users) over (order by daily) as cumulative_new_users_daily
    from (SELECT t.*,
          MIN(date_trunc('day', block_timestamp)) OVER(PARTITION BY trader) AS first_appearance
          FROM osmosis.core.fact_swaps t,  table(flatten(input => pool_ids))
    where  to_date(block_timestamp) >= '2022-07-01'
         ) t
    GROUP BY daily 
      """  

    # Unique new users adding liquidity pool 42
    SQL_QUERY_11 = """  select 
    TO_CHAR(date_trunc('day', first_appearance), 'YYYY-MM-DD') AS daily, 
    COUNT(DISTINCT liquidity_provider_address) AS unique_new_users,
    sum(unique_new_users) over (order by daily) as cumulative_new_users_daily
    from (SELECT t.*,
          MIN(date_trunc('day', block_timestamp)) OVER(PARTITION BY liquidity_provider_address) AS first_appearance
          FROM  osmosis.core.fact_liquidity_provider_actions t
    where   to_date(block_timestamp) >= '2022-07-01'
    and pool_id = '42'

         ) t
    GROUP BY daily  
      """  

    # Unique new users adding liquidity pool 22
    SQL_QUERY_12 = """ select 
    TO_CHAR(date_trunc('day', first_appearance), 'YYYY-MM-DD') AS daily, 
    COUNT(DISTINCT liquidity_provider_address) AS unique_new_users,
    sum(unique_new_users) over (order by daily) as cumulative_new_users_daily
    from (SELECT t.*,
          MIN(date_trunc('day', block_timestamp)) OVER(PARTITION BY liquidity_provider_address) AS first_appearance
          FROM  osmosis.core.fact_liquidity_provider_actions t
    where   to_date(block_timestamp) >= '2022-07-01'
    and pool_id = '22'

         ) t
    GROUP BY daily  
      """  

    # Unique new users OSMOSIS overall
    SQL_QUERY_13 = """ select 
    TO_CHAR(date_trunc('day', first_appearance), 'YYYY-MM-DD') AS daily, 
    COUNT(DISTINCT liquidity_provider_address) AS unique_new_users,
    sum(unique_new_users) over (order by daily) as cumulative_new_users_daily
    from (SELECT t.*,
          MIN(date_trunc('day', block_timestamp)) OVER(PARTITION BY liquidity_provider_address) AS first_appearance
          FROM  osmosis.core.fact_liquidity_provider_actions t
    where   to_date(block_timestamp) >= '2022-07-01'

         ) t
    GROUP BY daily  
      """


    # Top 10 trades pool Regen - Osmo 30/09
    SQL_QUERY_14 = """  select tx_id, trader,  case when from_currency = 'uosmo' then 'Osmo'
      else 'Regen' 
      end as from_currency, from_amount/pow(10, from_decimal) as from_amount, 
      case when to_currency = 'uosmo' then 'Osmo'
      else 'Regen' 
      end as to_currency, 
       to_amount/pow(10, to_decimal) as to_amount  from  osmosis.core.fact_swaps a , table(flatten(input => pool_ids))  
    where value = 42
    and tx_status = 'SUCCEEDED'
    and to_date(block_timestamp) = '2022-09-30'
    and (from_currency = 'ibc/1DCC8A6CB5689018431323953344A9F6CC4D0BFB261E88C9F7777372C10CD076' or to_currency = 'ibc/1DCC8A6CB5689018431323953344A9F6CC4D0BFB261E88C9F7777372C10CD076' or from_currency = 'uosmo' or to_currency = 'usomo')
    order by from_amount desc 
    limit 10 
      """

    # Top 10 traders pool Regen - Osmo 30/09 - first time?
    SQL_QUERY_15 = """ with top_10_trades as ( select tx_id, trader as user ,  case when from_currency = 'uosmo' then 'Osmo'
      else 'Regen' 
      end as from_currency, from_amount/pow(10, from_decimal) as from_amount, 
      case when to_currency = 'uosmo' then 'Osmo'
      else 'Regen' 
      end as to_currency, 
       to_amount/pow(10, to_decimal) as to_amount, 
      rank() over (order by to_amount desc) as Rank from osmosis.core.fact_swaps a , table(flatten(input => pool_ids))  
    where value = 42
    and tx_status = 'SUCCEEDED'
    and to_date(block_timestamp) = '2022-09-30'
    and (from_currency = 'ibc/1DCC8A6CB5689018431323953344A9F6CC4D0BFB261E88C9F7777372C10CD076' or to_currency = 'ibc/1DCC8A6CB5689018431323953344A9F6CC4D0BFB261E88C9F7777372C10CD076' or from_currency = 'uosmo' or to_currency = 'usomo')
    order by from_amount desc 
    limit 10 )

    select trader,  min(block_timestamp) as first_date from   osmosis.core.fact_swaps  , table(flatten(input => pool_ids))  
    where value = 42
    and tx_status = 'SUCCEEDED'
    and trader in (select distinct user from  top_10_trades)
    group by trader   
      """

    # Unique regen traders since 09-01
    SQL_QUERY_16 = """ with regen_trader as ( select distinct trader from osmosis.core.fact_swaps a , table(flatten(input => pool_ids))  
    where value = 42
    and tx_status = 'SUCCEEDED'
    and to_date(block_timestamp) >= '2022-09-01')

    select count(*) unique_regen_traders from regen_trader  
      """


    # Regen traders -> other pools swaps number 
    SQL_QUERY_17 = """ with regen_trader as ( select distinct trader from osmosis.core.fact_swaps a , table(flatten(input => pool_ids))  
    where value = 42
    and tx_status = 'SUCCEEDED'
    and to_date(block_timestamp) >= '2022-09-01')

    select value as POOL_ID, count(distinct tx_id) as num_transactions from osmosis.core.fact_swaps a , table(flatten(input => pool_ids))  
    where trader in (select * from regen_trader )
    group by value 
    order by num_transactions desc 
      """



    TTL_MINUTES = 15
    # return up to 100,000 results per GET request on the query id
    PAGE_SIZE = 100000
    # return results of page 1
    PAGE_NUMBER = 1

    def create_query(SQL_QUERY):
        r = requests.post(
            'https://node-api.flipsidecrypto.com/queries', 
            data=json.dumps({
                "sql": SQL_QUERY,
                "ttlMinutes": TTL_MINUTES
            }),
            headers={"Accept": "application/json", "Content-Type": "application/json", "x-api-key": API_KEY},
        )
        if r.status_code != 200:
            raise Exception("Error creating query, got response: " + r.text + "with status code: " + str(r.status_code))

        return json.loads(r.text)    


    def get_query_results(token):
        r = requests.get(
            'https://node-api.flipsidecrypto.com/queries/{token}?pageNumber={page_number}&pageSize={page_size}'.format(
              token=token,
              page_number=PAGE_NUMBER,
              page_size=PAGE_SIZE
            ),
            headers={"Accept": "application/json", "Content-Type": "application/json", "x-api-key": API_KEY}
        )
        if r.status_code != 200:
            raise Exception("Error getting query results, got response: " + r.text + "with status code: " + str(r.status_code))

        data = json.loads(r.text)
        if data['status'] == 'running':
            time.sleep(10)
            return get_query_results(token)

        return data

    query = create_query(SQL_QUERY_0)
    token = query.get('token')
    data0 = get_query_results(token)
    # Pool Osmo - Regen- Number of swaps and traders
    df0 = pd.DataFrame(data0['results'], columns = ['DATE', 'NUM_TRADERS','NUM_TRANSACTIONS']) 
    df0 = df0[(df0['DATE'] > '2022-09-01')]



    query = create_query(SQL_QUERY)
    token = query.get('token')
    data1 = get_query_results(token)
    # Pool Osmo - Regen- Number of swaps and traders
    df1 = pd.DataFrame(data1['results'], columns = ['DATE', 'NUM_TRADERS','NUM_TRANSACTIONS']) 
    df1 = df1[(df1['DATE'] > '2022-09-01')]


    query = create_query(SQL_QUERY_2)
    token = query.get('token')
    data2 = get_query_results(token)
    # Pool Atom - Regen- Number of swaps and traders
    df2 = pd.DataFrame(data2['results'], columns = ['DATE', 'NUM_TRADERS','NUM_TRANSACTIONS']) 
    df2 = df2[(df2['DATE'] > '2022-09-01')]

    query = create_query(SQL_QUERY_3)
    token = query.get('token')
    data3 = get_query_results(token)
    # Common traders - Traders that trade both on Osmo-Regen and Atom-Regen
    df3 = pd.DataFrame(data3['results'], columns = ['DATE', 'NUM_TRADERS','COMMON_TRADERS']) 
    df3 = df3[(df3['DATE'] > '2022-09-01')]

    query = create_query(SQL_QUERY_4)
    token = query.get('token')
    data4 = get_query_results(token)
    # List of Osmosis validators

    df4 = pd.DataFrame(data4['results'], columns =  ['ADDRESS', 'LABEL','SHARES','RANK', 'PERCENTAGE_VOTING_OSMOSIS']) 


    st.header("")
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
        [
            "Introduction to Regen network and Osmosis - News on Cosmoverse",
            "Price and Volume",
            "Number of users and unique new users",
            "Cohort analysis and other preferred pools",
            "Mesh security",
            "About",
        ])


    regen_osmo_json = requests.get('https://api-osmosis.imperator.co/pools/v2/volume/42/chart').json()
    regen_osmo_df = pd.DataFrame(regen_osmo_json) 
    regen_osmo_df = regen_osmo_df[(regen_osmo_df['time'] > '2022-09-01')]
    regen_atom_json = requests.get('https://api-osmosis.imperator.co/pools/v2/volume/22/chart').json()
    regen_atom_df = pd.DataFrame(regen_atom_json) 
    regen_atom_df = regen_atom_df[(regen_atom_df['time'] > '2022-09-01')]

    regen_osmo_liq_json = requests.get('https://api-osmosis.imperator.co/pools/v2/liquidity/42/chart').json()
    regen_osmo_liq_df = pd.DataFrame(regen_osmo_liq_json) 
    regen_osmo_liq_df = regen_osmo_liq_df[(regen_osmo_liq_df['time'] > '2022-09-01')]
    regen_atom_liq_json = requests.get('https://api-osmosis.imperator.co/pools/v2/liquidity/22/chart').json()
    regen_atom_liq_df = pd.DataFrame(regen_atom_liq_json) 
    regen_atom_liq_df = regen_atom_liq_df[(regen_atom_liq_df['time'] > '2022-09-01')]


    # List of Regen validators active
    validators_regen = requests.get('http://mainnet.regen.network:1317/cosmos/staking/v1beta1/validators?status=BOND_STATUS_BONDED').json()
    total_staking_regen = requests.get('http://mainnet.regen.network:1317/cosmos/staking/v1beta1/pool').json()
    historical_price_regen = requests.get('https://api-osmosis.imperator.co/tokens/v2/historical/regen/chart?tf=1440').json()

    df_historical_price_regen = pd.DataFrame(historical_price_regen)
    df_historical_price_regen = df_historical_price_regen.sort_values(by="time")
    newtime = []
    for i in range(len(df_historical_price_regen['time'])):
        newtime.append(datetime.datetime.fromtimestamp(df_historical_price_regen['time'][i]).strftime('%c'))

    df_historical_price_regen['new_time'] = newtime
    df_historical_price_regen['new_time'] =  pd.to_datetime(df_historical_price_regen['new_time'])

    df_historical_price_regen = df_historical_price_regen[df_historical_price_regen['new_time'] >= '2022-09-01']


    historical_price_osmo = requests.get('https://api-osmosis.imperator.co/tokens/v2/historical/osmo/chart?tf=1440').json()

    df_historical_price_osmo = pd.DataFrame(historical_price_osmo)
    df_historical_price_osmo = df_historical_price_osmo.sort_values(by="time")
    newtime = []
    for i in range(len(df_historical_price_osmo['time'])):
        newtime.append(datetime.datetime.fromtimestamp(df_historical_price_osmo['time'][i]).strftime('%c'))

    df_historical_price_osmo['new_time'] = newtime
    df_historical_price_osmo['new_time'] =  pd.to_datetime(df_historical_price_osmo['new_time'])

    df_historical_price_osmo = df_historical_price_osmo[df_historical_price_osmo['new_time'] >= '2022-09-01']



    val_reg = []
    val_reg_shares = []
    val_reg_percentage = []

    for i in range(len(validators_regen["validators"])):

        val_reg.append(validators_regen["validators"][i]["description"]["moniker"])
        val_reg_shares.append(float(validators_regen["validators"][i]["delegator_shares"])/1000000) 
        val_reg_percentage.append(((float(validators_regen["validators"][i]["delegator_shares"])/1000000)/(float(total_staking_regen["pool"]['bonded_tokens'])/1000000))*100)


    val_reg = pd.Series( (v for v in val_reg), name='LABEL' )    
    val_reg_shares = pd.Series ((v for v in val_reg_shares), name = 'VALIDATOR_SHARES' )
    val_reg_percentage = pd.Series ((v for v in val_reg_percentage), name = 'VALIDATOR_VOTING_PERCENTAGE_REGEN' )
    val_reg_total = pd.concat([val_reg, val_reg_shares, val_reg_percentage], axis=1).sort_values(by="VALIDATOR_VOTING_PERCENTAGE_REGEN", ascending = False)

    #val_reg[val_reg.str.contains("cito")]     
    Inner_join = pd.merge(df4[['LABEL','PERCENTAGE_VOTING_OSMOSIS']], 
                         val_reg_total, 
                         on ='LABEL', 
                         how ='inner')

    #This part here is to get a dictionary with pool_id and the pair. 
    pairs_summary = 'https://api-osmosis.imperator.co/pairs/v1/summary'
    pairs_summary_json = requests.get(pairs_summary).json()
    pairs_summary_df = pd.DataFrame(pairs_summary_json)
    pairs_summary_data = pairs_summary_df['data'] 
    pairs = []

    for i in range(0, len(pairs_summary_data),1):

        d = {
              'POOL_ID': pairs_summary_data[i]['pool_id'],
              'pair':pairs_summary_data[i]['base_symbol']+"-"+pairs_summary_data[i]['quote_symbol'],
              'volume_api':"https://api-osmosis.imperator.co/pools/v2/volume/"+pairs_summary_data[i]['pool_id']+"/chart"
        } 

        pairs.append(d)

    pairs = pd.DataFrame(pairs)

    with tab1:
        st.subheader("Introduction - Overview")

        st.markdown("---")
        st.write("As described in the Osmosis documentation, Osmosis is an advanced automated market maker (AMM) protocol that allows developers to build customized AMMs with sovereign liquidity pools. Built using the Cosmos SDK, Osmosis utilizes Inter-Blockchain Communication (IBC) to enable cross-chain transactions. Osmosis can be seen as something that can connects all the various dApps on Cosmos. Amongst other assets, users can also lock Regen network native token (REGEN) in pools on Osmosis, which is the object of study in this dashboard.")

        st.write("Regen Ledger is a sovereign, proof-of-stake blockchain built on the Cosmos SDK. REGEN is a staking token, providing Regen Ledger with utility - namely, fees, gas, governance and security. REGEN token is designed to ensure utility for ecological data and climate markets. Regen Network is governed as a public blockchain by token holders. REGEN token will accrue value from transaction fees on ecological assets and other transactions originated and secured on-chain.")

        st.write("Under the current capitalist market, nations find it hard to achieve their goals on sustainability because they are not financially incentivised to support sustainable iniciatives. One popular solution are carbon credits. They allow companies to emit a certain amount of carbon dioxide or other greenhouse gases. Companies with high pollution can continue to pollute up to a certain limit, with this level being reduced periodically. The company might sell any unused credits to other companies that 'need' to emit more. They can also make money by reducing their emissions and selling their excess allowances. ")

        st.write("The problem is that getting verified for carbon credits can take up to 3 years, and the procedure is costly, making it attractive for big companies. Most small businesses and farms can't afford the process, but may farms wotrdwide provide very valuable ecological services like:")

        st.markdown("* Creating biodiversity")
        st.markdown("* Producing clean water")
        st.markdown("* Sequestering carbon") 

        st.write("Incentivising these farms is crucial to fight climate change. This is where regen network comes into play. ")

        st.write("Regen Network is a PoS blockchain that leverages the Cosmos SDK and is IBC enabled. The blockchain tracks, verifies and rewards positive changes to ecologigal systems, and incentivizes farmers to provide valuable ecological services. Regen Network is also a marketplace for carbon credits, where corporations can buy them from farmers worldwide. ")

        st.write("On one side, a farm which sequesters vasts amounts of carbon could log into the regen network website, and enter crucial information about the service it provides (in this case, sequestering carbon). Through satellites and ground-proof data, Regen Network can ensure a fast and inexpensive verification of the land, which then gets stored on the regen blockchain, and corporations can buy carbon credits from the farm. This is how both parties profit. ")

        st.write("Regarding the Regen token, the native Regen token is used for staking to secure the blockchain and earn rewards, it serves as a governance token and is used to pay for fees on the network. Also, in order to mint credits you need to burn Regen tokens. ")

        st.markdown("---")
        st.subheader("News on Cosmoverse: Nature Carbon Ton (NCT) and Marketplace")

        st.markdown("---")
        st.image(
        "https://i.ibb.co/gJJfZRP/regen-nct.jpg" 
    )

        st.write("If someone has been following up with Regen updates during the last months, NCTs might sound familiar, but they are expected to launch very soon and were also big news from the Regen team during Cosmoverse, introducing the term and product to users who might not have heard about it yet.")

        st.write("NCT stands for Nature Carbon Ton, a premium digital carbon basket token of nature-based projects, which will be launched by the Regen Network community in cooperation with Osmosis. At least two new pools have been announced, both with Regen and Osmo. ")
        st.write("NCTs will be minted on the Regen Ledger, utilizing three native features: ecocredit module, bank module and baskets module. There's many more to explore and it's exciting to see how this new tool will develop. ")

        st.write("Over the last year Regen network has been working on buying and selling and originating carbon assets over the counter off chain over the last year, because the marketplace was not yet build. As stated by Gregory in Cosmoverse, safety over liveness; resiliant technology takes time. Through the new marketplace, this over the counter buys and sells will be done in the marketplace (expected and announced to launch during October). ")



        st.markdown("---")
        st.error("Volume and user metrics in the next tab...")

    with tab2:

        st.subheader("Price, volume and liquidity")
        st.markdown("---")

        st.info(
            "This section is dedicated to displaying price, volume and liquidity of the Regen pools on Osmosis."
        )
        st.write("A set of different metrics to show are:")  
        st.markdown("* **REGEN** and **OSMO** token price action")
        st.markdown("* **Daily users** swapping on Osmosis and Regen pools")
        st.markdown("* **Daily NEW users** swapping on Osmosis and Regen pools")
        st.markdown("* **Daily transactions** swapping on Osmosis and Regen pools")
        st.markdown("* **Liquidity** of Regen pools")
        st.markdown("* Insights on users adding/removing **liquidity** on Regen pools")

        st.markdown("---")
        st.subheader("Price")
        st.markdown("---")
        st.write("The first thing we can do is take a look at the price of both Regen and Osmo since September, to get a sense of the correlation between the price of both assets (if any). I've shown in the same chart the Cosmoverse event.")

        fig = go.Figure(data=[go.Candlestick(x=df_historical_price_regen['new_time'],
                        open=df_historical_price_regen['open'], high=df_historical_price_regen['high'],
                        low=df_historical_price_regen['low'], close=df_historical_price_regen['close'])
                             ])
        fig.add_vrect(
            x0="2022-09-26",
            x1="2022-09-29",
            annotation_text="Cosmoverse",
            annotation_position="inside top left",
            annotation_textangle=90,
            annotation_font_size=16,
            annotation_font_color="gray",
            fillcolor="Green",
            opacity=0.3,
            line_width=0,
            line_dash="dash",
        )
        fig.update_layout(xaxis_rangeslider_visible=False, title="Regen daily price",
        xaxis_title="Date",
        yaxis_title="Price (USD)")
        st.plotly_chart(fig, use_container_width=True) 

        fig = go.Figure(data=[go.Candlestick(x=df_historical_price_osmo['new_time'],
                        open=df_historical_price_osmo['open'], high=df_historical_price_osmo['high'],
                        low=df_historical_price_osmo['low'], close=df_historical_price_osmo['close'])
                             ])
        fig.add_vrect(
            x0="2022-09-26",
            x1="2022-09-29",
            annotation_text="Cosmoverse",
            annotation_position="inside top left",
            annotation_textangle=90,
            annotation_font_size=16,
            annotation_font_color="gray",
            fillcolor="Green",
            opacity=0.3,
            line_width=0,
            line_dash="dash",
        )

        fig.update_layout(xaxis_rangeslider_visible=False, title="Osmo daily price",
        xaxis_title="Date",
        yaxis_title="Price (USD)")
        st.plotly_chart(fig, use_container_width=True) 


        st.write("There's not much to say regarding the price; both assets went down in price during the event, but nothing really significant. The time scales set here are starting on September 1 to set a relatively new timeframe, and after the event the REGEN token price has increased by a discrete amount. On the other side, OSMO price has decreased, but again not by a significant amount.")
        st.markdown("---")
        st.subheader("Volume")


        st.markdown("---")

        st.write("We can also see that volume did increase for Regen pools during the Cosmoverse event. The main event of regen was on the main pannel the 27th of September, marked also in the following charts.")


        osmo_col1, atom_col2 = st.columns(2)
        osmo_col1.markdown("""---""")
        osmo_col1.write("Regen - Osmo pool daily volume")
        osmo_col1.markdown("""---""")
        osmo_col1.text("")


        fig = px.bar(regen_osmo_df, y='value', x='time')#, text='Daily Volume - Pool Regen-Atom')

        fig.add_vrect(
            x0="2022-09-26",
            x1="2022-09-29",
            annotation_text="Cosmoverse",
            annotation_position="inside top left",
            annotation_textangle=90,
            annotation_font_size=16,
            annotation_font_color="gray",
            fillcolor="Green",
            opacity=0.3,
            line_width=0,
            line_dash="dash",
        )
        fig.add_vrect(
            x0="2022-09-27",
            x1="2022-09-28",
            annotation_text="Regen cosmoverse talk",
            annotation_position="inside top right",
            annotation_textangle=90,
            annotation_font_size=16,
            annotation_font_color="orange",
            fillcolor="yellow",
            line_color="white",
            opacity=0.25,
            line_width=2,
            line_dash="solid",
        )

        fig.update_traces( marker_color='#2E8B57')
        fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide', xaxis_title="Date",
        yaxis_title="Volume (USD)") 
        osmo_col1.plotly_chart(fig, use_container_width=True) 


        atom_col2.markdown("""---""")
        atom_col2.write("Regen - Atom pool daily volume")
        atom_col2.markdown("""---""")
        atom_col2.text("")

        fig = px.bar(regen_atom_df, y='value', x='time')#, text='Daily Volume - Pool Regen-Atom')
        fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
        fig.add_vrect(
            x0="2022-09-26",
            x1="2022-09-29",
            annotation_text="Cosmoverse",
            annotation_position="inside top left",
            annotation_textangle=90,
            annotation_font_size=16,
            annotation_font_color="gray",
            fillcolor="Green",
            opacity=0.3,
            line_width=0,
            line_dash="dash",
        )
        fig.add_vrect(
            x0="2022-09-27",
            x1="2022-09-28",
            annotation_text="Regen cosmoverse talk",
            annotation_position="inside top right",
            annotation_textangle=90,
            annotation_font_size=16,
            annotation_font_color="orange",
            fillcolor="yellow",
            line_color="white",
            opacity=0.25,
            line_width=2,
            line_dash="solid",
        )

        fig.update_traces( marker_color='#2E8B57')
        fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide', xaxis_title="Date",
        yaxis_title="Volume (USD)") 
        atom_col2.plotly_chart(fig, use_container_width=True) 





        ####################################################################################################################

        st.markdown("---")


        st.subheader("Liquidity")
        st.markdown("---")

        st.info(
            "User growth on Osmosis: LP addresses"
        )
        st.markdown("---")
        st.write("When it comes to liquidity, we can look both at number of users adding/removing liquidity and the overall amount of liquidity deposited on the pools. For Regen pools, as we can see in the figures below there was not too much going on during the event and post-event. ")

        query = create_query(SQL_QUERY_13)
        token = query.get('token')
        data_user_osmo_lp = get_query_results(token) 
        df_user_osmo_lp = pd.DataFrame(data_user_osmo_lp['results'], columns = ['DAILY', 'UNIQUE_NEW_USERS','CUMULATIVE_NEW_USERS_DAILY']) 
        df_user_osmo_lp = df_user_osmo_lp.sort_values(by="DAILY")  
        df_user_osmo_lp = df_user_osmo_lp[df_user_osmo_lp['DAILY'] >= '2022-09-01']     

        fig = make_subplots(specs=[[{"secondary_y": True}]])

        fig.add_trace(
            go.Scatter(x=df_user_osmo_lp['DAILY'], y=df_user_osmo_lp['CUMULATIVE_NEW_USERS_DAILY'], name="Cumulative new users adding liquidity"),
            secondary_y=True,
        )

        fig.add_trace(
            go.Bar(x=df_user_osmo_lp['DAILY'], y=df_user_osmo_lp['UNIQUE_NEW_USERS'], name="Daily new users adding/removing liquidity"),
            secondary_y=False,
        )
        fig.add_vrect(
            x0="2022-09-26",
            x1="2022-09-29",
            annotation_text="Cosmoverse",
            annotation_position="inside top left",
            annotation_textangle=90,
            annotation_font_size=16,
            annotation_font_color="gray",
            fillcolor="Green",
            opacity=0.3,
            line_width=0,
            line_dash="dash",
        )
        # Add figure title

        fig.update_traces( marker_color='#7B68EE')
        fig.update_layout(
            title_text="Daily and cumulative new users adding/removing liquidity on Osmosis"
        )

        # Set x-axis title
        fig.update_xaxes(title_text="Date")

        # Set y-axes titles
        fig.update_yaxes(title_text="Number of users", secondary_y=False)
        fig.update_yaxes(title_text="Number of users", secondary_y=True)


        st.plotly_chart(fig, use_container_width=True) 


        ####################################################################################################################

        osmo_col_second, atom_col_second = st.columns(2)
        osmo_col_second.markdown("""---""")
        osmo_col_second.write("Regen - Osmo pool user growth - LPs")
        osmo_col_second.markdown("""---""")
        osmo_col_second.text("")


        query = create_query(SQL_QUERY_11)
        token = query.get('token')
        data_user_lp_42 = get_query_results(token) 
        df_user_lp_42 = pd.DataFrame(data_user_lp_42['results'], columns = ['DAILY', 'UNIQUE_NEW_USERS','CUMULATIVE_NEW_USERS_DAILY']) 
        df_user_lp_42 = df_user_lp_42.sort_values(by="DAILY")
        df_user_lp_42 = df_user_lp_42[df_user_lp_42['DAILY'] >= '2022-09-01']     
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        fig.add_trace(
            go.Scatter(x=df_user_lp_42['DAILY'], y=df_user_lp_42['CUMULATIVE_NEW_USERS_DAILY'], name="Cumulative new users"),
            secondary_y=True,
        )

        fig.add_trace(
            go.Bar(x=df_user_lp_42['DAILY'], y=df_user_lp_42['UNIQUE_NEW_USERS'], name="Daily new users"),
            secondary_y=False,
        )
        fig.add_vrect(
            x0="2022-09-26",
            x1="2022-09-29",
            annotation_text="Cosmoverse",
            annotation_position="inside top left",
            annotation_textangle=90,
            annotation_font_size=16,
            annotation_font_color="gray",
            fillcolor="Green",
            opacity=0.3,
            line_width=0,
            line_dash="dash",
        )
        fig.add_vrect(
            x0="2022-09-27",
            x1="2022-09-28",
            annotation_text="Regen cosmoverse talk",
            annotation_position="inside top right",
            annotation_textangle=90,
            annotation_font_size=16,
            annotation_font_color="orange",
            fillcolor="yellow",
            line_color="white",
            opacity=0.25,
            line_width=2,
            line_dash="solid",
        )
        # Add figure title

        fig.update_traces( marker_color='#2E8B57')
        fig.update_layout(
            title_text="Daily and cumulative new users adding/removing liquidity on Regen - Osmo pool"
        )

        # Set x-axis title
        fig.update_xaxes(title_text="Date")

        # Set y-axes titles
        fig.update_yaxes(title_text="Number of users", secondary_y=False)
        fig.update_yaxes(title_text="Number of users", secondary_y=True)


        osmo_col_second.plotly_chart(fig, use_container_width=True) 


        ####################################################################################################################

        atom_col_second.markdown("""---""")
        atom_col_second.write("Regen - Osmo pool user growth - LPs")
        atom_col_second.markdown("""---""")
        atom_col_second.text("")



        query = create_query(SQL_QUERY_12)
        token = query.get('token')
        data_user_lp_22 = get_query_results(token) 
        df_user_lp_22 = pd.DataFrame(data_user_lp_22['results'], columns = ['DAILY', 'UNIQUE_NEW_USERS','CUMULATIVE_NEW_USERS_DAILY']) 
        df_user_lp_22 = df_user_lp_22.sort_values(by="DAILY")
        df_user_lp_22 = df_user_lp_22[df_user_lp_22['DAILY'] >= '2022-09-01']     

        fig = make_subplots(specs=[[{"secondary_y": True}]])

        fig.add_trace(
            go.Scatter(x=df_user_lp_22['DAILY'], y=df_user_lp_22['CUMULATIVE_NEW_USERS_DAILY'], name="Cumulative new users"),
            secondary_y=True,
        )

        fig.add_trace(
            go.Bar(x=df_user_lp_22['DAILY'], y=df_user_lp_22['UNIQUE_NEW_USERS'], name="Daily new users"),
            secondary_y=False,
        )
        fig.add_vrect(
            x0="2022-09-26",
            x1="2022-09-29",
            annotation_text="Cosmoverse",
            annotation_position="inside top left",
            annotation_textangle=90,
            annotation_font_size=16,
            annotation_font_color="gray",
            fillcolor="Green",
            opacity=0.3,
            line_width=0,
            line_dash="dash",
        )
        fig.add_vrect(
            x0="2022-09-27",
            x1="2022-09-28",
            annotation_text="Regen cosmoverse talk",
            annotation_position="inside top right",
            annotation_textangle=90,
            annotation_font_size=16,
            annotation_font_color="orange",
            fillcolor="yellow",
            line_color="white",
            opacity=0.25,
            line_width=2,
            line_dash="solid",
        )
        # Add figure title
        fig.update_traces( marker_color='#2E8B57')
        fig.update_layout(
            title_text="Daily and cumulative new users adding/removing liquidity on Regen - Atom pool"
        )

        # Set x-axis title
        fig.update_xaxes(title_text="Date")

        # Set y-axes titles
        fig.update_yaxes(title_text="Number of users", secondary_y=False)
        fig.update_yaxes(title_text="Number of users", secondary_y=True)


        atom_col_second.plotly_chart(fig, use_container_width=True) 


       ####################################################################################################################



        osmo_col3, atom_col4 = st.columns(2)

        osmo_col3.markdown("""---""")
        osmo_col3.write("Regen - Osmo pool daily liquidity")
        osmo_col3.markdown("""---""")
        osmo_col3.text("")

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(x=regen_osmo_liq_df['time'], y=regen_osmo_liq_df['value'], name="yaxis data", fill='tozeroy') 
        ) #, text='Daily Volume - Pool Regen-Atom')

        fig.add_vrect(
            x0="2022-09-26",
            x1="2022-09-29",
            annotation_text="Cosmoverse",
            annotation_position="inside top left",
            annotation_textangle=90,
            annotation_font_size=16,
            annotation_font_color="gray",
            fillcolor="Green",
            opacity=0.3,
            line_width=0,
            line_dash="dash",
        )
        fig.add_vrect(
            x0="2022-09-27",
            x1="2022-09-28",
            annotation_text="Regen cosmoverse talk",
            annotation_position="inside top right",
            annotation_textangle=90,
            annotation_font_size=16,
            annotation_font_color="orange",
            fillcolor="yellow",
            line_color="white",
            opacity=0.25,
            line_width=2,
            line_dash="solid",
        )

        fig.update_traces( marker_color='#2E8B57')
        fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide', xaxis_title="Date",
        yaxis_title="Liquidity (USD)") 
        osmo_col3.plotly_chart(fig, use_container_width=True) 


        atom_col4.markdown("""---""")
        atom_col4.write("Regen - Atom pool daily liquidity")
        atom_col4.markdown("""---""")
        atom_col4.text("")


        fig = go.Figure()

        fig.add_trace(
            go.Scatter(x=regen_atom_liq_df['time'], y=regen_atom_liq_df['value'], name="yaxis data", fill='tozeroy') 
        ) #, text='Daily Volume - Pool Regen-Atom')
        fig.add_vrect(
            x0="2022-09-26",
            x1="2022-09-29",
            annotation_text="Cosmoverse",
            annotation_position="inside top left",
            annotation_textangle=90,
            annotation_font_size=16,
            annotation_font_color="gray",
            fillcolor="Green",
            opacity=0.3,
            line_width=0,
            line_dash="dash",
        )
        fig.add_vrect(
            x0="2022-09-27",
            x1="2022-09-28",
            annotation_text="Regen cosmoverse talk",
            annotation_position="inside top right",
            annotation_textangle=90,
            annotation_font_size=16,
            annotation_font_color="orange",
            fillcolor="yellow",
            line_color="white",
            opacity=0.25,
            line_width=2,
            line_dash="solid",
        )
        fig.update_traces( marker_color='#2E8B57')
        fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide', xaxis_title="Date",
        yaxis_title="Liquidity (USD)") 
        atom_col4.plotly_chart(fig, use_container_width=True) 



        st.markdown("---")



        st.error("Number of users and unique users on the following tab...")

    with tab3:

        st.subheader("Number of users and unique new users")
        st.markdown("---")
        st.write("After analyzing price and volume metrics, we'll now look at daily number of users and unique users, both on Osmosis and Regen pools. In this section, when we talk about users I'll be refering to trading pool activity (i.e. swaps), not adding or removing liquidity.")

        st.write("On Osmosis in general, there was an increase during the days of the Cosmoverse in *new* users swapping, almost a 200 daily new users increase from the day before the Cosmoverse.")


        query = create_query(SQL_QUERY_10)
        token = query.get('token')
        data_user_osmo = get_query_results(token) 
        df_user_osmo = pd.DataFrame(data_user_osmo['results'], columns = ['DAILY', 'UNIQUE_NEW_USERS','CUMULATIVE_NEW_USERS_DAILY']) 
        df_user_osmo = df_user_osmo.sort_values(by="DAILY")  
        df_user_osmo = df_user_osmo[df_user_osmo['DAILY'] >= '2022-09-01']

        fig = make_subplots(specs=[[{"secondary_y": True}]])

        fig.add_trace(
            go.Scatter(x=df_user_osmo['DAILY'], y=df_user_osmo['CUMULATIVE_NEW_USERS_DAILY'], name="Cumulative new users"),
            secondary_y=True,
        )

        fig.add_trace(
            go.Bar(x=df_user_osmo['DAILY'], y=df_user_osmo['UNIQUE_NEW_USERS'], name="Daily new users"),
            secondary_y=False,
        )
        fig.add_vrect(
            x0="2022-09-26",
            x1="2022-09-29",
            annotation_text="Cosmoverse",
            annotation_position="inside top left",
            annotation_textangle=90,
            annotation_font_size=16,
            annotation_font_color="gray",
            fillcolor="Green",
            opacity=0.3,
            line_width=0,
            line_dash="dash",
        )

        # Add figure title
        fig.update_layout(
            title_text="Daily and cumulative new users swapping on Osmosis"
        )

        # Set x-axis title
        fig.update_traces( marker_color='#7B68EE')
        fig.update_xaxes(title_text="Date")

        # Set y-axes titles
        fig.update_yaxes(title_text="Number of users", secondary_y=False)
        fig.update_yaxes(title_text="Number of users", secondary_y=True)


        st.plotly_chart(fig, use_container_width=True) 

        ####################################################################################################################

        st.write("This effect also translates to the Regen pools. Specifically, for the Regen - Osmo pools there were around 10 unique new users the day before the event, and 19 daily new users towards the end of the event. On the Regen - Atom pool, there was an increase from 6-9 daily new users to 13 daily new users. ")


        osmo_col_first, atom_col_first = st.columns(2)
        osmo_col_first.markdown("""---""")
        osmo_col_first.write("Regen - Osmo pool user growth")
        osmo_col_first.markdown("""---""")
        osmo_col_first.text("")

        query = create_query(SQL_QUERY_8)
        token = query.get('token')
        data_user_pool42 = get_query_results(token) 
        df_user_pool42 = pd.DataFrame(data_user_pool42['results'], columns = ['DAILY', 'UNIQUE_NEW_USERS','CUMULATIVE_NEW_USERS_DAILY']) 
        df_user_pool42 = df_user_pool42.sort_values(by="DAILY")
        df_user_pool42 = df_user_pool42[df_user_pool42['DAILY'] >= '2022-09-01']  

        fig = make_subplots(specs=[[{"secondary_y": True}]])

        fig.add_trace(
            go.Scatter(x=df_user_pool42['DAILY'], y=df_user_pool42['CUMULATIVE_NEW_USERS_DAILY'], name="Cumulative new users"),
            secondary_y=True,
        )

        fig.add_trace(
            go.Bar(x=df_user_pool42['DAILY'], y=df_user_pool42['UNIQUE_NEW_USERS'], name="Daily new users"),
            secondary_y=False,
        )
        fig.add_vrect(
            x0="2022-09-26",
            x1="2022-09-29",
            annotation_text="Cosmoverse",
            annotation_position="inside top left",
            annotation_textangle=90,
            annotation_font_size=16,
            annotation_font_color="gray",
            fillcolor="Green",
            opacity=0.3,
            line_width=0,
            line_dash="dash",
        )
        fig.add_vrect(
            x0="2022-09-27",
            x1="2022-09-28",
            annotation_text="Regen cosmoverse talk",
            annotation_position="inside top right",
            annotation_textangle=90,
            annotation_font_size=16,
            annotation_font_color="orange",
            fillcolor="yellow",
            line_color="white",
            opacity=0.25,
            line_width=2,
            line_dash="solid",
        )
        # Add figure title
        fig.update_traces( marker_color='#2E8B57')
        fig.update_layout(
            title_text="Regen - Osmo pool daily new users and cumulative"
        )

        # Set x-axis title
        fig.update_xaxes(title_text="Date")

        # Set y-axes titles
        fig.update_yaxes(title_text="Number of users", secondary_y=False)
        fig.update_yaxes(title_text="Number of users", secondary_y=True)


        osmo_col_first.plotly_chart(fig, use_container_width=True) 

        atom_col_first.markdown("""---""")
        atom_col_first.write("Regen - Osmo pool user growth")
        atom_col_first.markdown("""---""")
        atom_col_first.text("")

        query = create_query(SQL_QUERY_9)
        token = query.get('token')
        data_user_pool22 = get_query_results(token) 
        df_user_pool22 = pd.DataFrame(data_user_pool22['results'], columns = ['DAILY', 'UNIQUE_NEW_USERS','CUMULATIVE_NEW_USERS_DAILY']) 
        df_user_pool22 = df_user_pool22.sort_values(by="DAILY")
        df_user_pool22 = df_user_pool22[df_user_pool22['DAILY'] >= '2022-09-01']  

        fig = make_subplots(specs=[[{"secondary_y": True}]])

        fig.add_trace(
            go.Scatter(x=df_user_pool22['DAILY'], y=df_user_pool22['CUMULATIVE_NEW_USERS_DAILY'], name="Cumulative new users"),
            secondary_y=True,
        )

        fig.add_trace(
            go.Bar(x=df_user_pool22['DAILY'], y=df_user_pool22['UNIQUE_NEW_USERS'], name="Daily new users"),
            secondary_y=False,
        )
        fig.add_vrect(
            x0="2022-09-26",
            x1="2022-09-29",
            annotation_text="Cosmoverse",
            annotation_position="inside top left",
            annotation_textangle=90,
            annotation_font_size=16,
            annotation_font_color="gray",
            fillcolor="Green",
            opacity=0.3,
            line_width=0,
            line_dash="dash",
        )
        fig.add_vrect(
            x0="2022-09-27",
            x1="2022-09-28",
            annotation_text="Regen cosmoverse talk",
            annotation_position="inside top right",
            annotation_textangle=90,
            annotation_font_size=16,
            annotation_font_color="orange",
            fillcolor="yellow",
            line_color="white",
            opacity=0.25,
            line_width=2,
            line_dash="solid",
        )
        # Add figure title
        fig.update_traces( marker_color='#2E8B57')
        fig.update_layout(
            title_text="Regen - Osmo pool daily new users and cumulative"
        )

        # Set x-axis title
        fig.update_xaxes(title_text="Date")

        # Set y-axes titles
        fig.update_yaxes(title_text="Number of users", secondary_y=False)
        fig.update_yaxes(title_text="Number of users", secondary_y=True)


        atom_col_first.plotly_chart(fig, use_container_width=True) 


        st.markdown("---")
        st.subheader("Number of swaps and traders")
        st.markdown("---")
        st.write("Interestingly, if we look at the number of traders (not new traders), this increase is not reflected here, but it stays around the same values as the days before the event, and the same happens for the number of swaps (transactions). ")

        osmo_col5, atom_col6 = st.columns(2)

        osmo_col5.markdown("""---""")
        osmo_col5.write("Regen - Osmo pool daily number of traders")
        osmo_col5.markdown("""---""")
        osmo_col5.text("")


        fig = px.bar(df1, y='NUM_TRADERS', x='DATE')#, text='Daily Volume - Pool Regen-Atom')
        fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
        fig.add_vrect(
            x0="2022-09-26",
            x1="2022-09-29",
            annotation_text="Cosmoverse",
            annotation_position="inside top left",
            annotation_textangle=90,
            annotation_font_size=16,
            annotation_font_color="gray",
            fillcolor="Green",
            opacity=0.3,
            line_width=0,
            line_dash="dash",
        )
        fig.add_vrect(
            x0="2022-09-27",
            x1="2022-09-28",
            annotation_text="Regen cosmoverse talk",
            annotation_position="inside top right",
            annotation_textangle=90,
            annotation_font_size=16,
            annotation_font_color="orange",
            fillcolor="yellow",
            line_color="white",
            opacity=0.25,
            line_width=2,
            line_dash="solid",
        )
        fig.update_traces( marker_color='#2E8B57')
        fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide') 
        osmo_col5.plotly_chart(fig, use_container_width=True) 
        osmo_col5.markdown("""---""")
        osmo_col5.text("Regen - Osmo pool daily number of SWAPs")
        osmo_col5.markdown("""---""")
        osmo_col5.text("")


        fig = px.bar(df1, y='NUM_TRANSACTIONS', x='DATE')#, text='Daily Volume - Pool Regen-Atom')
        fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
        fig.add_vrect(
            x0="2022-09-26",
            x1="2022-09-29",
            annotation_text="Cosmoverse",
            annotation_position="inside top left",
            annotation_textangle=90,
            annotation_font_size=16,
            annotation_font_color="gray",
            fillcolor="Green",
            opacity=0.3,
            line_width=0,
            line_dash="dash",
        )
        fig.add_vrect(
            x0="2022-09-27",
            x1="2022-09-28",
            annotation_text="Regen cosmoverse talk",
            annotation_position="inside top right",
            annotation_textangle=90,
            annotation_font_size=16,
            annotation_font_color="orange",
            fillcolor="yellow",
            line_color="white",
            opacity=0.25,
            line_width=2,
            line_dash="solid",
        )
        fig.update_traces( marker_color='#2E8B57')
        fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide') 
        osmo_col5.plotly_chart(fig, use_container_width=True) 


        atom_col6.markdown("""---""")
        atom_col6.write("Regen - Atom pool daily number of traders")
        atom_col6.markdown("""---""")
        atom_col6.text("")

        fig = px.bar(df2, y='NUM_TRADERS', x='DATE')#, text='Daily Volume - Pool Regen-Atom')
        fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
        fig.add_vrect(
            x0="2022-09-26",
            x1="2022-09-29",
            annotation_text="Cosmoverse",
            annotation_position="inside top left",
            annotation_textangle=90,
            annotation_font_size=16,
            annotation_font_color="gray",
            fillcolor="Green",
            opacity=0.3,
            line_width=0,
            line_dash="dash",
        )
        fig.add_vrect(
            x0="2022-09-27",
            x1="2022-09-28",
            annotation_text="Regen cosmoverse talk",
            annotation_position="inside top right",
            annotation_textangle=90,
            annotation_font_size=16,
            annotation_font_color="orange",
            fillcolor="yellow",
            line_color="white",
            opacity=0.25,
            line_width=2,
            line_dash="solid",
        )
        fig.update_traces( marker_color='#2E8B57')
        fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide') 
        atom_col6.plotly_chart(fig, use_container_width=True) 
        atom_col6.markdown("""---""")
        atom_col6.text("Regen - Atom pool daily number of SWAPs")
        atom_col6.markdown("""---""")
        atom_col6.text("")


        fig = px.bar(df2, y='NUM_TRANSACTIONS', x='DATE')#, text='Daily Volume - Pool Regen-Atom')
        fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
        fig.add_vrect(
            x0="2022-09-26",
            x1="2022-09-29",
            annotation_text="Cosmoverse",
            annotation_position="inside top left",
            annotation_textangle=90,
            annotation_font_size=16,
            annotation_font_color="gray",
            fillcolor="Green",
            opacity=0.3,
            line_width=0,
            line_dash="dash",
        )
        fig.add_vrect(
            x0="2022-09-27",
            x1="2022-09-28",
            annotation_text="Regen cosmoverse talk",
            annotation_position="inside top right",
            annotation_textangle=90,
            annotation_font_size=16,
            annotation_font_color="orange",
            fillcolor="yellow",
            line_color="white",
            opacity=0.25,
            line_width=2,
            line_dash="solid",
        )
        fig.update_traces( marker_color='#2E8B57')
        fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide') 
        atom_col6.plotly_chart(fig, use_container_width=True) 

        st.write("But on the previous section, we did see an increase in the Regen - Osmo pool, from 5000 USD the days before the cosmoverse event, to 27000 USD post Cosmoverse. And since this increase is not related to the number of users overall, it seems logical to believe it was either due to new users swapping larger amounts, or a 'whale' (in Regen pool terms) which moved more liquidity during those days.")


        query = create_query(SQL_QUERY_14)
        token = query.get('token')
        data_top10_regen = get_query_results(token) 
        df_top10_regen = pd.DataFrame(data_top10_regen['results'], columns = ['TX_ID', 'TRADER', 'FROM_CURRENCY', 'FROM_AMOUNT', 'TO_CURRENCY', 'TO_AMOUNT']) 
        st.table(df_top10_regen)

        query = create_query(SQL_QUERY_15)
        token = query.get('token')
        data_top10_regen_date = get_query_results(token) 
        df_top10_regen_date = pd.DataFrame(data_top10_regen_date['results'], columns = ['TRADER', 'FIRST_DATE']) 
        st.table(df_top10_regen_date)

        st.info(
            "Let's check common traders"
        )

        st.write("The following chart shows the number of daily traders for the Regen - Osmo pool and the shared traders with the Regen - Atom pools for the same day. Interestingly, there are some days where the number of shared traders is around 40%.")




        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df3['DATE'],
            y=df3['NUM_TRADERS'],
            name='Number of traders',
            marker_color='indianred'
        ))
        fig.add_trace(go.Bar(
            x=df3['DATE'],
            y=df3['COMMON_TRADERS'],
            name='Number of common traders - Osmo/Regen and Atom/Regen pools',
            marker_color='lightsalmon'
        ))
        fig.add_vrect(
            x0="2022-09-26",
            x1="2022-09-29",
            annotation_text="Cosmoverse",
            annotation_position="inside top left",
            annotation_textangle=90,
            annotation_font_size=16,
            annotation_font_color="gray",
            fillcolor="Green",
            opacity=0.3,
            line_width=0,
            line_dash="dash",
        )
        fig.add_vrect(
            x0="2022-09-27",
            x1="2022-09-28",
            annotation_text="Regen cosmoverse talk",
            annotation_position="inside top right",
            annotation_textangle=90,
            annotation_font_size=16,
            annotation_font_color="orange",
            fillcolor="yellow",
            line_color="white",
            opacity=0.25,
            line_width=2,
            line_dash="solid",
        ) 
        # Here we modify the tickangle of the xaxis, resulting in rotated labels.
        fig.update_layout(barmode='group', xaxis_tickangle=-45) 
        st.plotly_chart(fig, use_container_width=True)



        query = create_query(SQL_QUERY_16)
        token = query.get('token')
        data_unique_regen_date = get_query_results(token) 
        df_unique_regen_date = pd.DataFrame(data_unique_regen_date['results'], columns = ['UNIQUE_REGEN_TRADERS']) 
        st.metric(label="Unique users in Regen pools since start of September", value =df_unique_regen_date['UNIQUE_REGEN_TRADERS'].sum() )
        st.markdown("---")
        st.error("Cohort analysis on the following tab...")
    with tab4:

        st.subheader("Cohort analysis")
        st.markdown("---")

        st.info("A very useful way to calculate user retention is cohort analysis. Cohort analysis is a study that concentrates on the activities of a specific cohort type. A cohort analysis table is used to visually display cohort data in order to help analysts compare different groups of users at the same stage in their lifecycle, and to see the long-term relationship between the characteristics of a given user group.")

        st.write("Considering only the swaps table, I've taken a look at how many users do at least one transaction at throughout 2022, and then see if how many of those users keep doing at least one transaction throughout the year.")

        st.write("Let’s look at an example. If we take a look at the cohort table for 2022, we have a row for each month, and a column where the underscore represents the number of months afterwards. For instance, for January, cohort_index_1 = 31 means that 31% of users active throughout January ‘22 were still active after 1 month. For the same month, cohort index 2 = 27% means that 27% of users active during January were also active after two months, and so on.")

        st.write("Therefore, if we compare the cohort index for both Regen-Osmo and Regen-Atom pool, it seems like overall the first one has a higher retention rate than the latter.")

        query = create_query(SQL_QUERY_7)
        token = query.get('token')
        data7 = get_query_results(token)
        # Common traders - Traders that trade both on Osmo-Regen and Atom-Regen
        df7 = pd.DataFrame(data7['results'], columns = ['MONTH', 'COHORT_INDEX_1', 'COHORT_INDEX_2', 'COHORT_INDEX_3', 'COHORT_INDEX_4', 'COHORT_INDEX_5', 'COHORT_INDEX_6', 'COHORT_INDEX_7', 'COHORT_INDEX_8']) 

        cols_df_7 = df7.columns.tolist()
        cols_df_7.remove('MONTH')
        fig = go.Figure(data=go.Heatmap(
                       z=df7.iloc[:, 1:9],
                       x=cols_df_7,
                       y=df7['MONTH'],
                       hoverongaps = True, 

                       colorscale='Viridis'))
        fig.update_xaxes(side="top")
        fig.update_layout(
        title='Regen - Osmo cohort analysis' )
        st.plotly_chart(fig, use_container_width=True) 



        query = create_query(SQL_QUERY_6)
        token = query.get('token')
        data6 = get_query_results(token)
        # Common traders - Traders that trade both on Osmo-Regen and Atom-Regen
        df6 = pd.DataFrame(data6['results'], columns = ['MONTH', 'COHORT_INDEX_1', 'COHORT_INDEX_2', 'COHORT_INDEX_3', 'COHORT_INDEX_4', 'COHORT_INDEX_5', 'COHORT_INDEX_6', 'COHORT_INDEX_7', 'COHORT_INDEX_8']) 

        cols_df_6 = df6.columns.tolist()
        cols_df_6.remove('MONTH')
        fig = go.Figure(data=go.Heatmap(
                       z=df6.iloc[:, 1:9],
                       x=cols_df_6,
                       y=df6['MONTH'],
                       hoverongaps = True, 

                       colorscale='Viridis'))
        fig.update_xaxes(side="top")
        fig.update_layout(
        title='Regen - Atom cohort analysis' )
        st.plotly_chart(fig, use_container_width=True) 




        st.markdown("---")
        st.error("Mesh security on the following tab...")

    with tab5:
        st.subheader("Mesh security introduction")
        st.markdown("---")
        st.write("All throughout the Cosmoverse conference the term **Mesh security** was all around, coined by Sunny from Osmosis. One of the main comparisons to real world examples of mesh security was NATO. It consists of a network of sovereign states, each of them having their own governance system, but providing security to each other.")
        st.markdown("* Through Interchain security (another fuzz word through the Cosmoverse), a chain has its own validator set with full sovereignty, and security is amplified by Atom stakers, but this is a hub-centric model. That's where mesh security comes into play.")
        st.markdown("* Through mesh security, Osmosis will be a consumer chain and gain security from Atom, but it will also lend security to the Hub. But it doesn't end there! It can follow this model through all different chains, and they can both add security to each other.")
        st.write("This works by leveraging the overlap of validators in Cosmos. Imagine 75% of OSMO validators are running JUNO validators, and 72% of JUNO validators are running OSMO validators. This is defined as soft security, and a same validator in both chains could submit transactions with correlated identities. If said validator tries to misbehave, they would get slashed on both chains. But on the other hand, it could boost staking rewards!")
        st.write("An obvious concern at first sight would be centralization, since if a validator has boosted rewards due to its presence in multiple chains, it holds an advantage respect to smaller validators. However, it can be solved through capping voting power. This would prevent an overtaking of the chain by larger validators.")
        st.write("It will be interesting to see how ecosystems with economic interdependencies will relate and boost each other through mesh security incentives.")

        st.markdown("---")
        st.subheader("Regen and Osmosis common validators")
        st.markdown("---")

        st.write("There are two ways to explore it: common validators and common validators voting power. Both of them are explored below. The first chart shows both common validators and their voting power on each individual chain. Conclusions are shown at the end.")

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=Inner_join['LABEL'],
            y=Inner_join['PERCENTAGE_VOTING_OSMOSIS'],
            name='Shared validators - Voting power in Osmosis',
            marker_color='BlueViolet'
        ))
        fig.add_trace(go.Bar(
            x=Inner_join['LABEL'],
            y=Inner_join['VALIDATOR_VOTING_PERCENTAGE_REGEN'],
            name='Shared validators - Voting power in Regen Network',
            marker_color='ForestGreen'
        ))

        # Here we modify the tickangle of the xaxis, resulting in rotated labels.
        fig.update_layout(barmode='group', xaxis_tickangle=-45, height = 1000) 
        st.plotly_chart(fig, use_container_width=True) 


        regen_osmo, osmo_regen = st.columns(2)


        regen_0_data = {'Shared_not_shared': 'Shared', 'Amount': Inner_join['LABEL'].nunique()}
        regen_1_data = {'Shared_not_shared': 'Not shared', 'Amount': val_reg_total['LABEL'].nunique()- Inner_join['LABEL'].nunique()}
        regen_2_data = {'Shared_not_shared': 'Shared', 'Amount': Inner_join['VALIDATOR_VOTING_PERCENTAGE_REGEN'].sum()}
        regen_3_data = {'Shared_not_shared': 'Not shared', 'Amount': 100-Inner_join['VALIDATOR_VOTING_PERCENTAGE_REGEN'].sum()}
        regen_validators_data =  pd.concat([pd.DataFrame(regen_0_data,  index = [0]), pd.DataFrame(regen_1_data,  index = [0])])
        regen_validators_data_voting =  pd.concat([pd.DataFrame(regen_2_data,  index = [0]), pd.DataFrame(regen_3_data,  index = [0])])

        fig = px.pie(regen_validators_data, values='Amount', names='Shared_not_shared', 
                     color_discrete_map={'Shared':'lightcyan',
                                     'Not shared':'royalblue'},
                     title='Regen network - Shared and non-shared validators with Osmosis')
        regen_osmo.plotly_chart(fig, use_container_width=True) 

        fig = px.pie(regen_validators_data_voting, values='Amount', names='Shared_not_shared',
                     color_discrete_map={'Shared':'lightcyan',
                                     'Not shared':'royalblue'},
                     title='Regen network - Voting power of shared and non-shared validators with Osmosis')
        regen_osmo.plotly_chart(fig, use_container_width=True) 

        osmo_0_data = {'Shared_not_shared': 'Shared', 'Amount': Inner_join['LABEL'].nunique()}
        osmo_1_data = {'Shared_not_shared': 'Not shared', 'Amount': 150- Inner_join['LABEL'].nunique()}
        osmo_2_data = {'Shared_not_shared': 'Shared', 'Amount': Inner_join['PERCENTAGE_VOTING_OSMOSIS'].sum()}
        osmo_3_data = {'Shared_not_shared': 'Not shared', 'Amount': 100-Inner_join['PERCENTAGE_VOTING_OSMOSIS'].sum()}

        osmo_validators_data =  pd.concat([pd.DataFrame(osmo_0_data,  index = [0]), pd.DataFrame(osmo_1_data,  index = [0])])
        osmo_validators_data_voting =  pd.concat([pd.DataFrame(osmo_2_data,  index = [0]), pd.DataFrame(osmo_3_data,  index = [0])])

        fig = px.pie(osmo_validators_data, values='Amount', names='Shared_not_shared',
                     color_discrete_map={'Shared':'lightcyan',
                                     'Not shared':'royalblue'},
                     title='Osmosis - Shared and non-shared validators with Regen network')
        osmo_regen.plotly_chart(fig, use_container_width=True) 

        fig = px.pie(osmo_validators_data_voting, values='Amount', names='Shared_not_shared',
                     color_discrete_map={'Shared':'lightcyan',
                                     'Not shared':'royalblue'},
                     title='Osmosis - Voting power of shared and non-shared validators with Regen network')
        osmo_regen.plotly_chart(fig, use_container_width=True)

        st.info("We've seen that 41% of Regen validators are shared with Osmosis validators, representing 44% of all voting power on Regen validators. On the other side, 20% of Osmosis validators are shared with Regen (since there are 75 active validators on Regen and 150 on Osmosis), but they represent 33% of all voting power on Osmosis.")
        st.markdown("---") 

    with tab6:
        st.subheader(
            "Description and metodology"
        ) 

        st.markdown("---")


        st.write("Thanks everyone for going through this dashboard! :) Feel free to contact me if there are any ideas you'd like to explore or if I'm missing something.")
        st.write("In order to explore this data, I've used:")

        st.markdown("* Flipside Crypto Data for querying swaps, liquidity, user behavior and Osmosis validators.")
        st.markdown("* Imperator Osmosis API for pool information.")
        st.markdown("* Mainnet regent network swagger API for Regen validator information.")

        st.write("Regarding the introduction, for reference I've used:")

        st.markdown("* @Flowslikeosmo mesh security information.")
        st.markdown("* Frens validator video on Regen network.")
        st.markdown("* Regen network website.")
        st.markdown("* Gregory Landua talk on Cosmoverse.")

        st.markdown("---")

except: 
   st_autorefresh(interval=10)
