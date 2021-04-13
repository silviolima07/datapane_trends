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

# display the top 20 rows in dataframe
print(df.head(20))

fig1 = px.line(df,df.index, 'jair bolsonaro', title='Jair Bolsonaro x Date', labels= {'x': 'Date'})


##########################

#fig1 = px.histogram(df_vagas, x="estado", color="vaga", title=' ', hover_name ='vaga')

#fig1.show()

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
               "#### Heatmap de Vagas pelo Brasil", 
               dp.Plot(fig1),
               "#### Total Vagas", 
               dp.Plot(fig1),
               "#### Total Vagas por Estado", 
               dp.Plot(fig1),
               "#### Total Vagas por Nível", 
               dp.Plot(fig1)
               ]
     ),
    dp.Page(
       label='Cientista de Dados',
       blocks=["#### Vagas - Cientista de Dados",
       dp.DataTable(df, label="Cientista de Dados")]
     ),
    dp.Page(
       label='Analista de Dados',
       blocks=["#### Vagas Analista de Dados", 
       dp.DataTable(df, label= "Analista de Dados")]
     ),
    dp.Page(
       label='Engenheiro de Dados',
       blocks=["#### Vagas - Engenheiro de Dados", 
       dp.DataTable(df, label = "Engenheiro de Dados")]
     ),
    dp.Page(
       label='Engenheiro de Machine Learning',
       blocks=["#### Vagas - Engenheiro de Machine Learning", 
       dp.DataTable(df, label = "Engenheiro de Machine Learning")]
     )
    

    
    

    )
r
# Publish
r.publish(name=f'Google Trends', open = False, description='Analisando termos no google trends')

     
