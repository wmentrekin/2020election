#The actual predictive model exists in this file
import Scraper
import State
import numpy as np
import pandas as pd

##Data for State objects
state_data = Scraper.state_scrape("state_data.csv")
for index, row in state_data.iterrows():
	State.State(row["state"],
    	  row["abbrev"],
    	  row["ev"],
    	  row["population"],
    	  [row["d16"],row["r16"],row["total16"]],
    	  [row["pvi"],row["pvi_party"],row["pvi_margin"]],
    	  row["demographics"],
    	  row["registration"],
    	  row["turnout"])
for state in State.State.states:
	print(state)