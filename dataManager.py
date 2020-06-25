import pandas as pd 
import json
import paramiko,os
from random import choice
from string import digits
from datetime import datetime, timedelta


class DataRequest():
    def __init__(self):
        # self.jobInfos = []
        self.client = paramiko.SSHClient()
        self.client._policy = paramiko.WarningPolicy()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        self.ssh_config = paramiko.SSHConfig()
        user_config_file = os.path.expanduser("~/.ssh/config")
        if os.path.exists(user_config_file):
            with open(user_config_file) as f:
                self.ssh_config.parse(f)


    def updateData(self):
        info = self.readJson()
        self.jobInfos = []
        for dat in info:
            if 'id' not in dat.keys(): # new added job
                newId = ''.join(choice(digits) for i in range(10))  # generate a 10 digit random string
                dat['name'] = dat['name']
                dat['host'] = dat['host']
                dat['location'] = dat['location']
                dat["id"] = newId
                # dat["currentStep"] = ''  # add those missing keys
                # dat["totalStep"] = ''
                # dat["submitted"] = ""
                # dat["lastUpdated"] =""
                # dat["avgTime"] = ""
                # dat["eta"] = ""
                dat["chunk"] = "norm"
            df = self.requestData(dat['host'],dat['location'],dat["id"])
            # print(df)
            dat["currentStep"] = df["step"].iloc[-1]
            dat["totalStep"] = 10000 # do it somehow else
            dat["submitted"] = df["timeStamp"].iloc[0]#.strftime('%H:%M:%S %b %d ')
            dat["lastUpdated"] = df["timeStamp"].iloc[-1]#.strftime('%H:%M:%S %b %d ')
            dat["avgTime"] = df["timeDelay"].mean()
            timeLeft = (dat["totalStep"] - dat["currentStep"])*dat["avgTime"]
            dat["eta"] = timeLeft/3600.0  #  timeleft in hours

            # weird, python 2 cannot strftime any date below 1900

            # now convert all to string
            dat["currentStep"] = str(dat["currentStep"])
            dat["totalStep"]   = str(dat["totalStep"])
            dat["avgTime"]     = str(dat["avgTime"])
            dat["submitted"]   = dat["submitted"].strftime('%I:%M %p %b %d ')
            dat["lastUpdated"] = dat["lastUpdated"].strftime('%I:%M %p %b %d ')
            dat["eta"]         = str(dat["eta"]) +' hours'
            self.jobInfos.append(dat)
        print("All data is updated")
        self.saveJson()



    def saveJson(self):
        with open('info.json','w') as f:
            json.dump(self.jobInfos,f,indent=4)
        print("Saved configuration in info.json")



    def readJson(self):
        print("Reading configuration form info.json")
        with open('./info.json') as f: 
            info = json.load(f)
        return info


    def requestData(self,host,location,jId):   # calls and update a specifc job data
        cfg={}
        user_config = self.ssh_config.lookup(host)
        cfg['hostname'] = user_config['hostname']
        cfg['username'] = user_config['user']
        cfg['port'] ='22'
        cfg['sock'] = paramiko.ProxyCommand(user_config['proxycommand'])

        self.client.connect(**cfg)
        # sftp = paramiko.SFTPClient.from_transport(self.client)
        sftp = self.client.open_sftp()

        print("Requesting data from {} at {}".format(host, location))
        # Download
        filepath = location+"/fort.21"
        localpath = 'tmp.dat'
        sftp.get(filepath,localpath)
        if sftp: sftp.close()
        df = self.readData()
        df.to_pickle(jId) # save the file and return df
        return df


    def readData(self,file='tmp.dat'):
        with open(file) as f:
            txt = f.read()

        txt = txt.split("Starting Propagation:")[1].split('\n')[5:]

        # splits along column
        dat = [i.split() for i in txt]
        dat = filter(lambda x : True if len(x)==7 else False, dat)
        # merge the time and date column

        dat = [[ i[0],i[1], i[2]+' '+i[3], i[4],i[5],i[6]] for i in dat]
        # print(dat[0])
        col = {"step":'int', 'time':'float64','timeStamp':"datetime64", 'timeDelay':'float64', 'energy':'float64','norm':'float64'}

        df = pd.DataFrame(dat,columns=['step', 'time', 'timeStamp', 'timeDelay', 'energy','norm'])
        # print(df)
        df = df.astype(col)
        return df


if __name__ == "__main__":
    dd = DataRequest()
    dd.updateData()


