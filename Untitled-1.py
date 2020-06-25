

app.layout = html.Div([
    html.Div([
        html.Button("Start calculation",n_clicks=0,id="btn")
        html.Label('Calculation 1 complete', style={'display':"none"}, id='cal1'),
        html.Label('Calculation 2 complete', style={'display':"none"}, id='cal1'),
        html.Label('Calculation 3 complete', style={'display':"none"}, id='cal1'),
])
])


@app.callback(
    [Output('cal1', 'style'),
    Output('cal2', 'style'),
    Output('cal3', 'style')],
    [Input('btn', 'n_clicks')])
def calculation():
    # long calulation 1
    #> make label id cal1 visible

    # long calulation 2
    #> make label id cal2 visible

    # long calulation 3
    #> make label id cal3 visible

    # calculation complete