import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, State, Output
import plotly.graph_objs as go
import pandas as pd
import math
import io
import random
import datetime as dt
# import time
import urllib.parse

import appfile
from appfile import app

# import app as appfile
# from app import app

#%%
# app = dash.Dash(__name__, external_stylesheets =[dbc.themes.BOOTSTRAP])
# app.config.suppress_callback_exceptions = True

#%%
# df = pd.read_csv('data_small - Copy.csv', names=['Transaction', 'Frequency'])
# df['Transaction'] = df['Transaction'].str.split(" ")
df = appfile.get_df()
te_df = pd.DataFrame()

#%%
parameters = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    dbc.FormGroup(
                        [
                            dbc.Label("Generation Type", className="font-weight-bold"),
                            dbc.RadioItems(
                                options=[
                                    {"label": "Random", "value": "random"},
                                    {"label": "Sequential", "value": "sequential"},
                                ],
                                value="random",
                                id="gen_type",
                            )
                        ],
                        className="m-0"
                    ),
                    className="col-md-3 col-10 alert alert-success my-md-0"
                ),
                dbc.Col(
                    dbc.FormGroup(
                        [
                            dbc.Label("Time Slab", className="font-weight-bold"),
                            dbc.Input(id="time_slab", type="number", placeholder="Time Slab")
                        ],
                        className="m-0"
                    ),
                    id="time_slab_col",
                    className="col-md-3 col-10 alert alert-secondary my-md-0"
                ),
                dbc.Col(
                    dbc.FormGroup(
                        [
                            dbc.Label("Total Events", className="font-weight-bold"),
                            dbc.Input(id="tot_events", type="number", placeholder="Total Events")
                        ],
                        className="m-0"
                    ),
                    className="col-md-3 col-10 alert alert-primary my-md-0"
                ),
                dbc.Col(
                    dbc.FormGroup(
                        [
                            dbc.Button("Generate Data", id="gen_data", color="danger", className='mb-3 col-12'),
                            dbc.Button(
                                html.A(
                                    "Export Events",
                                    id="export_data",
                                    href="none",
                                    download="simulated_events.csv",
                                    target="_blank",
                                    style={'color':'white', 'text-decoration':'none'}
                                ),
                                color="danger", 
                                className='col-12'
                            )
                        ],
                        className="m-0"
                    ),
                    className="col-md-2 col-10"
                )
            ],
            justify='around',
            align='center'
        ),
    ],
    className="alert alert-warning my-4 py-4"
)

#%%
table_graph = dbc.Row(
    id = "output_data",
    justify = 'around',
    align = 'center',
    className = 'm-0'
)

#%%
# bar_graph = dbc.Row(dbc.Col(id="bar_plot", width=10), justify='center', className='my-4 mx-0')

#%%
# app.
layout = html.Div([parameters, table_graph])

#%%
@app.callback(
    [Output('time_slab', 'disabled'), Output('time_slab', 'style'), Output('time_slab_col', 'style')],
    [Input('gen_type', 'value')]
)
def toggle_time_slab_disabling(gen_type):
    if gen_type == "random":
        return [False, {}, {}]
    elif gen_type == "sequential":
        return [True, 
                {'background': 'rgba(0, 0, 0, 0.08)', 'border': 'none'}, 
                {'background': 'rgba(0, 0, 0, 0.45)'}]

#%%
@app.callback(
    Output('output_data', 'children'),
    [Input('gen_data', 'n_clicks')],
    [State('gen_type', 'value'), State('time_slab', 'value'), State('tot_events', 'value')]
)
def print_te_table(btn_clk, gen_type, time_slab, tot_events):
    global df
    global te_df
    
    if btn_clk == None or gen_type == None or tot_events == None:
        return []
    if gen_type == "random" and time_slab == None:
        return []

    all_transactions = []
    min_time_slab_req = 0
    
    df = appfile.get_df()
    for index, row in df.iterrows():
        min_time_slab_req = max(min_time_slab_req, len(row['Transaction']))
        for no_of_times in range(row['Frequency']):
            all_transactions.append(row['Transaction'])
            
    if gen_type == "random" and time_slab < min_time_slab_req:
        return dbc.Col(
            dbc.Alert(
                'Invalid Time Slab value. It should be greater than or equal to number of events in each transaction.',
                className='alert-dark font-weight-bold mb-0 text-center'
            ),
            className="col-sm-8 col-10 mb-lg-0 mb-4"
        )
    
    time_val = dt.datetime.now().replace(microsecond = 0)
    
    timestamps = []
    events = []
    slab_intervals = []
    
    if gen_type == "random":
        curr_time = time_val
        
        while tot_events > 0:
            random.shuffle(all_transactions)
            for transaction in all_transactions:
                events_covered = 0
                random_sec = random.sample(range(time_slab), time_slab)
                for event in transaction:
                    timestamps.append(curr_time + dt.timedelta(seconds=random_sec[-1]))
                    events.append(event)
                    random_sec.pop()
                    
                    events_covered += 1
                    tot_events -= 1
                    if tot_events <= 0:
                        break
                    
                slab_intervals.append([curr_time, curr_time + dt.timedelta(seconds=time_slab-1)])
                curr_time = curr_time + dt.timedelta(seconds=time_slab)
                if tot_events <= 0:
                    break
                
    elif gen_type == "sequential":
        curr_time = time_val
        
        while tot_events > 0:
            for transaction in all_transactions:
                events_covered = 0
                
                for event in transaction:
                    timestamps.append(curr_time + dt.timedelta(seconds=events_covered))
                    events.append(event)
                    
                    events_covered += 1
                    tot_events -= 1
                    if tot_events <= 0:
                        break
                
                slab_intervals.append([curr_time, curr_time + dt.timedelta(seconds=events_covered-1)])
                curr_time = curr_time + dt.timedelta(seconds=events_covered)
                if tot_events <= 0:
                    break
        
    te_df = pd.DataFrame(None)
    te_df['Timestamp'] = timestamps
    te_df['Event'] = events
    te_df.sort_values('Timestamp', inplace=True)
    
    if slab_intervals:
        slab_intervals[-1][1] = te_df['Timestamp'].iloc[-1]
    
    formed_table = dash_table.DataTable(
        data = te_df.to_dict('records'),
        columns = [{'id': c, 'name': c} for c in te_df.columns],
        style_cell_conditional=[
            {'if': {'column_id': 'Timestamp'},
              'width': '65%'}
        ],
        style_data_conditional=[
            {'if': {'row_index': 'odd'},
             'backgroundColor': 'rgb(248, 248, 248)'}
        ],
        style_header={
            'backgroundColor': 'rgb(230, 230, 230)',
            'fontWeight': 'bold',
            # 'textAlign': 'center'
        }
    )
    
    traces = []
    for unique_event in te_df['Event'].unique():
        df_cat = te_df[te_df['Event'] == unique_event]
        traces.append(
            go.Bar(
                x=df_cat['Timestamp'],
                y=[1] * df_cat.shape[0],
                name=unique_event,
                hoverinfo = "x",
                width=400
            )
        )
    
    for i in range(len(slab_intervals)):
        if i % 2 == 0:
            color = 'rgb(255,200,255)'
        else:
            color = 'rgb(200,255,200)'
        traces.append(
            go.Scatter(
                x = [slab_intervals[i][0], slab_intervals[i][0], slab_intervals[i][1], slab_intervals[i][1]],
                y = [0, 1, 1, 0],
                fill = 'toself',
                fillcolor = color,
                line_color = color,
                # mode = "lines",
                showlegend = False,
                hoverinfo = "x",
                opacity = 0.5
            )
        )

    formed_graph = dcc.Graph(
        figure = {
            'data': traces,
            'layout':
                go.Layout(
                    xaxis={'title': '<b>Timeline</b>'},
                    yaxis={'title': '<b>Events</b>',
                           'showticklabels': False,
                           },
                    paper_bgcolor='#fafafa',
                    plot_bgcolor='#f6f6f6',
                    margin={'l':50, 'r':50, 't':50, 'b':50},
                    height=300
                )
        }
    )
    
    return [
        dbc.Col(
            formed_table, 
            className="col-lg-3 col-8 mb-lg-0 mb-4", 
            style={"max-height":"58vh", "overflowY":"auto"}
        ),
        dbc.Col(
            formed_graph, 
            className="col-lg-8 col-10 mb-lg-0 mb-4 p-0",
            style={"max-height":"58vh", "overflowY":"auto"}
        )
    ]

#%%
@app.callback(
    Output('export_data', 'href'),
    [Input('gen_data', 'n_clicks')]
)
def update_download_link(btn_clk):
    csv_string = te_df.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    name = "simulated_events.csv"
    return csv_string

#%%
# if __name__ == '__main__':
#     app.run_server()