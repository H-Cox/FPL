import requests
import re
import os

def f(regexStr,target):
	# refer to https://stackoverflow.com/questions/4026685/regex-to-get-text-between-two-characters
    mo = re.findall(regexStr,target)
    if not mo:
        print("NO MATCH")
    else:
        return mo

def importbasicdata():
	# pull the web page in
	r = requests.get('https://fantasy.premierleague.com/drf/elements/')

	# extract text and strip ends
	info = r.text
	info = info[2:-2]

	# split each players data out
	players = info.split('},{')

	return players

def getdatatypes(players):

	# extract all the data types
	pdatanames = list(f(r"(?<=,)[^:]*(?=:)",',' + players[0]))
	pdatanames = [item.strip('"') for item in pdatanames]

	return pdatanames

def getfhistdatatypes():

	# download the player data
	r = requests.get('https://fantasy.premierleague.com/drf/element-summary/1')

	# extract text
	info = r.text

	# split off the history and arrange data
	data = info.split(',"history":')
	data1 = data[0]
	hdata = data[1][2:-3]
	history = hdata.split('},{')

	# extract all the data types
	pdatanames = list(f(r"(?<=,)[^:]*(?=:)",',' + history[0]))
	pdatanames = [item.strip('"') for item in pdatanames]

	return pdatanames

def getdata(players):

	# we will fill in the player data
	pdataraw = []

	# loop through players extracting the data
	for i, player in enumerate(players):
		# use regex to find data between ':' and ','
		pdataraw.append(f(r"(?<=:)[^,]*(?=,)",player))
		pdataraw[i].append(player[-1])
	return pdataraw

def cleanhistorydata(playerhistory):

	# select data types to use
	index = [7,8,10,11,12,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,
			30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,
			48,49,50,53,5,4,3]

	# get lists of each previous gameweeks
	history = playerhistory.split('},{')

	# initialise history and loop throuh extracting data
	gwhist = []
	for w, week in enumerate(history):
	
		# extract main data values
		temp = (f(r"(?<=:)[^,]*(?=,)",week))

		# and final value
		final = week.split(',"opponent_team":')
		temp.append(final[1])

		# sort out team and opponent goals and if it was a home game
		# set if home or away and extract opponent
		if temp[5] == 'false':
			# if false it was an away fixture
			temp[5] = '0'
			index[-2] = 4
			index[-1] = 3
			gwhist.append([temp[i].strip('"') for i in index])
		else:
			temp[5] = '1'
			index[-2] = 3
			index[-1] = 4
			gwhist.append([temp[i].strip('"') for i in index])

	return gwhist

def cleanfixturedata(playerfixtures):
	# split off each upcoming fixture
	fixtures = playerfixtures.split('},{')

	# initialise and loop through fixtures
	gwfix = []
	for g, gws in enumerate(fixtures):
		# extract main data values
		temp = (f(r"(?<=:)[^,]*(?=,)",gws))

		# and final value
		final = gws.split(',"team_h":')
		temp.append(final[1])

		# set if home or away and extract opponent
		if temp[5] == 'false':
			#if false it was away
			temp[5] = '0'
			gwfix.append([temp[i].strip('"') for i in [5,6,17]])
		else:
			temp[5] = '1'
			gwfix.append([temp[i].strip('"') for i in [5,6,16]])

	# return final list of lists, data types are is it home (1)
	# or false(0), fixture difficult and opponent team id
	return gwfix

# import full data for a single player
def importplayerdata(id):

	# download the player data
	r = requests.get('https://fantasy.premierleague.com/drf/element-summary/' + str(id))

	# extract text
	info = r.text

	# split off the history and arrange data
	data = info.split(',"history":')
	data1 = data[0]
	hdata = data[1][2:-3]

	gwhist = cleanhistorydata(hdata)

	# now split off the upcoming fixtures
	data2 = data1.split(',"fixtures":')
	fdata = data2[1][2:-2]

	gwfix = cleanfixturedata(fdata)

	# return the results
	return [gwhist, gwfix]

def importfulldata():

	pdatabasic = getdata(importbasicdata())

	nplayers = len(pdatabasic)

	pdata = []
	examples = []

	for i in range(nplayers-1):

		pd = importplayerdata(i+1)
		pe = pd2examples(pd)

		pdata.append(pd)
		examples = examples + pe

		if i%10 == 0:
			print(i)

	return [pdata,examples]

# convert player datafile into a set of examples to learn from
def pd2examples(pd):

	history = pd[0]

	numweeks = len(history)
	examples = []
	for x in range(numweeks-3):
		examples.append([history[x+3][0]]+history[x+2]+history[x+1]+history[x])
	return examples

# save the list of data types in pdatanames to a file
def savedatatypes(pdatanames,filename):

	datafile = open(filename,'w')

	for id, name in enumerate(pdatanames):
		datafile.write(','.join([str(id),name])+'\n')

	datafile.close()

# saves the ID number and names of players to file
def savenames(pdata,filename):

	# open the data file
	datafile = open(filename,'w')

	# loop through players writing their names in
	for p in pdata:
		input = [p[i].strip('"') for i in [0,6,7]]
		datafile.write(','.join(input)+'\n')

	# close data file
	datafile.close()

# saves the selected datatypes into the file
def savedata(pdata,pdatanames,dataindex,filename):

	# open the file
	datafile = open(filename,'w')

	# write the header for each column
	input = [pdatanames[i].strip('"') for i in dataindex]
	datafile.write(','.join(input)+'\n')

	# loop through the players writing in the data
	for p in pdata:
		input = [p[i].strip('"') for i in dataindex]
		datafile.write(','.join(input)+'\n')

	# close the file
	datafile.close()

def saveexamples(examples,filename):

	file = open(filename,'w')
	for l in examples:
		file.write(','.join(l) + '\n')

def saveplayer(playerdata,filename):

	file = open(filename,'w')

	for l in playerdata[0]:
		file.write(','.join(l) + '\n')
	file.write('\n')
	for l in playerdata[1]:
		file.write(','.join(l) + '\n')

	file.close()

def savealldata(filename):
	# This script automatically downloads, sorts and saves all the data
	# from the FPL site in a csv format where each player is on a new line
	# and the headings of each data type are on the first line.
	# written by Henry Cox 02/11/17

	print('Running script to import and save all player data...')
	
	# open the file to be written to
	file = open(filename,'w')

	print('Importing basic player data...')
	
	# import basic data and seperate data names and data values
	basicdata = importbasicdata()
	headings = getdatatypes(basicdata)
	basicdatavalues = getdata(basicdata)

	# find the number of players
	nplayers = len(basicdata)

	# set up list for all the data
	pdata = []

	print('Importing full data for each player...')
	# loop through each player downloading the data
	for i in range(nplayers-1):

		if i%50 == 0:
			print('Processing player {} of {}...'.format(i+1,nplayers))

		# data is imported here
		pd = importplayerdata(i+1)

		# pdata has [basic, history, future]
		pdata.append([basicdatavalues[i]] + pd)


	# figure out the number of weeks completed and the number remaining
	numhist = len(pdata[0][1])
	numfuture = len(pdata[0][2])

	# get the data names for the full history data
	fhisttypes = getfhistdatatypes();

	# index to select the history data we want
	index = [7,8,10,11,12,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,
			30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,
			48,49,50,53,5,4,3]

	# set the data names according to our index above
	fhistnames = [fhisttypes[j] for j in index]

	# loop through each week in history adding in the titles
	for i in range(numhist):
		input = []
		# loop through the week itself changing for each value
		for j in range(len(pdata[0][1][0])):

			input.append('GW {}: '.format(i+1) + fhistnames[j])

		# save to the headings file
		headings = headings + input

	# set what the headings are for future fixtures
	futureheadings = ['Home_or_away','Fixture_difficulty','Opponent_id']

	# loop through each future week adding in titles in a similar way as before
	for i in range(numfuture):
		input = []
		for j in range(len(pdata[0][2][0])):
			# the correct gameweek number is i + 1 + numhist
			input.append('GW {}: '.format(i+1+numhist) + futureheadings[j])

		headings = headings + input

	print('Writing to file...')

	# write headings to first line of the file
	file.write(','.join(headings) + '\n')

	# now on to writing in the actual data
	# loop through each player
	for i in range(len(pdata)):

		# set up the input to be written for this player
		input = []
		# sort out the basic data and add to input
		input = input + [pdata[i][0][j].strip('"') for j in range(len(pdata[i][0]))]

		# now sort out the full history and future fixtures data
		for j in range(1,3):

			input = input + [item for sublist in pdata[i][j] for item in sublist]
		
		# finally write this players data to the file	
		file.write(','.join(input) + '\n')
	
	# close the file	
	file.close()

	print('Done.')

# useful links 
# https://fantasy.premierleague.com/drf/bootstrap-static
# https://fantasy.premierleague.com/drf/elements/
# https://fantasy.premierleague.com/drf/element-summary/{player_id}

if __name__ == '__main__':

	path = os.getcwd()
	
	while True:

		filename = input('Enter the filename to save to:')

		fullfilepath = path+'/'+filename+'.csv'

		print('File will be saved to: {}'.format(fullfilepath))

		selection = input('Enter y if this is ok:')

		if selection.lower().strip() == 'y':
			print('Running script')
			break

	savealldata(fullfilepath)



