from dash.dependencies import Output, Input, State
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
from flask import Flask
import pandas as pd
import dash

server = Flask(__name__)
app = dash.Dash(server=server, external_stylesheets=[dbc.themes.FLATLY])
app.title = 'Dashboard'

df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminderDataFiveYear.csv')

app.layout = dbc.Container([

    dbc.Row(dbc.Col(html.H2("Your Amazing Dashboard"), width={'size': 12, 'offset': 0, 'order': 0}), style = {'textAlign': 'center', 'paddingBottom': '1%'}),

    dbc.Row(dbc.Col(dcc.Loading(children=[dcc.Graph(id ='your-graph'),
                                          dcc.Slider(id='year-slider',
                                                    min=df['year'].min(),
                                                    max=df['year'].max(),
                                                    value=df['year'].min(),
                                                    marks={str(year): str(year) for year in df['year'].unique()},
                                                    step=None)
                                        ], color = '#000000', type = 'dot', fullscreen=True ) ))
])

@app.callback(
    Output('your-graph', 'figure'),
    Input('year-slider', 'value'))
def update_figure(selected_year):
    filtered_df = df[df.year == selected_year]

    fig = px.scatter(filtered_df, x="gdpPercap", y="lifeExp",
                     size="pop", color="continent", hover_name="country",
                     log_x=True, size_max=55)

    fig.update_layout(transition_duration=500)

    return fig

if __name__=='__main__':
    app.run_server()
