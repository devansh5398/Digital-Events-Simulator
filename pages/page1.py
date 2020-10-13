import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, State, Output
import plotly.graph_objs as go
import base64
import pandas as pd
import io
import pydotplus as pdp
import os
os.environ["PATH"] += os.pathsep + "C:/Users/arihant/Anaconda3/Library/bin/graphviz"

import appfile
from appfile import app

# import app as appfile
# from app import app
#%%
# app = dash.Dash(__name__, external_stylesheets =[dbc.themes.BOOTSTRAP])
# app.config.suppress_callback_exceptions = True

#%%
input_df = pd.DataFrame()
df = appfile.get_df()

#%%
readfile = dbc.Container(
    [
         dbc.Alert(
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Upload(
                            html.Div(['Load Data by Drag and Drop or Selecting Files']),
                            id='load_data',
                            style={'height': '60px', 'lineHeight': '60px', 'border': '1px dashed black', 'borderRadius': '5px'}
                        ),
                        className = "col-8 font-weight-bold"
                    ),
                    dbc.Col(dbc.Button("Get FP Tree", id="submit_data", color="danger"), width=2, align='center')
                ],
                justify='center'
            ),
            className = "my-4 alert-warning text-center",
         )
    ],
)

#%%
table_image = dbc.Row(
    [
        dbc.Col(id="table", width=4, style={"max-height":"60vh", "overflowY":"auto"}),
        dbc.Col(dbc.Row(html.Img(id="image", style={'max-height':'60vh'}), justify="center"), width=7, id="image_box")
    ],
    justify = 'center',
    align = 'center',
    className = 'm-0'
)

#%%
bar_graph = dbc.Row(dbc.Col(id="bar_plot", width=10), justify='center', className='my-4 mx-0')

#%%
# app.
layout = html.Div([readfile, table_image, bar_graph])

#%%
# @app.callback(
#     Output('submit_data', 'n_clicks'),
#     [Input('submit_data', 'n_clicks')]
# )
# def reset_submit_clicks(btn_click):
#     return 0

#%%
@app.callback(
    Output('table', 'children'),
    [Input('load_data', 'contents'), Input('submit_data', 'n_clicks')]
)
def print_table(content, btn_click):
    global input_df
    global df
    
    if content is None:
        if btn_click is None:
            return []
        else:
            return dbc.Alert('No data loaded yet.', className='alert-dark font-weight-bold text-center')
    
    filetype, filedata = content.split(',')
    filedata = base64.b64decode(filedata)
    filedata = filedata.decode('utf-8')
    input_df = pd.read_csv(io.StringIO(filedata), names=['Transaction', 'Frequency'])
    
    df = input_df.copy()
    df['Transaction'] = df['Transaction'].str.split(" ")
    appfile.set_df(df)
    
    # return dbc.Table.from_dataframe(input_df, dark=True, striped=True, bordered=True, hover=True, className="m-0 overflow-hidden")
    return dash_table.DataTable(
        data = input_df.to_dict('records'),
        columns = [{'id': c, 'name': c} for c in input_df.columns],
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

#%%
@app.callback(
    Output('load_data', 'children'),
    [Input('load_data', 'filename')]
)
def write_filename_on_select(filename):
    if filename is not None:
        return html.Div([f'{filename} selected or Load new data'])
    return html.Div(['Load Data by Drag and Drop or Selecting Files'])

#%%
# image_filename = 'E:/Jupyter/Dash App/my-image.png'
# encoded_image = base64.b64encode(open(image_filename, 'rb').read())
#     html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()))
@app.callback(
    [Output('image', 'src'), Output('image_box', 'style')],
    [Input('submit_data', 'n_clicks')],
    [State('load_data', 'contents')]
)
def show_image(btn_click, content):
    global df
    
    if btn_click is None or content is None:
        return ["", {"max-height":"60vh", "overflow":"auto", "display":"none"}]
    
    all_trans = []
    for index, row in df.iterrows():
        for no_of_times in range(row['Frequency']):
            all_trans.append(row['Transaction'])
    
    # Creating json
    json_data = [ {'name' : 'root', 'count' : None, 'no_of_children' : 0, 'children' : []} ]
    
    for trans in all_trans:
        par = json_data[0]
        children = json_data[0]['children']
        for item in trans:
            flag = False
            for child in children:
                if child['name'] == item:
                    child['count'] += 1
                    par = child
                    children = child['children']
                    flag = True
                    break
            
            if flag == False:
                par['no_of_children'] += 1
                children.append({'name': item, 'count':1, 'no_of_children':0, 'children':[]})
                par = children[-1]
                children = par['children']
    
    # Creating FP tree image
    tree_fig = pdp.Dot(graph_type='graph')
    node_name = 1
    def formation(tree, parent_name):
        nonlocal node_name
        nonlocal tree_fig
        for node in tree:
            curr_node_name = node_name
            node_name += 1
            
            tree_fig.add_node(pdp.Node(name=curr_node_name, label=f"Name: {node['name']}\nCount: {node['count']}"))
            
            if parent_name != None:
                edge = pdp.Edge(parent_name, curr_node_name)
                tree_fig.add_edge(edge)
                                       
            formation(node['children'], curr_node_name)
            
    formation(json_data, None)
    
    image = tree_fig.create_png()
    encoded_image = base64.b64encode(image)
    
    return ['data:image/png;base64,{}'.format(encoded_image.decode()), {"max-height":"60vh", "overflow":"auto"}]

#%%
@app.callback(
    Output('bar_plot', 'children'),
    [Input('submit_data', 'n_clicks')],
    [State('load_data', 'contents')]
)
def show_bar_plot(btn_click, content):
    global input_df
    
    if btn_click is None or content is None:
        return []
    
    return dcc.Graph(
        figure = {
            'data': [go.Bar(x = input_df['Transaction'], 
                           y = input_df['Frequency'], 
                           marker = {'color':input_df['Frequency'], 'showscale':True}, 
                           hoverinfo = "x+y",
                           text = input_df['Frequency'], 
                           textposition = 'outside'
                    )],
            'layout': go.Layout(
                           title='<b>Transactions vs Frequency Graph</b>',
                           xaxis={'title': '<b>Transactions</b>'},
                           yaxis={'title': '<b>Frequency</b>'},
                           plot_bgcolor='#f8f8f8',
                    )
        }
    )

#%%
# if __name__ == '__main__':
#     app.run_server()