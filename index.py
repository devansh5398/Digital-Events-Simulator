# !pip install jupyter-dash
# !pip install dash
# !pip install dash-bootstrap-components
# !pip install dash_core_components
# !pip install dash_html_components
# !pip install dash_table
# !pip install dash_bio
# !pip install plotly

#%%
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, State, Output
import plotly.express as px
import plotly.graph_objs as go
import base64
import pandas as pd
import time
import base64
import io

from pages import page1, page2
import appfile
from appfile import app

# import app as appfile
# from app import app

#%%
store_page1 = dcc.Store(id='page1_store', data=[page1.layout])
store_page2 = dcc.Store(id='page2_store', data=[page2.layout])

#%%
navbar = dbc.NavbarSimple(
    [
        dbc.NavItem(dbc.NavLink("Co-occurance frequency page", id="page1_link", href='#')),
        dbc.NavItem(dbc.NavLink("Data Generation", id="page2_link", href='#')),
    ],
    brand="Digital Simulator",
    brand_href="#",
    color="dark",
    dark=True,
    sticky="top"
)

#%%
page_content = html.Div(id="content")

#%%
server = app.server
app.layout = html.Div([store_page1, store_page2, navbar, page_content])

#%%
@app.callback(
    [Output('content', 'children')] +
    [Output(f'page{i}_store', 'data') for i in range(1,3)] +
    [Output(f'page{i}_link', 'active') for i in range(1,3)],
    
    [Input(f'page{i}_link', 'n_clicks') for i in range(1,3)],
    
    [State('content', 'children')] +
    [State(f'page{i}_store', 'data') for i in range(1,3)] +
    [State(f'page{i}_link', 'active') for i in range(1,3)]
)
def print_page_content(btn1_clk, btn2_clk, content, page1_data, page2_data, btn1_act, btn2_act):
    ctx = dash.callback_context
    if ctx.triggered:
        btn_id = ctx.triggered[0]['prop_id'].split('.')[0]
    else:
        btn_id = None
        
    if btn_id == 'page2_link':
        if btn2_act == True:
            return [dash.no_update for i in range(5)]
        return [page2_data[0], [content], dash.no_update, False, True]
    
    elif btn_id == 'page1_link':
        if btn1_act == True:
            return [dash.no_update for i in range(5)]
        return [page1_data[0], dash.no_update, [content], True, False]
        
    return [page1_data[0], dash.no_update, dash.no_update, True, False]

#%%
# import threading
# def printit():
#     threading.Timer(5.0, printit).start()
#     print(appfile.get_df())

# printit()

#%%
if __name__ == '__main__':
    app.run_server()