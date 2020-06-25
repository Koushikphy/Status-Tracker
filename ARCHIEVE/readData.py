import pandas as pd
import json

def readData(file):
    with open(file) as f: txt = f.read()

    txt = txt.split("Starting Propagation:")[1].split('\n')[5:]

    # splits along column
    dat = [i.split() for i in txt]
    dat = filter(lambda x : True if len(x)==7 else False, dat)
    # merge the time and date column

    dat = [[ i[0],i[1], i[2]+' '+i[3], i[4],i[5],i[6]] for i in dat]
    # print(dat[0])
    col = {"step":'int', 'time':'float64','timeStamp':"datetime64", 'timeDelay':'float64', 'energy':'float64','norm':'float64'}

    df = pd.DataFrame(dat,columns=col.keys())
    df = df.astype(col)
    return df


# with open('./info.json') as f:
#     y = json.loads(f.read())


a = 3000
b = 5000
c = 8.8



df = readData('./fort.21')
print(df)

# e = (b-a)*c
# print(e)
# print( df["timeStamp"].iloc[-1] + pd.Timedelta(seconds=e)     )


df.to_pickle('data.pkl')