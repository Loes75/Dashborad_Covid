import dash


app = dash.Dash(__name__,assets_folder = 'assets',)
app.config.suppress_callback_exceptions = True

server = app.server
