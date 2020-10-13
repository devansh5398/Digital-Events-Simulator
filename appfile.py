import dash
import dash_bootstrap_components as dbc
import pandas as pd

df = pd.DataFrame()

def get_df():
    return df

def set_df(df_to_copy):
    global df
    df = pd.DataFrame(None)
    df = df_to_copy.copy()

app = dash.Dash(__name__, external_stylesheets = [dbc.themes.BOOTSTRAP])
# server = app.server
app.config.suppress_callback_exceptions = True
