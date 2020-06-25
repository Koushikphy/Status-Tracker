import pandas as pd 
import datetime
import json



def getDT():
    return datetime.today().strftime('%H:%M:%S %b %d ')


class dataManager(object):
    def __init__(self,file='init.json'):
        with open(file) as f:
            self.info = json.load(f)
    


    def updateThisJob(self,index):
        self.info[index]["lastUpdated"] = getDT()

    
    def updateThisChunk(self,index,chunk):
        self.info[index]["chunk"] = chunk

    def refreshData(self,index):
    


    def addNewJob(self,details):
        