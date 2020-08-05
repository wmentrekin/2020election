#Will create pollster class and measure the accuracy of each pollster
import numpy as np
import pandas as pd

class Pollster:

	pollsters = []

	def __init__(self, name, grade, bias):
		self.name = name
		self.grade = grade
		self.bias
		pollsters.append(self)

	def set_correction(self):
		self.correction2016 = 0