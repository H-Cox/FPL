import pickle
import requests
import re
import os
import Importdata as Id
import numpy as np
#import matplotlib.pyplot as plt
from sklearn import datasets, linear_model
from sklearn.metrics import mean_squared_error

'''
This file contains some functions you can use to predict scores for players in FPL.
It makes use of the Importdata.py file so make sure its in the working directory.
You can do a simple fit easily from the terminal or an IDE.

First load this file so you can use the functions.

$ import linear_regression as lr

Next, you need to generate or load some examples from the historical data.
e.g.
$ filename = "machine_learning_examples"
$ [data, np_examples,np_prediction_set] = lr.import_and_save_examples(filename)

or if you have already saved the data before

$ filename = "machine_learning_examples"
$ [data, np_examples, np_prediction_set] = lr.load_examples(filename)

see the code for this below.
'''
def import_and_save_examples(filename):
	
	[data, examples, prediction_set] = Id.generate_examples()
	np_examples = np.array(examples)
	np_prediction_set = np.array(prediction_set)
	with open(filename+'.pkl','wb') as f:
		pickle.dump([data, np_examples,np_prediction_set],f) 
	return [data, np_examples,np_prediction_set]

def load_examples(filename):

	with open(filename+'.pkl','rb') as f:
		data, np_examples, np_prediction_set = pickle.load(f)

	return [data, np_examples, np_prediction_set]

'''
Next we simply perform the linear regression using the sklearn package
enter
$ [regr, diff_counts, mean_sq_error] = lr.perform_linear_regression(np_examples)
'''

def perform_linear_regression(np_examples):

	[x_train, y_train, x_test, y_test] = generate_train_test_examples(np_examples)

	regr = linear_model.LinearRegression()

	regr.fit(x_train, y_train)

	[diff_counts, mean_sq_error] = test_model_predictions(regr, x_test, y_test)

	return [regr, diff_counts, mean_sq_error]

'''
Now we are ready to predict next weeks scores.

$ results = lr.predict_next_week(regr, np_prediction_set)

You can edit the complexity of the model by changing the type of model used
(see the sklearn website) or adding features to the examples in the 'generate_examples'
function in the Importdata.py file.
'''
def predict_next_week(model,prediction_set):

	y_pred = model.predict(prediction_set)

	index = sorted(range(len(y_pred)), key=lambda k: y_pred[k], reverse=True)
	player_ids = np.array(index)+1
	player_scores = np.array(y_pred)
	player_scores = player_scores[index]

	return dictionary(zip(player_ids,player_scores))

'''
The scripts below are used by the main scripts to perform the analysis so if you 
fiddle around with them some then stuff above might break!
'''

def slice_examples(np_examples, number_examples_required):

	[row,col] = np_examples.shape

	new_order = np.random.permutation(row)

	shuffled_examples = np_examples[new_order,:]

	return shuffled_examples[:number_examples_required,:]

def generate_train_test_examples(np_examples):

	[row,col] = np_examples.shape

	new_order = np.random.permutation(row)

	shuffled_examples = np_examples[new_order,:]

	number_for_testing = row//10 + 1

	y_train = shuffled_examples[:-number_for_testing,0]
	y_test = shuffled_examples[-number_for_testing:,0]

	x_train = shuffled_examples[:-number_for_testing,1:]
	x_test = shuffled_examples[-number_for_testing:,1:]

	return [x_train, y_train, x_test, y_test]

def test_model_predictions(model, x_test, y_test):

	y_pred = model.predict(x_test)

	differences = np.array(y_test-y_pred)

	abs_diff = np.abs(np.round(differences))

	max_diff = int(max(abs_diff))

	diffs = list(range(0,max_diff+1))

	diff_counts = []

	for diff in diffs:
		diff_counts.append(len(abs_diff[abs_diff==diff]))

	mean_sq_error = mean_squared_error(y_test, y_pred)

	return [diff_counts, mean_sq_error]

def test_model(np_examples):

	[row,col] = np_examples.shape

	test_number_step = row//10 + 1

	test_numbers = list(range(test_number_step,row,test_number_step))
	test_numbers.append(row)

	mean_sq_error = []

	for number in test_numbers:

		temp_MSE = []

		for repeat in range(50):

			examples = slice_examples(np_examples,number)

			[regr, diff_counts, MSE] = perform_linear_regression(examples)

			temp_MSE.append(MSE)

		mean_sq_error.append(np.mean(temp_MSE))

	#plt.plot(test_numbers, mean_sq_error)
	#plt.show()
	return [test_numbers, mean_sq_error, regr]





