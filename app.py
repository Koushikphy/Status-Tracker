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
# 1. use way to read the total time step


class dataManager():
    # info.json has to be updated by the client before this can use the file
    def __init__(self):
        pass

    def updateThisChunk(self,index,chunk):
        self.info[index]["chunk"] = chunk

    def refreshData(self,file='info.json'):
        with open(file) as f: self.info = json.load(f)
        self.dfs =[pd.read_pickle(ii['id']) for ii in self.info]


    def getData(self,index):
        df = self.dfs[index]
        xx = df['step']
        yy1 = df["norm"]
        yy2 = df["energy"]
        yy3 = df["timeDelay"]
        # also calculate ranges
        minx, maxx = xx.min(), xx.max()
        rxx = [ minx, maxx]

        miny, maxy = yy1.min(), yy1.max()
        ryy1 = [miny*.9,maxy*1.1]

        miny, maxy = yy2.min(), yy2.max()
        ryy2 = [miny*.9,maxy*1.1]

        miny, maxy = yy3.min(), yy3[10:].max()
        ryy3 = [miny*.99,maxy*1.01]
        return xx,yy1,yy2,yy3, rxx, ryy1,ryy2,ryy3


# client = DataRequest() # reads and updates info.json and relavant data

data = dataManager() # reads the file to use for the ui
# probably i should merge the two classes


server = flask.Flask('app')
app = dash.Dash('app', server=server,external_stylesheets=['./assets/style.css'])
app.title = 'Status Tracker'
app.scripts.config.serve_locally = False


config={
    "displaylogo":False,
    "responsive": True,
    "modeBarButtonsToRemove" : ["toImage","sendDataToCloud"],
}


def getDT():
    return datetime.today().strftime('%H:%M:%S %b %d ')



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
    return [[ getThisJob(index) for index in range(len(data.info)) ],getDT()]




# @app.callback(
#     Output({'type': 'thisJob', 'index': MATCH}, 'children'),
#     [Input({'type': 'refButton', 'index': MATCH}, 'n_clicks')],
#     [State({'type': 'refButton', 'index': MATCH}, 'id')],
#     prevent_initial_call=True
#     )
# def updateThisJob(val, id):
#     print('ref update')
#     ind = id['index']
#     updateThisJobInfo(ind)
#     print (dash.callback_context.triggered)
#     return getThisJobChild(ind)




def getThisJob(index):
    return html.Div(
        getThisJobChild(index),
        className="job",
        id={
            'type':'thisJob',
            'index':index
        }
    )


def getThisJobChild(index):   # generates children for this particular job
    tInfo = data.info[index]
    xx,yy1,yy2,yy3, rxx, ryy1,ryy2,ryy3 = data.getData(index)
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
                        # html.Button(  # hide individual refresh button for now
                        #     className="btn",
                        #     n_clicks=0,
                        #     id={
                        #         'type':'refButton',
                        #         'index':index
                        #     }
                        # )
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
                                    'x': xx, 
                                    'y': yy1
                                }
                            ],
                            "layout":{
                                "margin":{
                                    "t":10,"r":0,'l':20,"b":19
                                },
                                "autorange" : False,
                                "hovermode":"closest",
                                "xaxis":{
                                    "range":rxx 
                                },
                                "yaxis":{
                                    "range":ryy1
                                },
                                "showlegend": False,
                            }
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
                                    'x': xx, 
                                    'y': yy2
                                }
                            ],
                            "layout":{
                                "margin":{
                                    "t":10,"r":0,'l':20,"b":19
                                },
                                "autorange" : False,
                                "hovermode":"closest",
                                "xaxis":{
                                    "range":rxx 
                                },
                                "yaxis":{
                                    "range":ryy2
                                },
                                "showlegend": False,
                            }
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
                                    'x': xx, 
                                    'y': yy3,
                                }
                            ],
                            "layout":{
                                "margin":{
                                    "t":10,"r":0,'l':20,"b":19
                                },
                                "autorange" : False,
                                "hovermode":"closest",
                                "xaxis":{
                                    "range":rxx 
                                },
                                "yaxis":{
                                    "range":ryy3
                                },
                                "showlegend": False,
                            }
                        },
                        config = config
                    )
                ]),
            ],parent_className="jobPlots")
        ]

if __name__ == '__main__':
    app.run_server(debug=True)
    # app.run_server(debug='True',port=8080,host='0.0.0.0')