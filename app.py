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
        with open(file) as f: 
            self.info = json.load(f)
        self.dfs =[pd.read_pickle('data/'+ii['id']) for ii in self.info]
    # def updateInfo(self,job,host,loc):
    #     self.info.append({
    #         "name":job,
    #         "host":host,
    #         "location":loc
    #     })
    #     with open('info.json','w') as f:
    #         json.dump(self.info,f,indent=4)

updateInterVal = .5 # min
data = dataManager() 
data.refreshData()
server = flask.Flask('app')
app = dash.Dash('app', server=server, external_stylesheets=['./assets/style.css'])
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
    ], style={"flex":1, "overflow-y": "auto","padding-bottom":"13px"}),
    # html.Div([
    #     html.Div([
    #         html.Label("Add New Jobs", className="titiletxt"),
    #         html.Button("x", id="clsBtn", n_clicks=0)
    #     ],className="title"),
    #     html.Div([
    #         dcc.Input(type="text", id="jName", placeholder="Job Name"),
    #         dcc.Input(type="text", id="host", placeholder="Host"),
    #         dcc.Input(type="text", id="location", placeholder="Location"),
    #         html.Button("Submit", id="submit", n_clicks=0)
    #     ],id="inputBox")
    # ],id='addjob'),
    # html.Button("+", id='addJobBtn',n_clicks=0),
    html.Label('dummy', id='dummy', style={"display":"none"}),
    dcc.Interval(id='trigger', interval=1000*60*updateInterVal)
],className='mainDiv')




# @app.callback(
#     [Output('addjob', 'style'),Output('addJobBtn',"style")],
#     [Input('addJobBtn', 'n_clicks'),Input('clsBtn', 'n_clicks')],
#     [State('addjob', 'style')]
#     ,prevent_initial_call=True)
# def dialog(val,val2, style):
#     if style and style['opacity']=="1":
#         return [{
#             "max-height" : "0%",
#             "opacity" : '0'
#         },{"transform":"rotate(0deg)"}]
#     else:
#         return [{
#             "max-height" : "40%",
#             "opacity" : '1'
#         },{"transform":"rotate(45deg)"}]


# @app.callback(
#     [Output('dummy', 'children')],
#     [Input('submit', 'n_clicks')],
#     [State('jName', 'value'),State('host', 'value'),State('location', 'value')]
#     ,prevent_initial_call=True)
# def dialog(val,job,host, loc):  # WIP
#     print(job,host,loc)
#     return ["dum"]







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


@app.callback(
    [Output('jobList', 'children'),Output('lastUpdateStamp','children')],
    [Input('fulRefBut', 'n_clicks'),Input('trigger', 'n_intervals')])
def generatePage(val,*args):
    if(val!=0): # no request during page build
        try:
            print('Hi there')
            client = DataRequest()
            client.updateData()
            data.refreshData()
        except Exception as e:
            print("Something went wrong",e)
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




def getThisJobChild(index): # generates children for this particular job
    tInfo = data.info[index]
    df = data.dfs[index]
    return [
            html.Table([
                html.Tr([
                    html.Td('Job Name'),
                    html.Td(tInfo["name"])
                ]),
                html.Tr([
                    html.Td("Running On"),
                    html.Td(tInfo["HostName"],title=tInfo["location"])
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
                        # animate=True,
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
                        # animate=True,
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
                        # animate=True,
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