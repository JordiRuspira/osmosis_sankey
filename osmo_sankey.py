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
import streamlit_autorefresh
#from streamlit_autorefresh import st_autorefresh

try:
	st.set_page_config(
		page_title="Osmosis Validators - Sankey chart",
		page_icon=":atom_symbol:",
		layout="wide",
		menu_items=dict(About="It's a work of Jordi"),
	)


	st.title(":atom_symbol: OSMO Sankey :atom_symbol:")


	st.success("This app only contains a chart! Please select a validator ")
	st.text("")
	st.subheader('Streamlit App by [Jordi R.](https://twitter.com/RuspiTorpi/). Powered by Flipsidecrypto')
	st.text("")
	st.markdown('Hi there. This streamlit app displays a Sankey chart showing all-time redelegations from a selected validator to the rest of validators. Future versions of this app may include time filters.' )   


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



	  
	SQL_QUERY = """   select distinct address, label, RANK() OVER (ORDER BY address DESC) AS RANK from osmosis.core.dim_labels
	where address in (select distinct validator_address from osmosis.core.fact_staking  ) 
	and address <> 'osmovaloper12l0vwef7w0xmkgktyqdzgd05jyq0lcuuqy2m8v'
	order by rank

	"""  

	SQL_QUERY_2 = """  with table_0 as ( select distinct address, label, RANK() OVER (ORDER BY address DESC) AS RANK from osmosis.core.dim_labels
	where address in (select distinct validator_address from osmosis.core.fact_staking ) 
	and address <> 'osmovaloper12l0vwef7w0xmkgktyqdzgd05jyq0lcuuqy2m8v')

	select b.label as from_validator, c.label as to_validator, d.RANK as from_validator_rank, e.rank as to_validator_rank, sum(amount/pow(10,decimal)) as amount_redelegated from osmosis.core.fact_staking a 
	left join  osmosis.core.dim_labels b 
	on a.redelegate_source_validator_address = b.address
	left join  osmosis.core.dim_labels c 
	on a.validator_address = c.address
	left join  table_0 d 
	on a.redelegate_source_validator_address = d.address
	left join  table_0 e 
	on a.validator_address = e.address
	where action = 'redelegate'
	and d.rank is not null
	group by from_validator, to_validator, from_validator_rank, to_validator_rank
	order by d.rank
	  

	"""  
	 

	TTL_MINUTES = 15
	# return up to 100,000 results per GET request on the query id
	PAGE_SIZE = 100000
	# return results of page 1
	PAGE_NUMBER = 1

	def create_query():
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
	 
	def create_query_2():
		r = requests.post(
			'https://node-api.flipsidecrypto.com/queries', 
			data=json.dumps({
				"sql": SQL_QUERY_2,
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



	def get_query_results_2(token):
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
			return get_query_results_2(token)

		return data


	query_2 = create_query_2()
	token_2 = query_2.get('token')
	data2 = get_query_results_2(token_2) 
	df2 = pd.DataFrame(data2['results'], columns = ['FROM_VALIDATOR', 'TO_VALIDATOR','FROM_VALIDATOR_RANK','TO_VALIDATOR_RANK','AMOUNT_REDELEGATED'])


	  



	query = create_query()
	token = query.get('token')
	data1 = get_query_results(token)
	df1 = pd.DataFrame(data1['results'], columns = ['ADDRESS', 'LABEL','RANK']) 

	randcolor = []
	for i in range(1,len(df1['LABEL']) + 1):
	 
		randcolor.append("#{:06x}".format(random.randint(0, 0xFFFFFF))) 
		
	df1['COLOR'] = randcolor


	keys_list =  df1['RANK']
	values_list = df1['LABEL']
	zip_iterator = zip(keys_list, values_list) 
	a_dictionary = dict(zip_iterator)



	df3 = pd.DataFrame(a_dictionary.items(), columns = ['RANK','LABEL'], index = keys_list)
	df3.index = df3.index
	df3 = df3.sort_index()






	with st.container():

		
		validator_choice = st.selectbox("Choose a validator", options = df2['FROM_VALIDATOR'].unique() )

		
		df_filtered = df2[df2['FROM_VALIDATOR'] == validator_choice]
		df_filtered['Link color'] = 'rgba(127, 194, 65, 0.2)'
		df_filtered['FROM_VALIDATOR_RANK'] = df_filtered['FROM_VALIDATOR_RANK']-1
		df_filtered['TO_VALIDATOR_RANK'] = df_filtered['TO_VALIDATOR_RANK'] - 1

		link = dict(source = df_filtered['FROM_VALIDATOR_RANK'].values , target = df_filtered['TO_VALIDATOR_RANK'].values, value = df_filtered['AMOUNT_REDELEGATED'], color = df1['COLOR'])
		node = dict(label = df3['LABEL'].values, pad = 35, thickness = 10)

	 
		
		 
		data = go.Sankey(link = link, node = node)
		fig = go.Figure(data)
		fig.update_layout(
			hovermode = 'x', 
			font = dict(size = 20, color = 'white'), 
			paper_bgcolor= 'rgba(0,0,0,0)',
			width=1000, height=1300
		) 
		
		st.plotly_chart(fig, use_container_width=True) 

except: 
   st_autorefresh(interval=10, key="dataframerefresh")
