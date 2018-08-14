import requests
import pandas as pd
from datetime import date

def importTodaysData():
    
    basicPage = requests.get('https://fantasy.premierleague.com/drf/elements/').json()
    basicData = pd.DataFrame(basicPage)
    basicData['date']=date.today()
    return basicData

def mergeNewData(newData):
	
    dataName = '/Users/Henry/GitHub/FPL/data/basicDataStore.pkl'
    dataStore = pd.read_pickle(dataName)
    frames = [dataStore, newData]
    newDataStore = pd.concat(frames)
    newDataStore.to_pickle(dataName)

def saveNewData(newData):
    
    filepath = '/Users/Henry/GitHub/FPL/data/dailyStore/'
    name = '{}.pkl'.format(date.today())
    
    newData.to_pickle(filepath+name)