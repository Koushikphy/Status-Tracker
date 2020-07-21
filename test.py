import time
import dash
import dash_core_components as dcc
import dash_html_components as html

from dash.dependencies import Input, Output

app = dash.Dash(__name__, prevent_initial_callbacks=True)
app.layout = html.Div(
    [
        html.Div(" Hi There", id='progress'),
        dcc.Interval(id='trigger', interval=3000),
    ]
)


@app.callback(Output('progress', 'children'), [Input('trigger', 'n_intervals')])
def update_progress(val):
    return str(val)+" iteration passed"


if __name__ == '__main__':
    app.run_server(debug=True)