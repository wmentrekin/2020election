#Will create pollster class and measure the accuracy of each pollster
from Poll import *

class Pollster:

	pollsters = []

	def __init__(self, name, grade, party_bias, percent_bias):
		self.name = name
		self.grade = grade
		self.party_bias = party_bias
		self.percent_bias = percent_bias
		self.correction2016 = 0
		pollsters.append(self)

	def set_correction(self):
		self.correction2016 = 0