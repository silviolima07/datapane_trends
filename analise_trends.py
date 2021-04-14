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

# Timeframe - irá pesquisar os termos escolhidos de hoje até 5 anos atrás.
pytrends.build_payload(kw_list, timeframe='today 5-y', geo='BR')

# store interest over time information in df
df = pytrends.interest_over_time()

# Filter last 3 years

df['year'] = df.index
df['year'] = df.year.dt.year
df = df.loc[df.year > 2017]
df = df[['covid', 'lockdown', 'jair bolsonaro']]
df['date'] = pd.to_datetime(df.index, format='%d/%m/%y')

df_region = pytrends.interest_by_region(resolution='REGION', inc_low_vol=True, inc_geo_code=False)

df_region['estado'] = df_region.index

# Arquivo csv com as coordenadas de latitude e longitude de cada Estado.
df_coor = pd.read_csv('latlong.csv', sep=';', usecols=['estado','lat', 'long'])
df_coor = df_coor.drop_duplicates()

# Criado dataset com as informações de interesse por Estado e suas coordenadas.
df_region2 = df_region.merge(df_coor)

#################################


# Mostra o interesse ao longo do tempo nos termos escolhidos
print(df.head(20))

# Mostra o interesse por região nos termos escolhidos
print(df_region.head(20))

##################################

# Fig1 é gráfico gerado do interesse dos termos escolhidos ao longo do tempo.

fig1_bol = px.line(df,df.date, 'jair bolsonaro', title='Bolsonaro x Date')

fig1_covid = px.line(df,df.date, 'covid', title='Covid x Date')

fig1_lock = px.line(df,df.date, 'lockdown', title='Lockdown x Date')


##########################

# Fig2 é gráfico gerado do interesse dos termos escolhidos por Estado.

fig2_bol = px.bar(df_region, x=df_region.estado, y="jair bolsonaro", title = "Bolsonaro x Estado")

fig2_covid = px.bar(df_region, x=df_region.estado, y="covid", title = "Covid x Estado")

fig2_lock = px.bar(df_region, x=df_region.estado, y="lockdown", title = "Lockdown x Estado")


##########################

# Fig3 é gráfico gerado do interesse dos termos escolhidos por Estado.

fig3_bol = px.treemap(df_region, path=[px.Constant('Termo Jair Bolsonaro pelo BRASIL'), df_region.index], values='jair bolsonaro',
                  color='jair bolsonaro')
                  
fig3_covid = px.treemap(df_region, path=[px.Constant('Termo Covid no BRASIL'), df_region.index], values='covid',
                  color='covid')

fig3_lock = px.treemap(df_region, path=[px.Constant('Termo Lockdown no BRASIL'), df_region.index], values='lockdown',
                  color='lockdown')                  

##########################

# Plataformas de Cloud
search_list = ["AWS", "AZURE", "GCP"]

# Pesquisando os últimos 5 anos
pytrends.build_payload(search_list, timeframe='today 5-y', geo='BR')

df_ibr = pytrends.interest_by_region(resolution='REGION', inc_low_vol=True, inc_geo_code=False)

# Ordenar e Plotar

import plotly.graph_objects as go

df2 = df_ibr.sort_values('AWS', ascending=False).head(20)
x=df2.index
fig_clouds = go.Figure(go.Bar(x=x, y=df2.AWS, name='AWS'))
fig_clouds.add_trace(go.Bar(x=x, y=df2.AZURE, name='AZURE'))
fig_clouds.add_trace(go.Bar(x=x, y=df2.GCP, name='GCP'))

fig_clouds.update_layout(barmode='stack', xaxis={'categoryorder':'category ascending'}, )
fig_clouds.show()


#######################

# Create report

r = dp.Report(
    dp.Page(
       label='Trend search Cloud Plataforma',
       blocks=[
               "#### AWS, AZURE e GCP ",
               dp.Plot(fig_clouds)]
     ),
    dp.Page(
       label='Covid',
       blocks=[
               #"#### Heatmap do termo Covid no Brasil", 
               #dp.Plot(mapa_covid),
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
       blocks=[
               #"#### Heatmap do termo Jair Bolsonaro no Brasil", 
               #dp.Plot(mapa_jair_bolsonaro),
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
       blocks=[
               #"#### Heatmap do termo Lockdown no Brasil", 
               #dp.Plot(mapa_lockdown),
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
r.publish(name=f'Google Trends com Python Pytrends', open = True, description='Analisando de jan/2018 até hoje, os termos: Covid, Jair Bolsonaro e Lockdown')

     
