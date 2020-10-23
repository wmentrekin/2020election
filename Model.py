#The predictive model exists in this file
import pandas as pd
import requests
from bs4 import BeautifulSoup
import xlrd

#Scrapes state data
def state_scrape():
	states = {}

	#Name & Population
	populations = pd.read_csv('data/populations.csv')
	for population in populations.iterrows():
		state_dict = {}
		state_dict['population'] = population[1]['P001001'].split('(')[0]
		states[str(population[1]['NAME'])] = state_dict

	#2016 Election Results
	loc = ("data/federalelections2016.xlsx")
	wb = xlrd.open_workbook(loc)
	sheet = wb.sheet_by_index(2)
	results = []
	for i in range(55):
		if i > 3:
			result = {}
			result['D'] = sheet.cell_value(i, 4)
			result['R'] = sheet.cell_value(i, 3)
			result['Total'] = sheet.cell_value(i, 5)
			if result['R'] > result['D']:
				result['EV'] = sheet.cell_value(i, 1)
			else:
				result['EV'] = sheet.cell_value(i, 2)
			results.append(result)
	count = 0
	for state in states:
		states[state]['2016'] = results[count]
		count += 1

	return states

#Scrapes the pollster data
def pollster_scrape():
	url = "https://projects.fivethirtyeight.com/pollster-ratings/"
	page = requests.get(url)
	soup = BeautifulSoup(page.content, 'html.parser')
	names = soup.find_all('td', class_='td js-pollster pollster')
	grades = soup.find_all('div', class_='gradeText')
	bias = soup.find_all('div', class_='biasTextBG innerDiv')
	pollsters = []
	for i in range(20):
		pollster = {}
		pollster['name'] = names[i]['data-sort']
		pollster['grade'] = grades[i].text[1::]
		pollster['bias'] = bias[i].text.split('+')
		pollsters.append(pollster)
	return pollsters

#Scrapes the poll data

#Creates State class and does some calculations
class State:

	states = []

	def __init__(self, name, ev, population, election16):
		self.name = str(name)
		self.ev = int(ev)
		self.population = int(population)
		self.election16 = {"D":election16[0], "R":election16[1], "Total":election16[2]}
		self.polls = []
		State.states.append(self)

	def __str__(self):
		return "{} has {} electoral votes and a population of {}".format(self.name, self.ev, self.population)

	def __repr__(self):
		return "{name:" + self.name + ", ev:" + str(self.ev) + ", population:" + str(self.population) + ", election16:" + str(self.election16)  + ", polls:" + self.polls + "}"

	def set_polls(self):
		self.polls = Poll.poll_by_state[self.name]

#creates pollster class and measure the accuracy of each pollster
class Pollster:

	pollsters = []

	def __init__(self, name, grade, bias):
		self.name = name
		self.grade = grade
		self.bias = bias
		Pollster.pollsters.append(self)
	
	def __str__(self):
		return "{} has a grade of {} from 538 and a mean-reverted bias of {}+{}%.".format(self.name, self.grade, self.bias[0], self.bias[1])
	
	def __repr__(self):
		return "{name:" + self.name + ", grade:" + self.grade + ", bias" + self.bias[0] + "+" + self.bias[1] + "}"

	def set_correction(self):
		self.correction2016 = 0

#create poll class and organizes them by pollster and state
class Poll:

	poll_by_state = {}
	for state in State.states:
		poll_by_state[state.name] = []
	poll_by_pollster = {}
	for pollster in Pollster.pollsters:
		poll_by_state[pollster.name] = []

	def __init__(self, state, date, pollster, d, r, error):
		self.state = state
		self.date = date
		self.pollster = pollster
		self.d = d
		self.r = r
		self.error = error
		Poll.poll_by_state[self.state.name].append(self)
		Poll.poll_by_pollster[self.pollster.name].append(self)

#Creates State Objects
def create_states(states):
	for state in states.keys():
		State(state, states[state]['2016']['EV'], states[state]['population'], (states[state]['2016']['D'], states[state]['2016']['R'], states[state]['2016']['Total']))

#Creates Pollster Objects
def create_pollsters(pollsters):
	for pollster in pollsters:
		if pollster['grade'] in ['A+', 'A', 'A-', 'B+', 'B', 'B-']:
			Pollster(pollster['name'], pollster['grade'], pollster['bias'])


#Creates Poll Objects

#Normalizes Polls with Pollster Ratings

#Aggregates Normalized Polls by State & Date into Single Rating

#Creates Distribution for both candidates in all states

#Runs random numbers on distribution

#Aggregates model

#Run Model
def model():
	#create_states(state_scrape())
	create_pollsters(pollster_scrape())

if __name__ == "__main__":
	model()