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
df['year'] = df.year.dt.year
df = df.loc[df.year > 2017]
df = df[['covid', 'lockdown', 'jair bolsonaro']]

df_region = pytrends.interest_by_region(resolution='REGION', inc_low_vol=True, inc_geo_code=False)

df_region['estado'] = df_region.index

df_coor = pd.read_csv('latlong.csv', sep=';', usecols=['estado','lat', 'long'])
df_coor = df_coor.drop_duplicates()

df_region2 = df_region.merge(df_coor)




# display the top 20 rows in dataframe
print(df.head(20))

# display the top 20 rows in dataframe
print(df_region.head(20))

fig1_bol = px.line(df,df.index, 'jair bolsonaro', title='Bolsonaro x Date', labels= {'x': 'Date'})

fig1_covid = px.line(df,df.index, 'covid', title='Covid x Date', labels= {'x': 'Date'})

fig1_lock = px.line(df,df.index, 'lockdown', title='Lockdown x Date', labels= {'x': 'Date'})


##########################

fig2_bol = px.bar(df_region, x=df_region.index, y="jair bolsonaro", title = "Bolsonaro x Estado")

fig2_covid = px.bar(df_region, x=df_region.index, y="covid", title = "Covid x Estado")

fig2_lock = px.bar(df_region, x=df_region.index, y="lockdown", title = "Lockdown x Estado", labels= {'x': 'estado'})


##########################


fig3_bol = px.treemap(df_region, path=[px.Constant('BRASIL'), df_region.index], values='jair bolsonaro',
                  color='jair bolsonaro')
                  
fig3_covid = px.treemap(df_region, path=[px.Constant('BRASIL'), df_region.index], values='covid',
                  color='covid')

fig3_lock = px.treemap(df_region, path=[px.Constant('BRASIL'), df_region.index], values='lockdown',
                  color='lockdown')                  

##########################



##########################

# Mapa do Brasil

def setar_coordenadas(df):
    coordenadas=[]
    for lat,lng in zip(df['lat'],df['long']):
        coordenadas.append([lat,lng])
    return coordenadas
    
df_region_covid = df_region2[['covid', 'lat', 'long']]
df_region_jair_bolsonaro = df_region2[['jair bolsonaro', 'lat', 'long']]
df_region_lockdown = df_region2[['lockdown', 'lat', 'long']]


#coordenadas=[]
#for lat,lng in zip(df_region_covid.lat,df_region_covid.long):
#  coordenadas.append([lat,lng])

coordenadas_covid = setar_coordenadas(df_region_covid)
coordenadas_jair_bolsonaro = setar_coordenadas(df_region_jair_bolsonaro)
coordenadas_lockdown = setar_coordenadas(df_region_lockdown)

mapa = folium.Map(location=[-15.788497,-47.879873],zoom_start=4,tiles='Stamen Toner')

mapa_covid = mapa.add_child(plugins.HeatMap(coordenadas_covid))
mapa_jair_bolsonaro = mapa.add_child(plugins.HeatMap(coordenadas_jair_bolsonaro))
mapa_lockdown = mapa.add_child(plugins.HeatMap(coordenadas_lockdown))    


####
#title_html = '''
#             <h3 align="center" style="font-size:20px"><b>Heatmap de vagas pelo Brasil</br></br></b></h3>
#             '''
#mapa.get_root().html.add_child(folium.Element(title_html))

#######################

# Create report

r = dp.Report(
    dp.Page(
       label='Covid',
       blocks=[
               "#### Heatmap do termo Covid pelo Brasil", 
               dp.Plot(mapa_covid),
               "#### Scatter Plot -> interest_over_time", 
               dp.Plot(fig1_covid),
               "#### Bar Plot -> interest_by_region", 
               dp.Plot(fig2_covid),
               "#### Treemap - > interest_by_region", 
               dp.Plot(fig3_covid)
               ]
     ),
    dp.Page(
       label='Bolsonaro',
       blocks=["#### Heatmap do termo Jair Bolsonaro pelo Brasil", 
               dp.Plot(mapa_jair_bolsonaro),
               "#### Scatter Plot -> interest_over_time", 
               dp.Plot(fig1_bol),
               "#### Bar Plot -> interest_by_region", 
               dp.Plot(fig2_bol),
               "#### Treemap - > interest_by_region", 
               dp.Plot(fig3_bol)
               ]
     ),
    dp.Page(
       label='Lockdown',
       blocks=["#### Heatmap do termo Lockdown pelo Brasil", 
               dp.Plot(mapa_lockdown),
               "#### Scatter Plot -> interest_over_time", 
               dp.Plot(fig1_lock),
               "#### Bar Plot - > interest_by_region", 
               dp.Plot(fig2_lock),
               "#### Treemap - > interest_by_region", 
               dp.Plot(fig3_lock)
               ]
     )
    )
r
# Publish
r.publish(name=f'Google Trends', open = False, description='Analisando de jan/2018 até hoje, os termos: Covid, Jair Bolsonaro e Lockdown')

     
