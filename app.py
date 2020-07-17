import dash
from dash.dependencies import Input, Output, State, MATCH, ALL
import dash_core_components as dcc
import dash_html_components as html
import flask
import numpy as np
import pandas as pd
import json
from datetime import datetime
from dataManager import DataRequest


# TODO:
# Handle bad data in fort.21 file


def getDT():
    return datetime.today().strftime('%H:%M:%S %b %d ')


class dataManager():
    def refreshData(self,file='info.json'):
        with open(file) as f: self.info = json.load(f)
        self.dfs =[pd.read_pickle('data'+ii['id']) for ii in self.info]



data = dataManager() 
# client = DataRequest() # reads and updates info.json and relavant data
server = flask.Flask('app')
app = dash.Dash('app', server=server,external_stylesheets=['./assets/style.css'])
app.title = 'Status Tracker'
app.scripts.config.serve_locally = False



app.layout = html.Div([
    html.Div([
        html.Label('Status Tracker',style={'padding-top':"5px"}),
        html.Div([
            html.Label("Last Refreshed on : "),
            html.Label(getDT(),id='lastUpdateStamp'),
            html.Button(className="btn",n_clicks=0,id="fulRefBut")
        ],className="lastRef")
    ],className="header"),
    html.Div(id='jobList', children=[
        html.Label("Updating Database. Please wait....", style={"font-size":"21px"})
    ], style={"flex":1, "overflow-y": "auto"}),
],className='mainDiv')



@app.callback(
    [Output('jobList', 'children'),Output('lastUpdateStamp','children')],
    [Input('fulRefBut', 'n_clicks')])
def generatePage(val):
    # also refresh the data
    # client = DataRequest()
    # client.updateData()
    data.refreshData()
    return [[
        html.Div(
            getThisJobChild(index),
            className="job",
            id={
                'type':'thisJob',
                'index':index
            }
        ) for index in range(len(data.info)) 
    ], getDT()]




config={
    "displaylogo":False,
    "responsive": True,
    "modeBarButtonsToRemove" : ["toImage","sendDataToCloud"],
}

layout = {
    "margin":{
        "t":10,"r":0,'l':20,"b":19
    },
    "autsize" : True,
    "hovermode":"closest",
    "xaxis":{
        "automargin": True,
        "zeroline": False,
        "showline": True,
        "showgrid": True,
    },
    "yaxis":{
        "automargin": True,
        "zeroline": False,
        "showline": True,
        "showgrid": True,
    },
    "showlegend": False,
}



def getThisJobChild(index):   # generates children for this particular job
    tInfo = data.info[index]
    df = data.dfs[index]
    return [
            html.Table([
                html.Tr([
                    html.Td('Job Name'),
                    html.Td(tInfo["name"])
                ]),
                html.Tr([
                    html.Td("Host"),
                    html.Td(tInfo["host"],title=tInfo["location"])
                ]),
                html.Tr([
                    html.Td("Progress"),
                    html.Td(tInfo["currentStep"]+'/'+tInfo["totalStep"])
                ]),
                html.Tr([
                    html.Td("Submitted"),
                    html.Td(tInfo["submitted"])
                ]),
                html.Tr([
                    html.Td("Last Updated"),
                    html.Td([
                        tInfo["lastUpdated"],
                    ])
                ]),
                html.Tr([
                    html.Td("Time Spent"),
                    html.Td(tInfo["timeSpent"])
                ]),
                html.Tr([
                    html.Td("Average Time"),
                    html.Td(tInfo["avgTime"])
                ]),
                html.Tr([
                    html.Td("ETC"),
                    html.Td(tInfo["eta"])
                ]),
            ],className="jobDescription"),
            dcc.Tabs([
                dcc.Tab(label='Norm', children=[
                    dcc.Graph(
                        animate=True,
                        figure={
                            'data': [
                                {
                                    'x': df['step'], 
                                    'y': df["norm"]
                                }
                            ],
                            "layout":layout
                        },
                        config = config
                    )
                ]),
                dcc.Tab(label='Energy', children=[
                    dcc.Graph(
                        animate=True,
                        figure={
                            'data': [
                                {
                                    'x': df['step'], 
                                    'y': df["energy"]
                                }
                            ],
                            "layout":layout
                        },
                        config = config
                    )
                ]),
                dcc.Tab(label='Time Delay', children=[
                    dcc.Graph( 
                        animate=True,
                        figure={
                            'data': [
                                {
                                    'x': df['step'], 
                                    'y': df["timeDelay"],
                                }
                            ],
                            "layout":layout
                        },
                        config = config
                    )
                ]),
            ],parent_className="jobPlots")
        ]

if __name__ == '__main__':
    app.run_server(debug=True)
    # app.run_server(debug='True',port=8080,host='0.0.0.0')