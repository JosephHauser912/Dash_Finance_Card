import dash
from dash import dcc, html, Input, Output 
import dash_bootstrap_components as dbc    # pip install dash-bootstrap-components
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from alpha_vantage.timeseries import TimeSeries # pip install alpha-vantage
import requests

# -------------------------------------------------------------------------------
# Set up initial key and financial category

# key = 'IDF8NFXCWRVB6P8C' # Use your own API Key or support my channel if you're using mine :)
#  # https://github.com/RomelTorres/alpha_vantage
#  # Chose your output format or default to JSON (python dict)
# ts = TimeSeries(key, output_format='pandas') # 'pandas' or 'json' or 'csv'
# ms_data, ms_meta_data = ts.get_intraday(symbol='MSFT',interval='60min', outputsize='full')
# df = ms_data.copy()
# df=df.transpose()
# df.rename(index={"1. open":"open", "2. high":"high", "3. low":"low",
#                  "4. close":"close","5. volume":"volume"},inplace=True)
# df=df.reset_index().rename(columns={'index': 'indicator'})
# df = pd.melt(df,id_vars=['indicator'],var_name='date',value_name='rate')
# df = df[df['indicator']!='volume']

# df.to_csv("ms_fin_data2.csv", index=False)
# exit()

# # # Read the data we already downloaded from the API
dff = pd.read_csv("ms_fin_data.csv")
dff = dff[dff.indicator.isin(['high'])]
print(dff.head(10))


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP],meta_tags=[{"name":'viewport', 'content': 'width-device=width, initial-scale=1.0'}])

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            dbc.Card(
                [
                    dbc.CardImg(
                        src='/assets/msft.png',
                        top=True,
                        style={"width": "6rem"},
                    ),

                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.P("Change (1D)")
                            ]),

                            dbc.Col([
                                dcc.Graph(id='indicator-graph', figure={},
                                config={'displayModeBar':False})
                            ])
                        ]),
                        dbc.Row([
                            dbc.Col([
                                html.P("Next Col"),
                                dcc.Graph(id='daily-line', figure = {},
                                config={'displayModeBar':False})
                            ])
                        ]),
                        dbc.Row([
                            dbc.Col([
                                dbc.Button("SELL")
                            ]),
                            dbc.Col([
                                dbc.Button("BUY")
                            ])
                        ]),
                        dbc.Row([
                            dbc.Col([
                                dbc.Label(id='low-price', children='375.02'),
                            ]),
                            dbc.Col([
                                dbc.Label(id='high-price', children = '375.06')
                            ])
                        ])
                    ])
                ],
                style={'width':'24rem'},
                className='mt-3'
            )
        ], width=6)
    ], justify='center'),

    dcc.Interval(id='update', n_intervals=0, interval=1000*5)
])

# Indicator Graph
@app.callback(
    Output('indicator-graph', 'figure'),
    Input('update', 'n_intervals')
)
def update_graph(timer):
    dff_rv = dff.iloc[::-1]
    day_start = dff_rv[dff_rv['date'] == dff_rv['date'].min()]['rate'].values[0]
    day_end = dff_rv[dff_rv['date'] == dff_rv['date'].max()]['rate'].values[0]
    print(day_start, day_end)

    fig = go.Figure(go.Indicator(
        mode ="delta",
        value = day_end,
        delta = {'reference':day_start, 'relative':True, 'valueformat': '.2%'}
    ))
    fig.update_traces(delta_font={'size':12})
    fig.update_layout(height=30, width=70)

    if day_end >= day_start:
        fig.update_traces(delta_increasing_color='green')
    elif day_start >= day_end:
        fig.update_traces(delta_increasing_color='red')
    print(f"the day start value is {day_start}")
    print(f"the day end value is {day_end}")

    return fig


def update_graph(timer):
    dff_rv = dff.iloc[::-1]
    day_start = dff_rv[dff_rv['date'] == dff_rv['date'].min()]['rate'].values[0]
    day_end = dff_rv[dff_rv['date'] == dff_rv['date'].max()]['rate'].values[0]

    fig = go.Figure(go.Indicator(
        mode="delta",
        value=day_end,
        delta={'reference': day_start, 'relative': True, 'valueformat':'.2%'}))
    fig.update_traces(delta_font={'size':12})
    fig.update_layout(height=30, width=70)

    if day_end >= day_start:
        fig.update_traces(delta_increasing_color='green')
    elif day_end < day_start:
        fig.update_traces(delta_decreasing_color='red')

    return fig


# Line Graph---------------------------------------------------------------
@app.callback(
    Output('daily-line', 'figure'),
    Input('update', 'n_intervals')
)
def update_graph(timer):
    dff_rv = dff.iloc[::-1]
    fig = px.line(dff_rv, x='date', y='rate',
                   range_y=[dff_rv['rate'].min(), dff_rv['rate'].max()],
                   height=120).update_layout(margin=dict(t=0, r=0, l=0, b=20),
                                             paper_bgcolor='rgba(0,0,0,0)',
                                             plot_bgcolor='rgba(0,0,0,0)',
                                             yaxis=dict(
                                             title=None,
                                             showgrid=False,
                                             showticklabels=False
                                             ),
                                             xaxis=dict(
                                             title=None,
                                             showgrid=False,
                                             showticklabels=False
                                             ))

    day_start = dff_rv[dff_rv['date'] == dff_rv['date'].min()]['rate'].values[0]
    day_end = dff_rv[dff_rv['date'] == dff_rv['date'].max()]['rate'].values[0]

    if day_end >= day_start:
        return fig.update_traces(fill='tozeroy',line={'color':'green'})
    elif day_end < day_start:
        return fig.update_traces(fill='tozeroy',
                             line={'color': 'red'})

if __name__=='__main__':
    app.run_server(debug=True, port=3000)

#  # https://youtu.be/iOkMaeU8dqE