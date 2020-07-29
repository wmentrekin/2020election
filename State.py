#Creates State class and does some calculations
from Poll import *
from Pollster import *

class State:

	states = []

	def __init__(self, name, abbreviation, ev, population, demographics16, demographics20, election16, pvi, registration, turnout):
		self.name = name
		self.abbreviation = abbreviation
		self.ev = ev
		self.population = population
		self.dem16 = demographics16
		self.dem20 = demographics20
		self.election16 = election16
		self.pvi = pvi
		self.registration
		self.turnout
		self.polls = []
		states.append(self)

	def __str__(self):
		return "{} voted for {} in 2016, who won by {} percent of the vote".format(self.name, self.election16[0][0], (self.election[0][1] - self.election[1][1]))

	def set_polls():
		self.polls = Poll.poll_dict[self.name]