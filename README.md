#2020election

The goal of this project is to create a state-by-state predictive model for the 2020 United States presidential election.

PollScraper.py will scrape information about presidential election polls for each state from https://projects.fivethirtyeight.com/polls/.
This data will include the date the poll was released, the name of the pollster, the sample size, and the percentage for each candidate.

PollsterScraper.py will scrap information about pollsters from https://projects.fivethirtyeight.com/pollster-ratings/
This data will include the name of the pollster, 538 rating of the pollster and each pollsters mean-reverted bias.

StateScraper.py will use a number of csv files and websites to compile information about all 50 U.S. states and the District of Columbia.
This data will include past presidential election data, demographic data, Cook PVI ratings, and basic facts about each state.

Poll.py will create object instances of each poll that we scrape from PollScraper.py and will add them to dictionaries that sort them by Pollster and by State.

Pollster.py will create object instances of each pollster that we scrape from PollsterScraper.py and will add them to a list of pollsters.
This class will contain a method that calculates the discrepancy between the pollster's polls and the results of the 2016 election.

State.py will create object instances of each state and the District of Columbia from the data that is collected in StateScraper.py and will add them to a list of states.
This class will contain a method that calculates the changes in demographics from 2016 to 2020 and estimate the change in partisan composition due to those changes.
This class will contain a method that takes into account 2016 election results, demographic trends, 2016 polling discrepancies, 2020 polls, Cook PVI ratings, historical turnout numbers, and other factors to create a prediction of the results of the 2020 presidential election in that state.

Visualizer.py will create a window that displays a map with data for each state and predictive data that we generate later.

Model.py will use all of the previously mentioned files to create a solid prediction of the outcome of the 2020 United States presidential election.
This file will contain a function using random numbers in certain ranges to simulate 10,000 elections in each state, to generate a statistical data representing how often each candidate wins, and the average vote share to create a prediction for the national election.