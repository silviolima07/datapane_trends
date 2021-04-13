# -*- coding: utf-8 -*-

import altair as alt
import pandas as pd
import datapane as dp
from datetime import date
from folium import plugins
import folium
import plotly.express as px
import sys

from pytrends.request import TrendReq

import plotly.io as pio
pio.templates.default = "plotly_dark"

datapane_token = sys.argv[1]

dp.login(token= datapane_token)

##########################

# execute the TrendReq method by passing the host language (hl) and timezone (tz) parameters
pytrends = TrendReq(hl='en-US', tz=360)

kw_list = ["covid", "lockdown", "jair bolsonaro"]

pytrends.build_payload(kw_list, timeframe='2020-01-04 2021-01-08', geo='BR')

# store interest over time information in df
df = pytrends.interest_over_time()

df_region = pytrends.interest_by_region(resolution='REGION', inc_low_vol=True, inc_geo_code=False)

# display the top 20 rows in dataframe
print(df.head(20))

# display the top 20 rows in dataframe
print(df_region.head(20))

fig1 = px.line(df,df.index, 'jair bolsonaro', title='Jair Bolsonaro x Date', labels= {'x': 'Date'})

#fig1_region = px.histogram(df_region,df.index, 'jair bolsonaro', title='Jair Bolsonaro x Date', labels= {'x': 'Date'})


##########################

fig1_region = px.histogram(df_region, x= 'jair bolsonaro', hover_name = df_region.index, color=df_region.index)

fig1_region.show()

##########################

#fig2 = px.histogram(df_vagas, x="nivel", color="nivel", hover_name ='nivel', facet_col= 'vaga')

##########################

#fig3 = px.histogram(df_vagas, x="vaga", color="vaga", hover_name ='vaga')

##########################

# Mapa do Brasil

#coordenadas=[]
#for lat,lng in zip(df_vagas.latitude,df_vagas.longitude):
#  coordenadas.append([lat,lng])

#mapa = folium.Map(location=[-15.788497,-47.879873],zoom_start=4,tiles='Stamen Toner')

#mapa.add_child(plugins.HeatMap(coordenadas))

####
#title_html = '''
#             <h3 align="center" style="font-size:20px"><b>Heatmap de vagas pelo Brasil</br></br></b></h3>
#             '''
#mapa.get_root().html.add_child(folium.Element(title_html))

#######################

# Create report

r = dp.Report(
    dp.Page(
       label='Dashes',
       blocks=[
               "#### Bolsonaro x Date", 
               dp.Plot(fig1),
               "#### Bolsonaro x Região", 
               dp.Plot(fig1_region)
               ]
     ),
    dp.Page(
       label='Interesse Ao longo do Tempo',
       blocks=["#### Bolsonaro",
       dp.DataTable(df, label="Bolsonaro")]
     ),
    dp.Page(
       label='Interesse Por Regiao',
       blocks=["#### Região", 
       dp.DataTable(df_region, label= "Região")]
     )
    )
r
# Publish
r.publish(name=f'Google Trends', open = False, description='Analisando termos no google trends')

     
