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

###########################

# execute the TrendReq method by passing the host language (hl) and timezone (tz) parameters
pytrends = TrendReq(hl='pt-BR', tz=360)

kw_list = ["covid", "lockdown", "jair bolsonaro"]

pytrends.build_payload(kw_list, timeframe='today 5-y', geo='BR')

# store interest over time information in df
df = pytrends.interest_over_time()

# Filter last 3 years

df['year'] = df.index
df['year2'] = df.year.dt.year
df = df.loc[df.year2 > 2017]

df_region = pytrends.interest_by_region(resolution='REGION', inc_low_vol=True, inc_geo_code=False)

df_region['estado'] = df_region.index

df_coor = pd.read_csv('latlong.csv', sep=';', usecols=['estado','lat', 'long'])
df_coor = df_coor.drop_duplicates()

df_region2 = df_region.merge(df_coor)




# display the top 20 rows in dataframe
print(df.head(20))

# display the top 20 rows in dataframe
print(df_region.head(20))

fig1 = px.line(df,df.index, 'jair bolsonaro', title='Bolsonaro x Date', labels= {'x': 'Date'})


##########################

fig2 = px.bar(df_region, x=df_region.index, y="jair bolsonaro", color=df_region.index, title = "Bolsonaro x Estado")


##########################


fig3 = px.treemap(df_region, path=[px.Constant('BRASIL'), df_region.index], values='jair bolsonaro',
                  color='jair bolsonaro')

##########################



##########################

# Mapa do Brasil

coordenadas=[]
for lat,lng in zip(df_region2.lat,df_region2.long):
  coordenadas.append([lat,lng])

mapa = folium.Map(location=[-15.788497,-47.879873],zoom_start=4,tiles='Stamen Toner')

mapa.add_child(plugins.HeatMap(coordenadas))

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
               "#### Heatmap do Trends", 
               dp.Plot(mapa),
               "#### Pytrends -> interest_over_time", 
               dp.Plot(fig1),
               "#### Pytrends -> interest_by_region", 
               dp.Plot(fig2),
               "#### Distribution - Treemap", 
               dp.Plot(fig3)
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

     
