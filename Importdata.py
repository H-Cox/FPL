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

def import_basic_data():
	# pull the web page in
	r = requests.get('https://fantasy.premierleague.com/drf/elements/').json()

	# export keys and all the values for each player
	headings = list(r[0].keys())
	data_values = [list(r[i].values()) for i in range(len(r))]

	return [headings, data_values]

def get_full_data_types():

	# download the player data
	r = requests.get('https://fantasy.premierleague.com/drf/element-summary/1').json()

	# extract history keys
	return list(r['history'][0].keys())

def clean_history_data(player_history):

	# select data types to use
	index = [7,8,10,11,12,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,
			30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,
			48,49,50,53,5,4,3]

	# initialise history and loop throuh extracting data
	gw_hist = []
	for w, week in enumerate(player_history):
	
		temp = list(week.values())

		# sort out team and opponent goals and if it was a home game
		# set if home or away and extract opponent
		if temp[5] == 'false':
			# if false it was an away fixture
			temp[5] = '0'
			index[-2] = 4
			index[-1] = 3
			gw_hist.append([temp[i] for i in index])
		else:
			temp[5] = '1'
			index[-2] = 3
			index[-1] = 4
			gw_hist.append([temp[i] for i in index])

	return gw_hist

def clean_fixture_data(player_fixtures):

	# initialise and loop through fixtures
	gw_fixtures = []
	for g, fixture in enumerate(player_fixtures):
		# extract main data values
		temp = list(fixture.values())

		# set if home or away and extract opponent
		if temp[5] == 'false':
			#if false it was away
			temp[5] = '0'
			gw_fixtures.append([temp[i] for i in [5,6,17]])
		else:
			temp[5] = '1'
			gw_fixtures.append([temp[i] for i in [5,6,16]])

	# return final list of lists, data types are is it home (1)
	# or false(0), fixture difficult and opponent team id
	return gw_fixtures

def history_pad(gw_history, num_weeks_missing):

	items = len(gw_history[0])

	non_playing_week = 45*[0]

	missing_weeks = num_weeks_missing*[non_playing_week]

	return missing_weeks+gw_history

# import full data for a single player
def import_player_data(player_id):

	# download the player data
	r = requests.get('https://fantasy.premierleague.com/drf/element-summary/' + str(player_id)).json()

	history_data = r['history']

	gw_history = clean_history_data(history_data)

	# now split off the upcoming fixtures
	fixture_data = r['fixtures']

	gw_fixtures = clean_fixture_data(fixture_data)

	first_gw_played = 1

	# pad out the history data if the player was not in the system originally
	if len(gw_history)+len(gw_fixtures) != 38:

		num_weeks_missing = 38 - len(gw_history)-len(gw_fixtures)

		gw_history = history_pad(gw_history, num_weeks_missing)

		first_gw_played += num_weeks_missing

	# return the results
	return [first_gw_played, gw_history, gw_fixtures]

def import_full_data():

	[headings ,basic_data] = import_basic_data()

	number_players = len(basic_data)

	player_data = []
	examples = []

	for i in range(number_players-1):

		temp_data = import_player_data(i+1)
		temp_examples = player_data_to_examples(temp_data)

		player_data.append(temp_data)
		examples = examples + temp_examples

		if i%10 == 0:
			print(i)

	return [player_data,examples]

# convert player data_file into a set of examples to learn from
def player_data_to_examples(player_data):

	history = player_data[0]

	num_weeks = len(history)
	examples = []
	for x in range(num_weeks-3):
		examples.append([history[x+3][0]]+history[x+2]+history[x+1]+history[x])
	return examples

# save the list of data types in data_names to a file
def save_data_types(data_names,filename):

	data_file = open(filename,'w')

	for id, name in enumerate(data_names):
		data_file.write(','.join([str(id),name])+'\n')

	data_file.close()

# saves the ID number and names of players to file
def save_names(player_data,filename):

	# open the data file
	data_file = open(filename,'w')

	# loop through players writing their names in
	for p in player_data:
		input = [p[i].strip('"') for i in [0,6,7]]
		data_file.write(','.join(input)+'\n')

	# close data file
	data_file.close()

# saves the selected datatypes into the file
def save_data(player_data,data_names,data_index,filename):

	# open the file
	data_file = open(filename,'w')

	# write the header for each column
	input = [data_names[i].strip('"') for i in data_index]
	data_file.write(','.join(input)+'\n')

	# loop through the players writing in the data
	for p in player_data:
		input = [p[i].strip('"') for i in data_index]
		data_file.write(','.join(input)+'\n')

	# close the file
	data_file.close()

def save_examples(examples,filename):

	file = open(filename,'w')
	for l in examples:
		file.write(','.join(l) + '\n')

def save_player(player_data,filename):

	file = open(filename,'w')

	for l in player_data[0]:
		file.write(','.join(l) + '\n')
	file.write('\n')
	for l in player_data[1]:
		file.write(','.join(l) + '\n')

	file.close()

def save_all_data(filename):
	# This script automatically downloads, sorts and saves all the data
	# from the FPL site in a csv format where each player is on a new line
	# and the headings of each data type are on the first line.
	# written by Henry Cox 02/11/17

	print('Running script to import and save all player data...')
	
	# open the file to be written to
	file = open(filename,'w')

	print('Importing basic player data...')
	
	# import basic data and seperate data names and data values
	[headings, basic_data_values] = import_basic_data()

	# find the number of players
	number_players = len(basic_data_values)

	# set up list for all the data
	player_data = []

	print('Importing full data for each player...')
	# loop through each player downloading the data
	for i in range(number_players-1):

		if i%50 == 0:
			print('Processing player {} of {}...'.format(i+1,number_players))

		# data is imported here
		temp_data = import_player_data(i+1)

		# player_data has [basic, history, future]
		player_data.append([basic_data_values[i]+[temp_data[0]]] + temp_data[1:])


	# figure out the number of weeks completed and the number remaining
	number_history = len(player_data[0][1])
	number_future = len(player_data[0][2])

	# get the data names for the full history data
	full_data_types = get_full_data_types();

	# index to select the history data we want
	index = [7,8,10,11,12,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,
			30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,
			48,49,50,53,5]

	# set the data names according to our index above
	full_data_names = [full_data_types[j] for j in index]+['team_goals','opponent_goals']

	# loop through each week in history adding in the titles
	for i in range(number_history):
		input = []
		# loop through the week itself changing for each value
		for j in range(len(player_data[0][1][0])):

			input.append('GW {}: '.format(i+1) + full_data_names[j])

		# save to the headings file
		headings = headings + ['First_gameweek'] + input

	# set what the headings are for future fixtures
	future_headings = ['Home_or_away','Fixture_difficulty','Opponent_id']

	# loop through each future week adding in titles in a similar way as before
	for i in range(number_future):
		input = []
		for j in range(len(player_data[0][2][0])):
			# the correct gameweek number is i + 1 + numhist
			input.append('GW {}: '.format(i+1+number_history) + future_headings[j])

		headings = headings + input

	print('Writing to file...')

	# write headings to first line of the file
	file.write(','.join(headings) + '\n')

	# now on to writing in the actual data
	# loop through each player
	for i in range(len(player_data)):

		# set up the input to be written for this player
		input = []
		# sort out the basic data and add to input
		input = input + [str(player_data[i][0][j]).strip('"') for j in range(len(player_data[i][0]))]

		# now sort out the full history and future fixtures data
		for j in range(1,3):

			input = input + [str(item) for sublist in player_data[i][j] for item in sublist]
		
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

		full_filepath = path+'/'+filename+'.csv'

		print('File will be saved to: {}'.format(full_filepath))

		selection = input('Enter y if this is ok:')

		if selection.lower().strip() == 'y':
			break

	save_all_data(full_filepath)



