#!/usr/bin/env python

"""Model.py: A statistical predictive model for the 2020 United States presidential election"""

import os
import sys

from bs4 import BeautifulSoup
import math
import pandas as pd
import requests
from scipy.stats import binom
import xlrd

__author__ = "Wyatt Entrekin"
__version__ = "1.0.0"
__email__ = "wmentrekin@gmail.com"
__status__ = "Production"

#####################
##      TO-DO      ##
#####################
#1) Apply Poll rating to 2016 election results for each State
#2) Create a distribution of possible Outcomes for each State
#3) Run 10,000 random numbers on the distribution for each State
#4) Visualize results

#Scrapes state data
def state_scrape():

	states = {}

	#Name & Population
	populations = pd.read_csv('data/populations.csv') #File Downloaded from Census.gov
	count = 1
	for population in populations.iterrows():
		state_dict = {}
		state_dict['population'] = population[1]['P001001'].split('(')[0]
		states[str(population[1]['NAME'])] = state_dict

		print('Scraping Data for State Populations: ' + str(count) + '/51')
		count += 1

	#2016 Election Results
	loc = ("data/federalelections2016.xlsx") #File Downloaded from FEC Website
	wb = xlrd.open_workbook(loc)
	sheet = wb.sheet_by_index(2)
	results = []
	count = 1
	for i in range(55):
		if i > 3:
			result = {}
			result['D'] = sheet.cell_value(i, 4)
			result['R'] = sheet.cell_value(i, 3)
			result['Total'] = sheet.cell_value(i, 6)
			if result['R'] > result['D']:
				result['EV'] = sheet.cell_value(i, 1)
			else:
				result['EV'] = sheet.cell_value(i, 2)
			results.append(result)
			print('Scraping Data for 2016 Election Results: ' + str(count) + '/51')
			count += 1
	count = 0
	for state in states:
		states[state]['2016'] = results[count]
		count += 1

	return states

#Scrapes the pollster data
def pollster_scrape():

	pollsters = []

	#Setting Up Scrape
	url = "https://projects.fivethirtyeight.com/pollster-ratings/"
	page = requests.get(url)
	soup = BeautifulSoup(page.content, 'html.parser')

	#Finding Specific Data
	names = soup.find_all('td', class_='td js-pollster pollster')
	grades = soup.find_all('div', class_='gradeText')
	bias = soup.find_all('div', class_='biasTextBG innerDiv')

	#Compiling Data
	for i in range(20):
		pollster = {}
		pollster['name'] = names[i]['data-sort']
		pollster['grade'] = grades[i].text[1::]
		pollster['bias'] = bias[i].text.split('+')
		pollsters.append(pollster)
		print('Scraping Data on Reputable Pollsters: ' + str(i + 1) + '/20')

	return pollsters

#Scrapes the poll data
def poll_scraper():

	polls = []

	#Scraping Polls for Each State
	base = 'https://www.270towin.com/2020-polls-biden-trump/'
	for state in State.states:
		name = state.name.lower().replace(' ', '-')
		url = base + name
		page = requests.get(url)
		soup = BeautifulSoup(page.content, 'html.parser')
		pollsters = soup.find_all('td', class_='poll_src')
		dates = soup.find_all('td', class_='poll_date')
		d = soup.find_all('td', candidate_id='D')
		r = soup.find_all('td', candidate_id='R')
		errors = soup.find_all('td', class_='poll_sample')
		print('Scraping Data for Polls Conducted in ' + str(state.name))

		#Gathering Data for Each Poll
		for i in range(len(dates)):
			polldict = {}
			polldict['state'] = state
			polldict['pollster'] = pollsters[i].text.strip('\n')
			polldict['date'] = dates[i].text
			polldict['D'] = d[i].text.split('%')[0].strip()
			polldict['R'] = r[i].text.split('%')[0].strip()
			error = errors[i].text.split(' &plusmn')
			polldict['error'] = 0 if len(error) == 1 else error[1].split('%')[0]
			polls.append(polldict)

	return polls

#Creates State class and does some calculations
class State:

	states = []

	def __init__(self, name, ev, population, election16):
		self.name = str(name)
		self.ev = int(ev)
		self.population = int(population)
		self.election16 = {"D": int(election16[0]), "R": int(election16[1]), "Total": int(election16[2])}
		self.poll_rating = {}
		State.states.append(self)

	def __str__(self):
		return "{} has {} electoral votes and a population of {}".format(self.name, self.ev, self.population)

#Creates pollster class and measure the accuracy of each pollster
class Pollster:

	pollsters = []

	def __init__(self, name, grade, bias):
		self.name = str(name)
		self.grade = str(grade)
		self.bias = bias
		Pollster.pollsters.append(self)
	
	def __str__(self):
		return "{} has a grade of {} from 538 and a mean-reverted bias of {}+{}%.".format(self.name, self.grade, self.bias[0], self.bias[1])

	def set_correction(self):
		self.correction2016 = 0

#Create poll class and organizes them by pollster and state
class Poll:

	polls = []

	def __init__(self, state, date, pollster, d, r, error):
		self.state = state
		self.date = date
		self.pollster = pollster
		self.d = float(d)
		self.r = float(r)
		self.error = float(error)
		Poll.polls.append(self)

	def __str__(self):
		return "{} conducted a poll in {} on {} which had Biden at {} and Trump at {} with an error of {}%.".format(self.pollster.name, self.state.name, self.date, self.d, self.r, self.error)

#Creates State Objects
def create_states(states):
	count = 1
	for state in states.keys():
		print('Instantiating State Objects: ' + str(count) + '/51')
		count += 1
		State(state, states[state]['2016']['EV'], states[state]['population'], (states[state]['2016']['D'], states[state]['2016']['R'], states[state]['2016']['Total']))

#Creates Pollster Objects
def create_pollsters(pollsters):

	count = 1
	for pollster in pollsters:
		print('Instanting Pollster Objects: ' + str(count) + '/20')
		count += 1

		#Checking if Pollster is Reputable, Then Instantiating Reference
		if pollster['grade'] in ['A+', 'A', 'A-', 'B+', 'B', 'B-']:
			Pollster(pollster['name'], pollster['grade'], pollster['bias'])

#Creates Poll Objects
def create_polls(polls):

	#Normalizing Pollster Names Between Pollster Instances & Polls
	names = {'SurveyUSA': 'SurveyUSA',
			 'Mason-Dixon': 'Mason-Dixon Polling & Strategy',
			 'Public Policy': 'Public Policy Polling',
			 'YouGov': 'YouGov',
			 'American Research Group': 'American Research Group',
			 'Quinnipiac': 'Quinnipiac University',
			 'NBC News/Marist': 'Marist College',
			 'Emerson College': 'Emerson College',
			 'InsiderAdvantage': 'Opinion Savvy/InsiderAdvantage',
			 'Univ. of New Hampshire': 'University of New Hampshire',
			 'Monmouth University': 'Monmouth University',
			 'CNN//SSRS': 'CNN/Opinion Research Corp.'}
	new_polls = []
	for poll in polls:
		if poll['pollster'] in names.keys():
			poll['pollster'] = names[poll['pollster']]
			new_polls.append(poll)

	#Instantiating Poll References
	success = 0
	for pollster in Pollster.pollsters:
		for poll in new_polls:
			if pollster.name == poll['pollster']:
				Poll(poll['state'], poll['date'], pollster, poll['D'], poll['R'], poll['error'])
				success += 1
				print('Instantiating Poll Objects: ' + str(success) + '/' + str(len(new_polls)))

#Normalizes Polls with Pollster Ratings
def normalize():

	#Groups Polls by Pollster
	polls_by_pollster = {}

	count = 0
	for pollster in Pollster.pollsters:
		pollster_name = pollster.name
		polls_by_pollster[pollster] = []
		for poll in Poll.polls:
			poll_name = poll.pollster.name
			if pollster_name == poll_name:
				print('Grouping Polls by Pollster: ' + str(count + 1) + '/' + str(len(Poll.polls)))
				count += 1
				polls_by_pollster[pollster].append(poll)

	#Normalizes Polls according to Pollster grade and bias
	count = 0
	error_multipliers = {'A+': 1.0, 'A': 1.2, 'A-': 1.4, 'B+': 1.6, 'B': 1.8, 'B-': 2.0}
	for key in polls_by_pollster.keys():
		grade = key.grade
		error_multiplier = error_multipliers[grade]
		bias_party = key.bias[0]
		bias_amount = float(key.bias[1])
		for poll in polls_by_pollster[key]:
			poll.error *= error_multiplier
			if bias_party == 'D':
				poll.d -= bias_amount
			else:
				poll.r -= bias_amount
			print('Normalizing Polls according to Pollster bias and grade: ' + str(count + 1) + '/' + str(len(Poll.polls)))
			count += 1

#Aggregates Normalized Polls by State & Date into Single Rating
def aggregate():

	#Group Polls by State
	polls_by_state = {}

	count = 0
	for state in State.states:
		state_name = state.name
		polls_by_state[state] = []
		for poll in Poll.polls:
			poll_state = poll.state.name
			if state_name == poll_state:
				print('Grouping Polls by State: ' + str(count + 1) + '/' + str(len(Poll.polls)))
				count += 1
				polls_by_state[state].append(poll)
	
	#Aggregating Polls into singular rating for each State
	count = 0
	for key in polls_by_state.keys():
		rating = {}
		d_sum = 0
		r_sum = 0
		error_sq_sum = 0
		n = len(polls_by_state[key])
		if n > 0:
			for poll in polls_by_state[key]:
				d_sum += poll.d
				r_sum += poll.r
				error_sq_sum += poll.error**2
			rating['D'] = round(d_sum / n, 1)
			rating['R'] = round(r_sum / n, 1)
			rating['error'] = round(math.sqrt(error_sq_sum), 2)
		else:
			n = key.election16['Total']
			d = key.election16['D']
			r = key.election16['R']
			prob_d = d / n
			prob_r = r / n
			var_d = binom.var(n, prob_d)
			var_r = binom.var(n, prob_r)
			se_d = math.sqrt(var_d / n)
			se_r = math.sqrt(var_r / n)
			rating['D'] = round(100 * prob_d, 1)
			rating['R'] = round(100 * prob_r, 1)
			rating['error'] = round(math.sqrt(se_d**2 + se_r**2), 2)
		print('Aggregating Polls into singular rating for each State: ' + str(count + 1) + '/' + str(len(State.states)))
		count += 1
		key.poll_rating = rating

#Creates Distribution for both candidates in all states

#Runs random numbers on distribution

#Aggregates model

#Run Model
def model():

	#Scraping & Instantiating States, Pollsters, & Polls
	create_states(state_scrape())
	create_pollsters(pollster_scrape())
	create_polls(poll_scraper())

	#Groups Polls by Pollster, Normalizes Polls according to Pollster grade and bias
	normalize()

	#Groups Polls by State, Aggregates Polls into singular rating for each state
	aggregate()

if __name__ == "__main__":
	model()