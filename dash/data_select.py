import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import datetime as dt

import pandas as pd
import plotly.graph_objs as go

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


df = pd.read_csv('2018-09-30-Data.csv')
# convert data type of time to datetime
df[['_source.time']] = df[['_source.time']].apply(pd.to_datetime)

# we are interested in time, ambient temperature and humidity, and soil temperature and humidity
df_coffee_farm = df[['_source.time','_source.dev_id',
                     '_source.temperature_2', '_source.relative_humidity_3',
                     '_source.analog_in_4', '_source.analog_in_5']]
df_coffee_farm.columns = ['time','dev_id','Ambient Temperature',
                          'Relative Humidity', 'Soil Temperature', 'Soil Moisture']

# sorting based on time
df_coffee_farm.sort_values(by='time');

devices = [{'label': i, 'value': i} for i in list(df_coffee_farm.dev_id.unique())]
parameter_labels = ['Ambient Temperature',
                    'Relative Humidity',
                    'Soil Temperature',
                    'Soil Moisture']
parameters = [{'label': i, 'value': i} for i in parameter_labels]
parameter_ranges = [[0, 40], [0, 110], [0, 70], [0, 110]]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div([
    html.Div([
        dcc.Dropdown(
            id='device-dropdown',
            options=devices,
            placeholder="Select a Greenhouse",
            style={'height': '30px', 'width': '250px'}
            #value=devices[0]['value']
        ),
        html.P()
    ]),
    html.Div([
        dcc.Dropdown(
            id='parameter-dropdown',
            options=parameters,
            placeholder="Select a Parameter",
            style={'height': '30px', 'width': '250px'}
            #value=parameters[0]['value']
        ),
        html.P()
    ]),
    #html.Label('Select Date Range:'),
    dcc.DatePickerRange(
        id='date-range',
        min_date_allowed=dt.datetime(2018, 9, 11),
        max_date_allowed=dt.datetime(2018, 9, 22),
        initial_visible_month=dt.datetime(2018, 9, 11),
        display_format='MMM Do, YYYY',
        #start_date=dt.datetime(2018, 9, 11),
        #end_date=dt.datetime(2018, 9, 22)
    ),
    dcc.Graph(
        id='plot',
        figure=go.Figure(
            layout=go.Layout(
                margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                legend={'x': 0, 'y': 1},
                hovermode='closest'
            )
        )
    )
])


@app.callback(
    Output('plot', 'figure'),
    [Input('device-dropdown', 'value'),
     Input('parameter-dropdown', 'value'),
     Input('date-range', 'start_date'),
     Input('date-range', 'end_date')])
def update_output(device, parameter, start_date, end_date):

    if device is not None and parameter is not None:

        df_for_analysis = df_coffee_farm[df_coffee_farm.dev_id==device]

        if start_date is not None and end_date is not None:
            start_date = dt.datetime.strptime(start_date, '%Y-%m-%d')
            end_date = dt.datetime.strptime(end_date, '%Y-%m-%d')
            filtered_df = df_for_analysis[(df_for_analysis['time'].dt.date>=start_date.date()) &
                                      (df_for_analysis['time'].dt.date<=end_date.date())]
            traces = [go.Scatter(
                x=filtered_df['time'],
                y=filtered_df[parameter],
                mode='markers',
                opacity=0.7,
                marker={
                    'size': 15,
                    'line': {'width': 0.5, 'color': 'white'}
                }
            )]

            return {
                'data': traces,
                'layout': go.Layout(
                    xaxis={'title': 'Time'},
                    yaxis={'title': parameter,
                           'range': parameter_ranges[parameter_labels.index(parameter)]},
                    margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                    legend={'x': 0, 'y': 1},
                    hovermode='closest'
                )
            }




if __name__ == '__main__':
    app.run_server(debug=True)
