import numpy as np
import pandas as pd

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
		return "{} has a grade of {} from 538 and usually is off by {}%."
	
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