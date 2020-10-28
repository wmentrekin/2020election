#!/usr/bin/env python

"""Model.py: A statistical predictive model for the 2020 United States presidential election"""

import os
import sys

from bs4 import BeautifulSoup
import csv
import math
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap as Basemap
from matplotlib.colorbar import ColorbarBase
from matplotlib.colors import rgb2hex, Normalize
from matplotlib.patches import Polygon
import numpy as np
import pandas as pd
import requests
from scipy.stats import binom
import statistics
import xlrd

__author__ = "Wyatt Entrekin"
__version__ = "1.0.0"
__email__ = "wmentrekin@gmail.com"

#Scrapes state data
def state_scrape():

	states = {}

	#Name & Population
	populations = pd.read_csv('data/populations.csv') #File Downloaded from Census.gov
	for population in populations.iterrows():
		state_dict = {}
		state_dict['population'] = population[1]['P001001'].split('(')[0]
		states[str(population[1]['NAME'])] = state_dict

	#2016 Election Results
	loc = ("data/federalelections2016.xlsx") #File Downloaded from FEC Website
	wb = xlrd.open_workbook(loc)
	sheet = wb.sheet_by_index(2)
	results = []
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

#Creates State class
class State:

	states = []

	def __init__(self, name, ev, population, election16):
		self.name = str(name)
		if name == 'Maine':
			self.ev = int(ev) + 1
		else:
			self.ev = int(ev)
		self.population = int(population)
		self.election16 = {"D": int(election16[0]), "R": int(election16[1]), "Total": int(election16[2])}
		self.poll_rating = {}
		self.simulations = {}
		State.states.append(self)

	def __str__(self):
		return "{} has {} electoral votes and a population of {}".format(self.name, self.ev, self.population)

#Creates Pollster class
class Pollster:

	pollsters = []

	def __init__(self, name, grade, bias):
		self.name = str(name)
		self.grade = str(grade)
		self.bias = bias
		Pollster.pollsters.append(self)
	
	def __str__(self):
		return "{} has a grade of {} from 538 and a mean-reverted bias of {}+{}%.".format(self.name, self.grade, self.bias[0], self.bias[1])

#Create Poll class
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

	for state in states.keys():
		State(state, states[state]['2016']['EV'], states[state]['population'], (states[state]['2016']['D'], states[state]['2016']['R'], states[state]['2016']['Total']))

#Creates Pollster Objects
def create_pollsters(pollsters):

	#Checking if Pollster is Reputable, Then Instantiating Reference
	for pollster in pollsters:
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
	for pollster in Pollster.pollsters:
		for poll in new_polls:
			if pollster.name == poll['pollster']:
				Poll(poll['state'], poll['date'], pollster, poll['D'], poll['R'], poll['error'])

#Normalizes Polls with Pollster Ratings
def normalize():

	#Groups Polls by Pollster
	polls_by_pollster = {}

	for pollster in Pollster.pollsters:
		pollster_name = pollster.name
		polls_by_pollster[pollster] = []
		for poll in Poll.polls:
			poll_name = poll.pollster.name
			if pollster_name == poll_name:
				polls_by_pollster[pollster].append(poll)

	#Normalizes Polls according to Pollster grade and bias
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

#Aggregates Normalized Polls by State & Date into Single Rating
def aggregate():

	#Group Polls by State
	polls_by_state = {}

	for state in State.states:
		state_name = state.name
		polls_by_state[state] = []
		for poll in Poll.polls:
			poll_state = poll.state.name
			if state_name == poll_state:
				polls_by_state[state].append(poll)
	
	#Aggregating Polls into singular rating for each State
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
		key.poll_rating = rating

#Creates Distribution for both candidates in all States, Runs 10,000 simulations in each State
def simulate():

	margins = {}

	for state in State.states:

		simulations = {}

		n = state.election16['Total']
		e_poll = state.poll_rating['error']

		#Vote Percent in 2016
		d_16 = 100 * state.election16['D'] / n
		r_16 = 100 * state.election16['R'] / n

		#Poll Percent
		d_poll = state.poll_rating['D']
		r_poll = state.poll_rating['R']

		#Standard Deviations
		sigma_d = math.sqrt((d_poll - d_16)**2) + (e_poll / 100)
		sigma_r = math.sqrt((r_poll - r_16)**2) + (e_poll / 100)

		#Means
		mu_d = (d_16 + 2 * d_poll) / 3
		mu_r = (r_16 + 2 * r_poll) / 3

		#Distributions
		dist_d = np.random.normal(mu_d, sigma_d, 10000)
		dist_r = np.random.normal(mu_r, sigma_r, 10000)

		#Counting which candidate wins State what % of the time
		races_won_d = 0
		races_won_r = 0
		races = dist_d - dist_r
		for race in races:
			if race > 0:
				races_won_d += 1
			else:
				races_won_r += 1
		win_pct_d = round(100 * races_won_d / 10000, 2)
		win_pct_r = round(100 * races_won_r / 10000, 2)

		#Average Vote Share
		vote_pct_d = round(statistics.mean(dist_d), 2)
		vote_pct_r = round(statistics.mean(dist_r), 2)

		#Average Margin of Victory
		winner = 'Joe Biden' if vote_pct_d > vote_pct_r else 'Donald Trump'
		margin = round((vote_pct_d - vote_pct_r),2) if winner == 'Joe Biden' else round((vote_pct_r - vote_pct_d),2)

		#Storing Simulation
		simulations['win_pct_d'] = win_pct_d
		simulations['win_pct_r'] = win_pct_r
		simulations['vote_pct_d'] = vote_pct_d
		simulations['vote_pct_r'] = vote_pct_r
		simulations['margin'] = margin
		simulations['winner'] = winner

		state.simulations = simulations

		margins[state.name] = (margin, winner)

	return margins

#Visualizes the Model
def visualize(margins):

	fig, ax = plt.subplots()

	#Lambert Conformal map of lower 48 states.
	m = Basemap(llcrnrlon = -119, llcrnrlat = 20, urcrnrlon = -64, urcrnrlat = 49, projection = 'lcc', lat_1 = 33, lat_2 = 45, lon_0 = -95)

	#Mercator projection, for Alaska and Hawaii
	m_ = Basemap(llcrnrlon = -190, llcrnrlat = 20, urcrnrlon = -143, urcrnrlat = 46, projection = 'merc', lat_ts = 20)

	#Draw State Borders
	shp_info = m.readshapefile('st99_d00', 'states', drawbounds = True, linewidth = 0.45, color = 'gray')
	shp_info_ = m_.readshapefile('st99_d00','states', drawbounds = False)

	#Assign States a color based on their margins
	colors = {}
	statenames = []
	cmap_r = plt.cm.Reds
	cmap_d = plt.cm.Blues
	vmin = 0
	vmax = 20
	norm = Normalize(vmin = vmin, vmax = vmax)
	for shapedict in m.states_info:
		statename = shapedict['NAME']
		if statename != 'Puerto Rico':
			margin = margins[statename][0]
			winner = margins[statename][1]
			if winner == 'Joe Biden':
				colors[statename] = cmap_d(np.sqrt((margin - vmin) / (vmax - vmin)))[:3]
			else:
				colors[statename] = cmap_r(np.sqrt((margin - vmin) / (vmax - vmin)))[:3]
		statenames.append(statename)

	for nshape, seg in enumerate(m.states):
		if statenames[nshape] != 'Puerto Rico':
			color = rgb2hex(colors[statenames[nshape]])
			poly = Polygon(seg, facecolor = color, edgecolor = color)
			ax.add_patch(poly)

	#Resize and move Alaska and Hawaii
	AREA_1 = 0.005
	AREA_2 = AREA_1 * 30.0
	AK_SCALE = 0.19
	HI_OFFSET_X = -1900000
	HI_OFFSET_Y = 250000
	AK_OFFSET_X = -250000
	AK_OFFSET_Y = -750000

	for nshape, shapedict in enumerate(m_.states_info):
		if shapedict['NAME'] in ['Alaska', 'Hawaii']:
			seg = m_.states[int(shapedict['SHAPENUM'] - 1)]
			if shapedict['NAME'] == 'Hawaii' and float(shapedict['AREA']) > AREA_1:
				seg = [(x + HI_OFFSET_X, y + HI_OFFSET_Y) for x, y in seg]
				color = rgb2hex(colors[statenames[nshape]])
			elif shapedict['NAME'] == 'Alaska' and float(shapedict['AREA']) > AREA_2:
				seg = [(x*AK_SCALE + AK_OFFSET_X, y*AK_SCALE + AK_OFFSET_Y)\
					   for x, y in seg]
				color = rgb2hex(colors[statenames[nshape]])
			poly = Polygon(seg, facecolor=color, edgecolor='gray', linewidth=.45)
			ax.add_patch(poly)

	#Plot Bounding Boxes for Alaska and Hawaii
	light_gray = [0.8]*3
	x1,y1 = m_([-190,-183,-180,-180,-175,-171,-171],[29,29,26,26,26,22,20])
	x2,y2 = m_([-180,-180,-177],[26,23,20])
	m_.plot(x1,y1,color=light_gray,linewidth=0.8)
	m_.plot(x2,y2,color=light_gray,linewidth=0.8)

	plt.savefig('results/map.png')

#Output CSV files with result data
def write_results():

	#Create HTML Table for States with closest projected margins
	closest_margins = []
	closest_margins_fields = ['State', 'Projected Margin', 'Projected Winner']
	closest_margins.append(closest_margins_fields)
	closest_margins_rows = []
	for state in State.states:
		row = []
		if state.simulations['margin'] < 10:
			row.append(state.name)
			row.append(state.simulations['margin'])
			row.append(state.simulations['winner'])
			closest_margins_rows.append(row)
	closest_margins_rows = sorted(closest_margins_rows, key=lambda row: row[1])
	for row in closest_margins_rows:
		row[1] = str(row[1]) + '%'
	for i in range(len(closest_margins_rows)):
		closest_margins.append(closest_margins_rows[i])

	#Create HTML Table
	cols = ["<td>{0}</td>".format( "</td><td>".join(t)) for t in closest_margins]
	rows = "<tr>{0}</tr>".format( "</tr>\n<tr>".join(cols))
	file = open("tables/closest_margins.html", 'r+')
	file.truncate(0)
	file.close()
	file = open("tables/closest_margins.html", 'w')
	file.write("""<HTML> <body>
                    	<h2>Closest Projected Margins of Victory</h2>
                            <table>
                              {0}  
                            </table>
                        </body>  
                  </HTML>""".format(rows))
	file.close()

	#Create HTML Table for States with the most lopsided margins
	lopsided_margins = []
	lopsided_margins_fields = ['State', 'Projected Margin', 'Projected Winner']
	lopsided_margins.append(lopsided_margins_fields)
	lopsided_margins_rows = []
	for state in State.states:
		row = []
		if state.simulations['margin'] > 25:
			row.append(state.name)
			row.append(state.simulations['margin'])
			row.append(state.simulations['winner'])
			lopsided_margins_rows.append(row)
	lopsided_margins_rows = sorted(lopsided_margins_rows, key=lambda row: row[1], reverse = True)
	for row in lopsided_margins_rows:
		row[1] = str(row[1]) + '%'
	for i in range(len(lopsided_margins_rows)):
		lopsided_margins.append(lopsided_margins_rows[i])

	#Create HTML Table
	cols = ["<td>{0}</td>".format( "</td><td>".join(t)) for t in lopsided_margins]
	rows = "<tr>{0}</tr>".format( "</tr>\n<tr>".join(cols))
	file = open("tables/lopsided_margins.html", 'r+')
	file.truncate(0)
	file.close()
	file = open("tables/lopsided_margins.html", 'w')
	file.write("""<HTML> <body>
                    	<h2>Most Lopsided Projected Margins of Victory</h2>
                            <table>
                              {0}  
                            </table>
                        </body>  
                  </HTML>""".format(rows))
	file.close()

	#Create HTML Table for tossup States
	tossups = []
	tossups_fields = ['State', 'Trump Projected Chance', 'Biden Projected Chance']
	tossups.append(tossups_fields)
	tossups_rows = []
	for state in State.states:
		row = []
		chance_d = state.simulations['win_pct_d']
		chance_r = state.simulations['win_pct_r']
		if 40 < chance_d < 60 and 40 < chance_r < 60:
			row.append(state.name)
			row.append(chance_r)
			row.append(chance_d)
			tossups_rows.append(row)
	tossups_rows = sorted(tossups_rows, key=lambda row: math.fabs(row[1] - row[2]))
	for row in tossups_rows:
		row[1] = str(row[1]) + '%'
		row[2] = str(row[2]) + '%'
	for i in range(len(tossups_rows)):
		tossups.append(tossups_rows[i])
	
	#Create HTML Table
	cols = ["<td>{0}</td>".format( "</td><td>".join(t)) for t in tossups]
	rows = "<tr>{0}</tr>".format( "</tr>\n<tr>".join(cols))
	file = open("tables/tossups.html", 'r+')
	file.truncate(0)
	file.close()
	file = open("tables/tossups.html", 'w')
	file.write("""<HTML> <body>
                    	<h2>Projected Tossup States</h2>
                            <table>
                              {0}  
                            </table>
                        </body>  
                  </HTML>""".format(rows))
	file.close()

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

	#Creates Distribution for both candidates in all States, Runs 10,000 simulations in each State
	margins = simulate()

	#Visualizes the Model
	visualize(margins)

	#Output CSV files with result data
	write_results()

if __name__ == "__main__":
	model()