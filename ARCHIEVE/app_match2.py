import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, MATCH, ALL

app = dash.Dash(__name__, suppress_callback_exceptions=True)






data = [
    {
        'name' : 1,
        'time' : 3
    },
    {
        'name' : 2,
        'time' : 22
    },
    {
        'name' : 33,
        'time' : 99
    }
]



app.layout = html.Div(
    [
        html.Div([


            html.Label('name\t\t\t'),
            html.Label(
                i['name'],
                id={
                    'type':'dynamic_label_name',
                    'index':j
                }
            ),
            html.Button(
                'Update Name',
                id={
                    'type':'dynamic_button_name',
                    'index':j
                },
                n_clicks=0
            ),
            html.Label('time\t\t\t'),
            html.Label(
                i['time'],
                id={
                    'type':'dynamic_label_time',
                    'index':j
                }
            ),
            html.Button(
                'Update Time',
                id={
                    'type':'dynamic_button_time',
                    'index':j
                },
                n_clicks=0
            )
        ]) 
    for j,i in enumerate(data)
    ]
)



@app.callback(
    Output({'type': 'dynamic_label_name', 'index': MATCH}, 'children'),
    [Input({'type': 'dynamic_button_name', 'index': MATCH}, 'n_clicks')],
    [State({'type': 'dynamic_button_name', 'index': MATCH}, 'id')],
)
def display_output(value, id):
    ind = id['index']
    data[ind]['name'] +=1
    return data[ind]['name']





@app.callback(
    Output({'type': 'dynamic_label_time', 'index': MATCH}, 'children'),
    [Input({'type': 'dynamic_button_time', 'index': MATCH}, 'n_clicks')],
    [State({'type': 'dynamic_button_time', 'index': MATCH}, 'id')],
)
def display_output(value, id):
    ind = id['index']
    data[ind]['time'] +=1
    return data[ind]['time']






if __name__ == '__main__':
    app.run_server(debug=True)