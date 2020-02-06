import json
import numpy as np
import geopandas as gpd
import plotly.express as px
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output

#Data Extract
bm = gpd.read_file('output/merged_data.geojson')
with open("output/merged_data.geojson") as geofile:
    j_file = json.load(geofile)

for feature in j_file["features"]:
    feature['id']= feature['properties']['Mun_Code']

app = dash.Dash(__name__, external_stylesheets=["https://codepen.io/chriddyp/pen/bWLwgP.css"])

server = app.server

#Lists
risks = ['high', 'med', 'med_sea']
risk_alias = ['High (Magnitude > 5)', 'Mid (Magnitude < 5)', 'Mid Sea (Magnitude < 5)']
mapstyles = ['open-street-map','basic','streets','outdoors','light','dark','satellite']
colorscales =  ['aggrnyl', 'agsunset', 'algae', 'amp', 'armyrose', 'balance',
             'blackbody', 'bluered', 'blues', 'blugrn', 'bluyl', 'brbg',
             'brwnyl', 'bugn', 'bupu', 'burg', 'burgyl', 'cividis', 'curl',
             'darkmint', 'deep', 'delta', 'dense', 'earth', 'edge', 'electric',
             'emrld', 'fall', 'geyser', 'gnbu', 'gray', 'greens', 'greys',
             'haline', 'hot', 'hsv', 'ice', 'icefire', 'inferno', 'jet',
             'magenta', 'magma', 'matter', 'mint', 'mrybm', 'mygbm', 'oranges',
             'orrd', 'oryel', 'peach', 'phase', 'picnic', 'pinkyl', 'piyg',
             'plasma', 'plotly3', 'portland', 'prgn', 'pubu', 'pubugn', 'puor',
             'purd', 'purp', 'purples', 'purpor', 'rainbow', 'rdbu', 'rdgy',
             'rdpu', 'rdylbu', 'rdylgn', 'redor', 'reds', 'solar', 'spectral',
             'speed', 'sunset', 'sunsetdark', 'teal', 'tealgrn', 'tealrose',
             'tempo', 'temps', 'thermal', 'tropic', 'turbid', 'twilight',
             'viridis', 'ylgn', 'ylgnbu', 'ylorbr', 'ylorrd']

#Interactions
risks_dropdown =  dcc.Dropdown(id="risk", value='high',
        options=[{'label':risk[0],'value':risk[1]} for risk in zip(risk_alias,risks)])

mapstyles_dd = dcc.Dropdown(id='mapstyle', value='light',
        options = [{'label':mapstyle.title(),'value':mapstyle} for mapstyle in mapstyles])

colorscale_dd = dcc.Dropdown(id='colorscale', value='spectral',
        options = [{'label':colorscale.title(), 'value':colorscale} for colorscale in colorscales])

reversecolorscale_checklist = dcc.Checklist(id='reverse_color', value = [],
        options = [{'label':'Reverse Color Scale', 'value':'_r'}])

opacity_slider = dcc.Slider(id='opacity', min=0, max=1, value=0.8, step=0.1,
        marks={tick: str(tick)[0:3] for tick in np.linspace(0,1,11)},)

app.layout = html.Div(
    [
        html.H1("BARMM Earthquake Hazard Map"),
        html.Div(
            [

                html.P(["Risk:", risks_dropdown, 'Map Styles:', mapstyles_dd, 'Color Scale:', colorscale_dd, reversecolorscale_checklist,
                    "Choropleth Opacity:", opacity_slider])
            ],
            style={"width": "25%", "float": "left"},
        ),
        dcc.Graph(id="graph", style={"width": "75%", "display": "inline-block"}),
    ]
)

px.set_mapbox_access_token('pk.eyJ1Ijoia2V2c2VzdHJlbGxhIiwiYSI6ImNrNWlwcWpvZDBoNGEza21zeDc0OWczeDIifQ.-ajWL8TrUDMCN1OzzXTjhg')

@app.callback(Output("graph", "figure"), [Input("risk", "value"), Input("mapstyle", "value"), Input("colorscale", "value"),
    Input('reverse_color','value'), Input("opacity", "value")])
def make_figure(risk, mapstyle, colorscale, reverse, opacity):
    fig = px.choropleth_mapbox(bm[['Mun_Name','Mun_Code','POPULATION','high','med', 'med_sea']], geojson=j_file, locations='Mun_Code',
                           color=risk, color_continuous_scale=colorscale+''.join(reverse), range_color=(0,1),
                           mapbox_style=mapstyle, zoom=6, center = {"lat": 6.509640, "lon": 121.648446},
                           opacity=opacity, labels={'Mun_Name':'Municipality',risk:'risk', 'POPULATION':'Population'}, 
                           hover_data = ['Mun_Name', 'POPULATION'])
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, showlegend=False)
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
