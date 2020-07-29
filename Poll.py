#will create poll class
from State import *
from Pollster import *

class Poll:

	poll_by_state = {}
	for state in State.states:
		poll_by_state[state.name] = []
	poll_by_pollster = {}
	for pollster in Pollster.pollsters:
		poll_by_state[pollster.name] = []

	def __init__(self, state, date, size, pollster, d, r):
		self.state = state
		self.date = date
		self.size = size
		self.pollster = pollster
		self.d = d
		self.r = r
		poll_by_state[self.state.name].append(self)
		poll_by_pollster[self.pollster.name].append(self)