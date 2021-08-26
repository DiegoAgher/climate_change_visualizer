import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px

from datetime import datetime

from pandas.core.window.rolling import _Rolling_and_Expanding

def weighted_average(x):
    d = []
    d.append(x['mult'].sum()/x['importance'].sum())
    return pd.Series(d, index=['wavg'])

_Rolling_and_Expanding.weighted_average = weighted_average

# Load world data
world_data = pd.read_csv('data/GlobalLandTemperaturesByCountry.csv')
world_data = world_data.dropna()
world_data['dt'] = pd.to_datetime(world_data['dt'])
world_data = world_data.sort_values(by=['dt'])
world_data['importance'] = 1 / world_data['AverageTemperatureUncertainty']
world_data['mult'] = world_data['importance'] * world_data['AverageTemperature']

st.title('Play around to visualize temperatures over time')

unique_countries = world_data['Country'].unique()
country_filter = st.selectbox(
             'Select one country',
                 unique_countries)

'You selected:', country_filter

rolling_steps = st.slider('How many days for rolling mean?', 3, 365, 10)
start_time = st.text_input("Choose a starting date", '1800-01-01')
st.write("Start time:", start_time)

# Get everything ready for the first graph
filtered_data = world_data[world_data['Country']==country_filter]
filtered_data = filtered_data[filtered_data['dt']>= start_time]
filtered_data['importance'] = 1 / filtered_data['AverageTemperatureUncertainty']
filtered_data['mult'] = filtered_data['importance'] * filtered_data['AverageTemperature']

mean_temps = filtered_data.rolling(rolling_steps).weighted_average()['wavg'].dropna()
dates = filtered_data['dt'].shift(rolling_steps-1).dropna()

mean_temps = pd.concat([mean_temps, dates], 1)
mean_temps = mean_temps.reset_index(drop=True)
mean_temps = mean_temps.reset_index(drop=False)
mean_temps.rename(columns={0:'(weighted)Avg Temperature',
                           'dt': 'time'}, inplace=True)


#'temps', mean_temps
fig = px.scatter(mean_temps, x='time', y='(weighted)Avg Temperature', 
                 trendline='ols', trendline_color_override='#A52A2A')

# Get trendline to be thicker
tr_line=[]
for  k, trace  in enumerate(fig.data):
    if trace.mode is not None and trace.mode == 'lines':
        tr_line.append(k)
for id in tr_line:
    fig.data[id].update(line_width=4)


# First graph
'Moving (weighted) averages'
st.plotly_chart(fig, use_container_width=True)



# Get everything ready for second graph
second_filter = st.selectbox('Country', unique_countries)
start_time2 = st.text_input("Choose a second starting date", '1800-01-01')
st.write("Start time:", start_time2)

country_data = world_data[world_data['Country']==second_filter]
country_data = country_data[country_data['dt']>=start_time2]

time_frame = st.text_input("month, year?", 'month')
freq = "M" if time_frame == 'month' else "Y"
country_data = country_data.set_index('dt')
grouped = country_data.groupby(pd.Grouper(freq=freq))
res = grouped.apply(weighted_average)
res.rename(columns={'wavg':'(weighted)Avg Temperature'},
                    inplace=True)

fig = px.scatter(res, y='(weighted)Avg Temperature',
                 trendline='ols', trendline_color_override='#A52A2A')

tr_line=[]
for  k, trace  in enumerate(fig.data):
    if trace.mode is not None and trace.mode == 'lines':
        tr_line.append(k)

for id in tr_line:
    fig.data[id].update(line_width=4)

# Second graph
st.write('Averages per {}'.format(time_frame))
st.plotly_chart(fig, use_container_width=True)
