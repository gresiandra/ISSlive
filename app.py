# -*- coding: utf-8 -*-
"""
Created on Sun Aug 25 10:16:58 2019

@author: ASUS
"""

import pandas as pd
import urllib.request as ur
import json
from threading import Timer
import dash
import plotly.graph_objs as go
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input
import datetime
from datetime import date
from collections import deque
import mapbox
import dash_table
   
#time = Timer(5,iss_loc)
#time.start()

altitude0 = deque(maxlen=12)
altitude1 = []
velocity = []
longitude = []
longitude0 = deque(maxlen=1)
latitude = []
latitude0 = deque(maxlen=1)
locationiss = []
time0 = deque(maxlen=8)
time1 = []
dates = []

#DASH APP
app = dash.Dash()

server = app.server

app.layout = html.Div(children=[
    html.Div([
        html.Img(
            src="https://www.nasa.gov/sites/default/files/thumbnails/image/nasa-logo-web-rgb.png",
            className='three columns',
            style={
                'height': '15%',
                'width': '15%',
                'float': 'right',
                'position': 'relative'}),

        html.H1('Live ISS Location',
            style={
            'font-family': 'Helvetica',
            'textAlign': 'left',
            'margin-left':10,
            'color':'white'}),

    ], style = {'border':'1px solid #C6CCD5', 
                'padding': 15,
                'margin-left':-10,
                'margin-right':-10,
                'margin-top':-10,
                'background-color': '#303952'}),
                
    html.Div([
            
        html.Div([
            html.Div(id='output-container'),
        ],  style = {'width':'50%',
                     'height':600,
                     'float':'left',
                     'margin-bottom':20}
            ),

        html.Div([
            html.Div(id='live-update-text'),
            html.Div(id='output-container0',
                     style = {'margin-left':15}),
        ],  style = {'width':'50%',
                     'height':600,
                     'float':'right',
                     'margin-bottom':20}),

    ], style = {'margin-top': 5,'margin-bottom':630}),
                
    html.Div([
            
        html.Span('Developed by Gresiandra Putra : ',
                  style={'font-family': 'Helvetica',
                         'margin-left':10,
                         'color':'white'
                }),
        
        html.A('gresiandra@gmail.com', 
               href='mailto:gresiandra@gmail.com',
                   style={'font-family': 'Helvetica','color':'white'
                })
        
        ],  style={'font-family': 'Helvetica',
                'border':'1px solid #C6CCD5', 
                'padding': 10,
                'margin-left':-10,
                'margin-right':-10,
                'margin-bottom':-10,
                'background-color': '#303952',
                }),

        dcc.Interval(
            id='interval-component',
            interval=10*1000, # in milliseconds
            n_intervals=5
        ),
                
])
            
@app.callback(Output('output-container', 'children'),
              [Input('interval-component', 'n_intervals')])

def update_output1(n):
    
    response = ur.urlopen("https://api.wheretheiss.at/v1/satellites/25544")
    
    json_content = json.loads(response.read())
    longitude0.append(json_content['longitude'])
    latitude0.append(json_content['latitude'])
    
    return dcc.Graph(
        id='mapbox',
        figure={
            'data': [
                go.Scattermapbox(
                    lat=list(latitude0),
                    lon=list(longitude0),
                    mode='markers',
                    marker=go.scattermapbox.Marker(
                        size=9
                    ), hoverinfo='text'
                )
            ],
            'layout':go.Layout(autosize=False,
                        mapbox= dict(accesstoken="pk.eyJ1IjoiZ3Jlc2lhbmRyYSIsImEiOiJjanpxbmJpbXEwbmtiM2JvYmExOWkzYmV2In0.r10NAfXhqvZm5TXTG1Eg6w",
                                    bearing=0, pitch=30, zoom=3,
                                    center= dict(lat=latitude0[-1], lon=longitude0[-1])),
                        width = 600,
                        height = 600,
                        margin=dict(
                            l=10, r=5,
                            b=5, t=5
                        ),
                    )
        },
    ),

@app.callback(Output('live-update-text', 'children'),
              [Input('interval-component', 'n_intervals')])

def update_metrics(n):
    try:
        geocoder = mapbox.Geocoder(access_token='pk.eyJ1IjoiZ3Jlc2lhbmRyYSIsImEiOiJjanpxbmJpbXEwbmtiM2JvYmExOWkzYmV2In0.r10NAfXhqvZm5TXTG1Eg6w')
        response = geocoder.reverse(lon=longitude[-1], lat=latitude[-1])
        result = response.json()
        address0 = result['features'][0]['place_name']
        locationiss.append(address0)
    except:
        locationiss.append('Somewhere On The Ocean')
        
    return html.H3(str(locationiss[-1]),
                    style={
                        'font-family': 'Helvetica',
                        'textAlign': 'center',
                        'border':'3px solid #303952',
                        'padding':15,
                        'margin-right':15,
                        'fontSize': '13px',
                        'border-radius':5,
                        'color':'#303952'}),
                        
                        
@app.callback(Output('output-container0', 'children'),
             [Input('interval-component', 'n_intervals')])

def update_output0(n):
    
    time1.append(datetime.datetime.now().strftime('%H:%M:%S'))
    today = date.today()
    dates.append(today)
    
    response = ur.urlopen("https://api.wheretheiss.at/v1/satellites/25544")
    
    json_content = json.loads(response.read())
    longitude.append(json_content['longitude'])
    latitude.append(json_content['latitude'])
    altitude1.append(json_content['altitude'])
    velocity.append(json_content['velocity'])
   
    df = pd.DataFrame(zip(dates,time1,latitude,longitude,altitude1,velocity), 
                      columns=['Dates','Time','Latitude','Longitude','Altitude','Velocity'])
    
    dfd = df.round({'Dates': 0,'Time': 0,'Latitude': 4,'Longitude': 4,'Altitude': 1, 'Velocity': 1})
#    print(dfd)
    
    return dash_table.DataTable(
        data=dfd.to_dict('records'),
        columns=[{'id': c, 'name': c} for c in dfd.columns],
        style_as_list_view=True,
        style_data_conditional=[
        {
            'if': {'row_index': 'odd'},
            'backgroundColor': 'rgb(248, 248, 248)'
        }],
        style_table={
                'maxHeight':490,
                'alignment': 'center',
                },
        fixed_rows={
                'headers': True,
                'data': 0 
                },
        style_header={
                'backgroundColor': '#303952',
                'fontWeight': 'bold',
                'height': 60,
                'color':'white'
                },
        style_cell={
                'textAlign': 'center',
                'width': 95,
                'height': 70,
                }
        
    ),


if __name__ == '__main__':
    app.run_server(debug=False)