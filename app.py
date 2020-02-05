import json
import geopandas as gpd
import plotly.express as px
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output

bm = gpd.read_file('output/merged_data.geojson')
with open("output/merged_data.geojson") as geofile:
    j_file = json.load(geofile)

for feature in j_file["features"]:
    feature['id']= feature['properties']['Mun_Code']

app = dash.Dash(__name__, external_stylesheets=["https://codepen.io/chriddyp/pen/bWLwgP.css"])

server = app.server

app.layout = html.Div(
    [
        html.H1("Demo: Plotly Express in Dash with Tips Dataset"),
        html.Div(
            [
                html.P(["risk:", dcc.Dropdown(id="risk", value='high',
                    options=[{'label':'high','value':'high'},{'label':'med','value':'med'},
                            {'label':'med_sea','value':'med_sea'},])])
            ],
            style={"width": "25%", "float": "left"},
        ),
        dcc.Graph(id="graph", style={"width": "75%", "display": "inline-block"}),
    ]
)

@app.callback(Output("graph", "figure"), [Input("risk", "value")])
def make_figure(risk):
    return px.choropleth_mapbox(bm[['Mun_Name','Mun_Code','high','med', 'med_sea']], geojson=j_file, locations='Mun_Code',
                           color=risk, color_continuous_scale='reds', range_color=(1,0),
                           mapbox_style="carto-darkmatter", zoom=6, center = {"lat": 6.509640, "lon": 121.648446},
                           opacity=0.5,labels={'Mun_Name':'Municipality','high':'risk'})

if __name__ == '__main__':
    app.run_server(debug=True)
