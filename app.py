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



class dataManager():
    # info.json has to be updated by the client before this can use the file
    def __init__(self,file='info.json'):
        self.refreshData(file)

    def updateThisChunk(self,index,chunk):
        self.info[index]["chunk"] = chunk

    def refreshData(self,file):
        with open(file) as f: self.info = json.load(f)
        self.dfs =[pd.read_pickle(ii['id']) for ii in self.info]


    def getData(self,index):
        df = self.dfs[index]
        xx = df['step']
        yy = df[self.info[index]['chunk']]
        return xx,yy




client = DataRequest() # reads and updates info.json and relavant data
client.updateData()

data = dataManager() # reads the file to use for the ui
# probably i should merge the two classes


server = flask.Flask('app')
app = dash.Dash('app', server=server)
app.title = 'Status Tracker'
app.scripts.config.serve_locally = False



def getDT():
    return datetime.today().strftime('%H:%M:%S %b %d ')



app.layout = html.Div([
    html.Div([
        html.Label('Status Tracker',style={'padding-top':"9px"}),
        html.Div([
            html.Label("Last Refreshed on : "),
            html.Label(getDT(),id='lastUpdateStamp'),
            html.Button(className="btn",n_clicks=0,id="fulRefBut")
        ],className="lastRef")
    ],className="header"),
    html.Div(id='jobList', children=[], style={"flex":1, "overflow-y": "auto"}),
],className='mainDiv')



@app.callback(
    [Output('jobList', 'children'),Output('lastUpdateStamp','children')],
    [Input('fulRefBut', 'n_clicks')])
def generatePage(val):
    # also refresh the data
    client.updateData()
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



@app.callback(
    [Output({'type': 'jobPlot', 'index': MATCH}, 'figure'),
    Output({'type': 'selecter', 'index': MATCH}, 'children')],
    [Input({'type': 'chunkSelector', 'index': MATCH, "chunk":ALL}, 'n_clicks')],
    [State({'type': 'chunkSelector', 'index': MATCH, "chunk":ALL}, 'id')],
    prevent_initial_call=True
)
def updateThisJobChunk(val, id):
    ind = id[0]['index']

    # as this label update resets the clicks so the 
    # n clicks will always be 1  for currently clicked button
    if(val[0]):
        ch= 'norm'
    elif(val[1]):
        ch="energy"
    elif(val[2]):
        ch="timeDelay"
    else:
        print("something went wrong")
    data.updateThisChunk(ind, ch)
    figure= getFigureData(ind)
    labelChildren = createLabelChildren(ind)
    return figure, labelChildren






def getFigureData(ind):
    xx,yy = data.getData(ind)

    minx, maxx = xx.min(), xx.max()
    miny, maxy = yy.min(), yy.max()
    return {
            "data":[{
                "x" : xx,
                "y" : yy
            }],
            "layout":{
                "margin":{
                    "t":10,"r":0,'l':20,"b":20
                },
                "autorange" : False,
                "xaxis":{
                    "range":[ minx, maxx] # give a slight padding
                },
                "yaxis":{
                    "range":[miny*.9,maxy*1.1]
                },
                "showlegend": False,
            }
        }




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
    xx,yy = data.getData(index)
    return [
            html.Table([
                html.Tr([
                    html.Td('Job Name'),
                    html.Td(tInfo["name"],className="longCell")
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
                    html.Td("Average Time"),
                    html.Td(tInfo["avgTime"])
                ]),
                html.Tr([
                    html.Td("ETA"),
                    html.Td(tInfo["eta"])
                ]),
            ],className="jobDescription"),
            html.Div([
                html.Div(
                    createLabelChildren(index),
                    id={
                        "type": "selecter",
                        "index" : index
                    },
                className='selectBar'),
                dcc.Graph(
                    animate=True,
                    className="myPlot",
                    id={
                        "type" : 'jobPlot',
                        "index" : index
                    },
                    figure={
                        "data":[{
                            "x" : xx,
                            "y" : yy
                        }],
                        "layout":{
                            "margin":{
                                "t":10,"r":0,'l':20,"b":20
                            },
                            "autorange" : True,
                            "showlegend": False,
                        }
                    }
                )
            ],className="jobPlots")
        ]



def createLabelChildren(index):
    tInfo = data.info[index]
    return [
            html.Label(
                'Norm',
                n_clicks=0,
                className='focused' if tInfo['chunk']=='norm' else '',
                id={
                    'type':'chunkSelector',
                    'index':index,
                    "chunk":'norm'
                }
            ),
            html.Label(
                "Energy",
                n_clicks=0,
                className="midSelect "+('focused' if tInfo['chunk']=='energy' else ''),
                id={
                    'type':'chunkSelector',
                    'index':index,
                    "chunk":'ener'
                }
            ),
            html.Label(
                "TimeDelay", 
                n_clicks=0,
                className='focused' if tInfo['chunk']=='timeDelay' else '',
                id={
                    'type':'chunkSelector',
                    'index':index,
                    "chunk":'time'
                }
            )
        ]




if __name__ == '__main__':
    app.run_server(debug=True)
    # app.run_server(debug='True',port=8080,host='0.0.0.0')