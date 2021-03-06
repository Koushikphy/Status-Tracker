import pandas as pd 
import json, paramiko,os,re
from random import choice
from string import digits
from datetime import datetime, timedelta


class DataRequest():
    def __init__(self):
        # self.jobInfos = []
        paramiko.util.log_to_file("ssh_log.log")  #<- sometimes throws problem
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
                dat["chunk"] = "norm"
            df, totalStep, HostName = self.requestData(dat['host'],dat['location'],dat["id"])

            dat["HostName"] = HostName
            dat["currentStep"] = df["step"].iloc[-1]
            dat["totalStep"] = totalStep # do it somehow else
            dat["submitted"] = df["timeStamp"].iloc[0]#.strftime('%H:%M:%S %b %d ')
            dat["lastUpdated"] = df["timeStamp"].iloc[-1]#.strftime('%H:%M:%S %b %d ')
            dat["avgTime"] = df["timeDelay"].mean()
            timeLeft = (dat["totalStep"] - dat["currentStep"])*dat["avgTime"]
            dat["eta"] = timeLeft/3600.0  #  timeleft in hours  
            timeSpent = dat["lastUpdated"] - dat["submitted"]
            dat["timeSpent"] = timeSpent.total_seconds()/3600.0  #  timespent in hours  

            # weird, python 2 cannot strftime any date below 1900

            # now convert all to string
            dat["currentStep"] = str(dat["currentStep"])
            dat["totalStep"]   = str(dat["totalStep"])
            dat["avgTime"]     = '{:.2f} sec'.format(dat["avgTime"]) 
            dat["submitted"]   = dat["submitted"].strftime('%I:%M:%S %p %b %d ')
            dat["lastUpdated"] = dat["lastUpdated"].strftime('%I:%M:%S %p %b %d ')
            dat["eta"]         = "{:.2f} hours".format(dat["eta"])
            dat["timeSpent"]   = "{:.2f} hours".format(dat["timeSpent"])
            self.jobInfos.append(dat)
        print("All data is updated")
        self.saveJson()



    def saveJson(self):
        with open('info.json','w') as f:
            json.dump(self.jobInfos,f,indent=4)
        print("Saved configuration in info.json")



    def readJson(self):
        print("Reading configuration form info.json")
        with open('info.json') as f: 
            info = json.load(f)
        return info


    def requestData(self,host,location,jId): # calls and update a specifc job data
        cfg={}
        user_config = self.ssh_config.lookup(host)
        # print(user_config)
        cfg['hostname'] = user_config['hostname']
        cfg['username'] = user_config['user']
        cfg['port'] ='22'
        cfg['sock'] = paramiko.ProxyCommand(user_config['proxycommand'])

        self.client.connect(**cfg)
        # sftp = paramiko.SFTPClient.from_transport(self.client)
        sftp = self.client.open_sftp()

        print("Requesting data from {} at {}".format(host, location))
        # Download
        filepath = location+"/abc.log"
        localpath = 'tmp.dat'
        # print(filepath)
        sftp.get(filepath,localpath)
        print("Data received")
        if sftp: sftp.close()
        df, totalStep, HostName = self.readData()
        df.to_pickle('data/'+jId, protocol=2) # save the file and return df
        return df, totalStep, HostName


    def readData(self,file='tmp.dat'):
        with open(file) as f:
            txt = f.read()
        HostName = re.findall(  'Host: (\w+)' , txt)[0]
        totalStep = int(re.findall('Total Time Step: (\d+)', txt)[0])
        txt = txt.split("Starting Propagation:")[1].split('\n')[5:]
        # splits along column
        dat = [i.split() for i in txt]
        dat = filter(lambda x : True if len(x)==7 else False, dat)
        # merge the time and date column

        dat = [[ i[0],i[1], i[2]+' '+i[3], i[4],i[5],i[6]] for i in dat]
        # problem on timedelay column
        for i in range(len(dat)):
            try:
                float(dat[i][3])
            except:
                dat[i][3] = dat[i-1][3]
        # print(dat[0])
        col = {"step":'int', 'time':'float64','timeStamp':"datetime64", 'timeDelay':'float64', 'energy':'float64','norm':'float64'}

        df = pd.DataFrame(dat,columns=['step', 'time', 'timeStamp', 'timeDelay', 'energy','norm'])
        # print(df)
        df = df.astype(col)
        return df, totalStep, HostName


if __name__ == "__main__":
    dd = DataRequest()
    dd.updateData()


