# Libraries
import streamlit as st
import pandas as pd
import geopandas as gpd
from geopandas import GeoDataFrame
import matplotlib.pyplot as plt
import numpy as np
import json
import plotly.express as px



# Loading Data
data = pd.read_csv('datasets/Perda_Florestal.csv')
data_drivers = pd.read_csv('datasets/Dominant_Drivers.csv')
geo_data = gpd.read_file('datasets/Geo_Estados.gpkg')

#Loading Geo Estados
geometry = []
for g in range(27):
  geo = geo_data.loc[g:g,'geometry'].to_json()
  #geo = geo.split(':')[8]
  #geo = geo.split('"')[0]
  #geo = geo.split('}')[0]
  geometry.append(geo)

# Addind Sidebar
st.sidebar.header('Análise do Brasil:')
# -- Year
years = [2001,2002,2003,2004,2005,2006,2007,2008,2009,2010,2011,2012,2013,2014,2015,2016,2017,2018,2019,2020,2021]
default_year = years.index(2021)
side_year = st.sidebar.selectbox('Ano', years, index=default_year)


# -- Estados
estados = ['<select>','Acre','Alagoas','Amapá','Amazonas','Bahia','Ceará','Distrito Federal',
'Espírito Santo','Goiás','Maranhão','Mato Grosso','Mato Grosso do Sul','Minas Gerais','Pará',
'Paraíba','Paraná','Pernambuco','Piauí','Rio de Janeiro','Rio Grande do Norte','Rio Grande do Sul',
'Rondônia','Roraima','Santa Catarina','São Paulo','Sergipe','Tocantins'
]
side_estados = st.sidebar.selectbox('Estados',estados)

# Body
st.title('Perda Florestal no Brasil')

col1,col2 = st.columns([2,1])
#-- 
year = 0
for i in years:
  if side_year == i:
    data_y = data.loc[data['year'] == i].reset_index(drop=True)
    data_year = geo_data.merge(data_y,on = 'id')
    year = i

with col1:
  st.header(year)
  st.subheader("Perda Florestal nos Estados em Hectares") 
  #Maps:
  # set the value column that will be visualised
  column = 'area_ha'

  # set the range for the choropleth values
  vmin = data_year['area_ha'].min()
  vmax = data_year['area_ha'].max()

  # create figure and axes for Matplotlib
  fig, ax = plt.subplots(1, figsize=(11,15))

  # remove the axis
  ax.axis('off')

  # add a title and annotation
  #ax.set_title('Perda Florestal nos Estados - ha', fontdict={'fontsize': '25', 'fontweight' : '3'})
  ax.annotate('Source: Global Forest Watch', xy=(0.4, .08), xycoords='figure fraction', fontsize=20, color='#555555')

  # Create colorbar legend
  sm = plt.cm.ScalarMappable(cmap='PuRd', norm=plt.Normalize(vmin=vmin, vmax=vmax))

  # empty array for the data range
  sm.set_array([]) # or alternatively sm._A = []. Not sure why this step is necessary, but many recommends it

  #add the colorbar to the figure
  fig.colorbar(sm,orientation='horizontal',fraction=0.046, pad=0.04).set_label(label='Hectares',size=20)
  ax.margins(x=0,y=-0.01)
  # create map
  data_year.plot(column=column, cmap='PuRd', linewidth=0.8, ax=ax, edgecolor='0.8')
  st.write(fig)

with col2:
  st.subheader('')
  st.subheader('Estados com Maior Perda Florestal')

  # Ranking
  data_year_rank = data_year[['nome','area_ha']].sort_values('area_ha',ascending=False).reset_index(drop=True)
  data_year_rank.index =range(1, data_year_rank.shape[0] + 1)
  st.write(data_year_rank.head())

  with st.expander ('Outros Estados:'):
    st.write(data_year_rank.loc[6:])

# Creating the Perda Florestal brasileira ao longo dos anos chart
data_perda_years = data[['year','area_ha']].groupby('year').sum()
data_perda_years = data_perda_years.reset_index()

fig1, ax1 = plt.subplots(1)

y= data_perda_years['area_ha'].tolist()
x= data_perda_years['year'].tolist()

plt.bar(x,y,color='#9c3a6c',edgecolor='grey')
plt.title(' Perda Florestal Brasileira ao longo dos Anos')
plt.xlabel('Anos')
plt.ylabel('Hectares em milhoes')

with st.expander ('Perda Florestal Brasileira ao longo dos Anos') :
  st.write(fig1)

# Creating Chart By Dominant Driver:
drivers = data_drivers.loc[data_drivers['year'] == year,['dominant_driver','area_ha']].groupby('dominant_driver').sum()

commodities = drivers.loc[1].values[0]
itinerant = drivers.loc[2].values[0]
floresta = drivers.loc[3].values[0]
queimadas = drivers.loc[4].values[0]
urbanizacao = drivers.loc[5].values[0]

labels=['Commodities','Agricultura Itinerante','','','']
sizes = [commodities,itinerant,floresta,queimadas,urbanizacao]
colors = ['#980043','#dd1c77','#df65b0','#c994c7','#d4b9da']

fig5, ax5 = plt.subplots()
ax5.pie(sizes, labels=labels, autopct='%1.1f%%',shadow=False, startangle=90,colors=colors)
ax5.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
col1_2, col2_1 =  st.columns([2,1])

with col1_2:
  with st.expander ('Principais Causas de Perda Florestal') :
    st.text(year)
    st.write(fig5)
    st.text('1 - Commodities             4 - Queimadas')
    st.text('2 - Agricultura Itinerante  5 - Urbanização ')
    st.text('3 - Florestas')

with col2_1:
  with st.expander ('Dados:') :
    st.write(drivers)
#Estados Map
estado = ''
for i in estados:
  if side_estados == i:
    estado = i

col3,col4 = st.columns([2,1])

if estado == '<select>':
    st.write('')
else:
  with col3:
    index_estados = data_year.loc[data_year['nome'] == estado,'id'].values[0]
    data_estados = data_year.loc[index_estados:index_estados]

    st.write('')
    st.subheader(estado)
    fig2, ax2 = plt.subplots(1, figsize=(15,15))
    ax2.axis('off')
    data_estados.plot(column='area_ha',color='#cc0052', linewidth=0.8, ax=ax2, edgecolor='black')
    st.write(fig2)

  with col4:
    st.text('')
    st.text('')
    st.text('')
    st.text('')
    st.text('')
    st.write('Area de Perda Florestal:')
    st.text(year)
    area_estado = data_year['area_ha'].loc[data_year['nome'] == estado].values[0]
    st.write(area_estado)

    #Pie Chart
    st.write('Porcentagem me relação ao país:')
    area_total =data_year['area_ha'].sum()
    area_resto = area_total - area_estado

    labels=['',estado]
    sizes = [area_resto,area_estado]
    explode = (0, 0.1)  # only "explode" the 2nd slice

    fig3, ax3 = plt.subplots(figsize=(5,5))
    ax3.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',shadow=False, startangle=90, colors=['#ffe6f0','#cc0052'])
    ax3.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    st.pyplot(fig3)

  # Evolução da Perda florestal dos Estados nos Anos:
  
  estados_anos = data[['year','area_ha']].loc[data['nome'] == estado]

  fig4, ax4 = plt.subplots(1)

  y= estados_anos['area_ha'].tolist()
  x= estados_anos['year'].tolist()

  plt.bar(x,y,color='#9c3a6c',edgecolor='grey')
  plt.xlabel('Anos')
  plt.ylabel('Hectares')

  with st.expander ('Evolução da Perda florestal nos Anos:') :
    st.write(estado)
    st.write(fig4)
  
