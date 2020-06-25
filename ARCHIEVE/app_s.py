data = [
    {
        'name':'a',
        'host':'b',
        'status':'c'
        'x':[0,1,2,3],
        'y':[6,7,8,9]
    }
]


app.layout = html.Div(
    [
        html.Div([
                html.Div(
                    [
                        html.Label( dat['name']),
                        html.Label(dat['host']),
                        html.Label(dat['status']),
                        html.Button('Refresh')
                    ]
                ),
                html.Div([
                        dcc.Graph(
                            className= 'dashPlot',
                            figure={
                                'data': [{
                                        'x': dat['x'],
                                        'y': dat['y'],
                                        'mode': 'lines',
                                        'line':{"width":1.5}
                                }]
                            }
                        )
                    ],
                    className="myPlot",
                    style= {'display': 'block'}
                )
        ]) for dat in data
    ]
)

