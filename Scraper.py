#Will use state_data.csv, other csv files, and websites to compile all the data needed for the model

import numpy as np
import pandas as pd

def csv_scrape(file):
	data = pd.read_csv(file)
	return data