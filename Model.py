#The actual predictive model exists in this file
import Scraper
import Objects
import numpy as np
import pandas as pd

##Data for State objects
state_data = Scraper.csv_scrape("state_data.csv")
for index, row in state_data.iterrows():
	Objects.State(row["state"],
    	  row["abbrev"],
    	  row["ev"],
    	  row["population"],
    	  [row["d16"],row["r16"],row["total16"]],
    	  [row["pvi"],row["pvi_party"],row["pvi_margin"]],
    	  row["turnout"])

pollster_data = Scraper.csv_scrape("pollster_data.csv")
for index, row in pollster_data.iterrows():
	Objects.Pollster()