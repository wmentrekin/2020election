#The predictive model exists in this file
import pandas as pd

#Scrapes state data
def state_scrape():
	print("Scraping state data")

#Scrapes the pollster data
def pollster_scrape():
	print("Scraping pollster data")

#Scrapes the poll data
def poll_scrape():
	print("Scraping poll data")

#Creates State class and does some calculations
class State:

	states = []

	def __init__(self, name, abbreviation, ev, population, election16, pvi, turnout):
		self.name = str(name)
		self.abbreviation = str(abbreviation)
		self.ev = int(ev)
		self.population = int(population)
		self.election16 = {"D":election16[0], "R":election16[1], "Total":election16[2]}
		self.pvi = {"party":pvi[1], "margin":pvi[2]}
		self.turnout = turnout
		self.polls = []
		State.states.append(self)

	def __str__(self):
		return "{} ({}) has {} electoral votes, a population of {}, and a Cook PVI of {}+{}.".format(self.name, self.abbreviation, self.ev, self.population, self.pvi["party"], self.pvi["margin"])

	def __repr__(self):
		return "{name:" + self.name + ", abbreviation:" + self.abbreviation + ", ev:" + str(self.ev) + ", population:" + str(self.population) + ", election:" + str(self.election16) + ", pvi:" + str(self.pvi) + ", turnout:" + str(self.turnout) + ", polls:" + self.polls + "}"

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
		return "{} has a grade of {} from 538 and a mean-reverted bias of {}%.".format(self.name, self.grade, self.bias)
	
	def __repr__(self):
		return "{name:" + self.name + ", grade:" + self.grade + ", bias" + self.bias + "}"

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
def create_states():
	state_data = pd.read_csv("state_data.csv")
	for row in state_data.iterrows():
		State(row["state"],
    	  	row["abbrev"],
    	  	row["ev"],
    	  	row["population"],
    	  	[row["d16"],row["r16"],row["total16"]],
    	  	[row["pvi"],row["pvi_party"],row["pvi_margin"]],
    	  	row["turnout"])

#Creates Pollster Objects
def create_pollsters():
	pollster_data = pd.read_csv("pollster_data.csv")
	for row in pollster_data.iterrows():
		Pollster(row['POLLSTER'], row['538 GRADE'], row['MEAN-REVERTED BIAS'])

#Creates Poll Objects

#Normalizes Polls with Pollster Ratings

#Aggregates Normalized Polls by State & Date into Single Rating

#Creates Distribution for both candidates in all states

#Runs random numbers on distribution

#Aggregates model

#Run Model
def model():
	state_scrape()
	pollster_scrape()
	poll_scrape()
	create_states()
	create_pollsters()