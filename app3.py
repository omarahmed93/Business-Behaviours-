import streamlit as st
import pandas as pd
import plotly.express as px

df=px.data.tips()
# select time
time=st.sidebar.radio('select time',options=df['time'].unique())
sex=st.sidebar.selectbox('select gender',options=df['sex'].unique())
# filter
df_filter=df[(df['time']==time) & (df['sex']==sex)]
# chose chart
fig=px.histogram(data_frame=df_filter,x='total_bill')
st.plotly_chart(fig)
