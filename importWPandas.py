import requests
import pandas as pd
import datetime
import time

def importTodaysData():
    
    basicPage = requests.get('https://fantasy.premierleague.com/drf/elements/').json()
    basicData = pd.DataFrame(basicPage)
    basicData['date']=datetime.date.today()

    return basicData

def mergeNewData(newData):
	# Mac
    #dataName = '/Users/Henry/GitHub/FPL/data/basicDataStore.pkl'
    # RaspberryPi
    dataName = '~/GitHub/FPL/data/basicDataStore.pkl'
    dataStore = pd.read_pickle(dataName)
    frames = [dataStore, newData]
    newDataStore = pd.concat(frames)
    newDataStore.to_pickle(dataName)

def saveNewData(newData):
    # Mac
    #filepath = '/Users/Henry/GitHub/FPL/data/dailyStore/'

    # Raspberry Pi
    filepath = '~/GitHub/FPL/data/dailyStore/'
    name = '{}.pkl'.format(datetime.date.today())
    
    newData.to_pickle(filepath+name)

def dailyTask():
	print('running tasks')
	todaysData = importTodaysData()

	saveNewData(todaysData)
	mergeNewData(todaysData)


def main():

	for i in range(0,365):
		# sleep until 2AM
		t = datetime.datetime.today()
		future = datetime.datetime(t.year,t.month,t.day,7,0)
		if t.hour >= 7 and t.minute >= 0:
			future += datetime.timedelta(days=1)
		wait = (future-t).seconds
		print('Waiting {} seconds.'.format(wait))
		time.sleep(wait)

    	#do 9AM stuff
		dailyTask()
		print('Tasks done for today, recalculating in 1 hour.')
		time.sleep('3600')
if __name__ == '__main__':
	main()