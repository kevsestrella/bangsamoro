#!/usr/bin/env python
# coding: utf-8

# # Bangsamoro Earthquake Data Visualization
# ## Links
# 1. https://towardsdatascience.com/how-to-create-an-interactive-geographic-map-using-python-and-bokeh-12981ca0b567
# 
# ## Instructions(Local)
# 0. Make sure packages required are installed : `pip install -r requirements.txt`
# 1. Running this notebook is not needed. We can go directly to command line and run `bokeh serve path/to/this/ipynb --show`
# 2. Open localhost:5006/earthquake on your browser or whatever link is provided after step 1
# 3. Wait for a while as bokeh is quite slow(possibly depend on your machine)
# 
# ## Todo
# 1. Include non BARMM Geodata as the visualization has a lot of white space, but gray out this non BARMM as this is not part of the project
# 2. Fix hover, it is not working when changing to medium risk earthquake data
# 3. Deploy to heroku
# 4. See if PWA/Offline App possible

# In[1]:


import pandas as pd
import numpy as np
import math

import geopandas as gpd
import shapely.geometry as gm
import json

from bokeh.io import output_notebook, show, output_file
from bokeh.plotting import figure
from bokeh.models import GeoJSONDataSource, LinearColorMapper, ColorBar, NumeralTickFormatter
from bokeh.palettes import brewer

from bokeh.io.doc import curdoc
from bokeh.models import Slider, HoverTool, Select
from bokeh.layouts import widgetbox, row, column


# # Geo Data Preparation

# In[2]:


highrisk = pd.read_csv('data/high_risk0.csv')
medrisk = pd.read_csv('data/medium.csv')
medrisk10 = pd.read_csv('data/medium1_risk0.csv')
medrisk20 = pd.read_csv('data/medium2_risk0.csv')


# In[3]:


highrisk = gpd.GeoDataFrame(highrisk.drop(['latitude','longitude'],axis=1), crs={'init': 'epsg:4326'} ,geometry = [gm.Point(latlong) for latlong in zip(highrisk.longitude, highrisk.latitude)])
medrisk = gpd.GeoDataFrame(medrisk.drop(['latitude','longitude'],axis=1), crs={'init': 'epsg:4326'} ,geometry = [gm.Point(latlong) for latlong in zip(medrisk.longitude, medrisk.latitude)])
medrisk10 = gpd.GeoDataFrame(medrisk10.drop(['latitude','longitude'],axis=1), crs={'init': 'epsg:4326'} ,geometry = [gm.Point(latlong) for latlong in zip(medrisk10.longitude, medrisk10.latitude)])
medrisk20 = gpd.GeoDataFrame(medrisk20.drop(['latitude','longitude'],axis=1), crs={'init': 'epsg:4326'} ,geometry = [gm.Point(latlong) for latlong in zip(medrisk20.longitude, medrisk20.latitude)])


# In[4]:


bm = gpd.read_file('mapdata/AdministrativeBoundariesBARMMMunicipalities20190206PSA2016.dbf')


# In[5]:


bm = bm.to_crs(epsg=4236)


# # Initial Visualizations

# In[10]:


#x = bm.plot(color='lightblue', edgecolor='gray', figsize=(30,30))
#y = bm.plot(color='lightblue', edgecolor='gray', figsize=(30,30))
#z = bm.plot(color='lightblue', edgecolor='gray', figsize=(30,30))


# In[12]:


#highrisk.plot(ax=x, color='red')


# In[13]:


#medrisk.plot(ax=x, color='orange')


# In[ ]:


#x.get_figure()


# In[15]:


#medrisk10.plot(ax=y, color='orange')
#medrisk20.plot(ax=y, color='orange')


# In[ ]:


#y.get_figure()


# # Geo Data Preprocessing

# In[6]:


lenbm = len(bm)
lenhr = len(highrisk)
lenmdr = len(medrisk)#combine all medrisk
bm_range = range(lenbm)
highrisk_range = range(lenhr)
medrisk_range = range(lenmdr)


# In[7]:


bangsamoro_risk = {'high':[],'med':[]}
max_geo_distance = 180 #guessing that max distance of geoobjects is 180'.''
for x in bm_range:
    municipal_highrisk = 0
    municipal_medrisk = 0
    for y in highrisk_range:
        municipal_highrisk += bm.geometry[x].centroid.distance(highrisk.geometry[y])
    for z in medrisk_range:
        municipal_medrisk += bm.geometry[x].centroid.distance(medrisk.geometry[z])
    bangsamoro_risk['high'].append(lenhr*max_geo_distance-municipal_highrisk)
    bangsamoro_risk['med'].append(lenmdr*max_geo_distance-municipal_medrisk)


# In[8]:


#add normalized to geodata for choropleth
bm['high'] = bangsamoro_risk['high']
bm['high'] = bm['high']/bm['high'].max()
bm['med'] = bangsamoro_risk['med']
bm['med'] = bm['med']/bm['med'].max()


# # Bokeh Visualization

# In[22]:


def update_plot(attr,old,new):
    severity=select.value
    new_data = json_data(severity)
    #input_field
    geosource.geojson = new_data
    hover = HoverTool(tooltips = [('Municipality','@Mun_Name'),(severity+' risk','@'+severity)])
    p = make_plot(severity)
    layout=column(p,widgetbox(select))
    curdoc().clear()
    curdoc().add_root(layout)


# In[10]:


def json_data(severity):
    if severity == 'high':
        return json.dumps(json.loads(bm.drop('med', axis=1).to_json()))
    return json.dumps(json.loads(bm.drop('high',axis=1).to_json()))    


# In[26]:


def make_plot(severity):
    color_mapper = LinearColorMapper(palette=palette,low=bm[severity].min(), high=bm[severity].max())
    #format_tick = NumeralTickFormatter(format='0.0')
    color_bar = ColorBar(color_mapper=color_mapper, location=(0,0))
    p = figure(title='Title', plot_height = 650, plot_width = 850, toolbar_location = None)
    #p = figure()
    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = None
    p.axis.visible = False
    p.patches('xs', 'ys', source=geosource, fill_color = {'field' : severity, 'transform' : color_mapper}, line_color = 'gray', line_width = 0.25, fill_alpha = 1)
    p.add_layout(color_bar, 'right')
    p.add_tools(hover)
    return p


# In[12]:


severity = 'med'
geosource = GeoJSONDataSource(geojson = json_data(severity))


# In[27]:


palette = brewer['Blues'][8]
palette = palette[::-1]
hover = HoverTool(tooltips = [('Municipality','@Mun_Name'),(severity+' risk','@'+severity)])
p = make_plot(severity)
select = Select(title='Select Severity:', value=severity, options=['high','med'])
#maybe we could add toggle for epicenters and evacuation centers
select.on_change('value', update_plot)
layout=column(p, widgetbox(select))
curdoc().add_root(layout)


# In[20]:


#output_notebook() #comment out when deploying to heroku


# In[68]:


#p= figure() #comment out when deploying to heroku


# In[28]:


#show(p) #comment out when deploying to heroku

