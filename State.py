#Creates State class and does some calculations
import numpy as np
import pandas as pd

class State:

	states = []

	def __init__(self, name, abbreviation, ev, population, election16, pvi, demographics, registration, turnout):
		self.name = str(name)
		self.abbreviation = str(abbreviation)
		self.ev = int(ev)
		self.population = int(population)
		self.election16 = {"D":election16[0], "R":election16[1], "Total":election16[2]}
		self.pvi = {"party":pvi[1], "margin":pvi[2]}
		self.dem = demographics
		self.registration = registration
		self.turnout = turnout
		self.polls = []
		State.states.append(self)

	def __str__(self):
		return "{} ({}) has {} electoral votes, a population of {}, and a Cook PVI of {}+{}.".format(self.name, self.abbreviation, self.ev, self.population, self.pvi["party"], self.pvi["margin"])

	def __repr__(self):
		return "{name:" + self.name + ", abbreviation:" + self.abbreviation + ", ev:" + str(self.ev) + ", population:" + str(self.population) + ", election:" + str(self.election16) + ", pvi:" + str(self.pvi) + ", demographics:" + str(self.dem) + ", registration:" + str(self.registration) + ", turnout:" + str(self.turnout) + "}"

	def set_polls():
		self.polls = Poll.poll_dict[self.name]