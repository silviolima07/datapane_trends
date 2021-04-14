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
#df = pytrends.interest_over_time()
df_ot = pd.DataFrame(pytrends.interest_over_time()).drop(columns='isPartial')

# Filter last 3 years

df_ot['date'] = df_ot.index
df_ot['date'] = df_ot.date.dt.year
df_ot = df_ot.loc[df_ot.date > 2017]

df_region = pytrends.interest_by_region(resolution='REGION', inc_low_vol=True, inc_geo_code=False)

df_region['estado'] = df_region.index

#################################


# Mostra o interesse ao longo do tempo nos termos escolhidos
print(df_ot.head(20))

# Mostra o interesse por região nos termos escolhidos
print(df_region.head(20))

##################################

# Fig1 é gráfico gerado do interesse dos termos escolhidos ao longo do tempo.

fig1_covid = px.line(df_ot,df_ot.index, 'covid', title='Covid x Date', labels= {'index':'date'})

fig1_lock = px.line(df_ot,df_ot.index, 'lockdown', title='Lockdown x Date', labels= {'index':'date'})


##########################

# Fig2 é gráfico gerado do interesse dos termos escolhidos por Estado.

fig2_covid = px.bar(df_region, x=df_region.estado, y="covid", title = "Covid x Estado")

fig2_lock = px.bar(df_region, x=df_region.estado, y="lockdown", title = "Lockdown x Estado")


##########################

# Fig3 é gráfico gerado do interesse dos termos escolhidos por Estado.
                  
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

df2 = df_ibr.sort_values('AWS', ascending=False)
x=df2.index
fig_clouds = go.Figure(go.Bar(x=x, y=df2.AWS, name='AWS'))
fig_clouds.add_trace(go.Bar(x=x, y=df2.AZURE, name='AZURE'))
fig_clouds.add_trace(go.Bar(x=x, y=df2.GCP, name='GCP'))

fig_clouds.update_layout(barmode='stack', xaxis={'categoryorder':'category ascending'}, )
fig_clouds.show()


#######################

search_list = ["LINGUAGEM R", "LINGUAGEM PYTHON"]
pytrends.build_payload(search_list, timeframe='today 5-y', geo='BR')

df_linguagens_ot = pd.DataFrame(pytrends.interest_over_time()).drop(columns='isPartial')
# Gerar a coluna year com o data completa vinda do index
df_linguagens_ot['date'] = df_linguagens_ot.index

fig_R = px.line(df_linguagens_ot,df_linguagens_ot.index,'LINGUAGEM R', title='Linguagem R x Date', labels= {'index':'date'})
fig_R

fig_python = px.line(df_linguagens_ot,df_linguagens_ot.index,'LINGUAGEM PYTHON', title='Linguagem PYTHON x Date', labels= {'index':'date'})
fig_python




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
       label='Trend search Linguagens',
       blocks=[
               "#### Scatter Plot -> interest_over_time of Python",
               dp.Plot(fig_python),
               "### Scatter Plot -> interest_over_time of R",
               dp.Plot(fig_R)]
     ),
    dp.Page(
       label='Trend search Covid',
       blocks=[
               "#### Scatter Plot -> interest_over_time", 
               dp.Plot(fig1_covid),
               "#### Bar Plot -> interest_by_region", 
               dp.Plot(fig2_covid),
               "#### Treemap - > interest_by_region", 
               dp.Plot(fig3_covid)
               ]
     ),
    dp.Page(
       label='Trend search Lockdown',
       blocks=[
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
r.publish(name=f'Google Trends com Python Pytrends', open = True, description='Analisando: interest_over_time e interest_by_region')

     
