import os
import pandas as pd
import numpy as np
from sodapy import Socrata

def dataGatherer():

	with open("authKeys.txt") as f:
		lines = f.readlines()

	keyID = lines[0].split(":")[1].split("\n")[0]
	keySecret = lines[1].split(":")[1]

	kcpdDataDictionary = {2017:"98is-shjt", 2018:"dmjw-d28i", 2019:"pxaa-ahcm", 2020:"vsgj-uufz", 2021:"w795-ffu6", 2022:"x39y-7d3m"}

	client = Socrata("data.kcmo.org","W4eVE8n4fpyTw7QMpZFbr6qWJ",username=keyID,password=keySecret)

	for year in kcpdDataDictionary.keys():
		results = client.get(kcpdDataDictionary.get(year), limit = 300000)
		df = pd.DataFrame.from_dict(results)

		df = df.rename(columns={'location_1': 'location', 'report_date':'reported_date', 'firearmused_flag':'firearm_used_flag', 'firearmusedflag': 'firearm_used_flag','report_time':'reported_time' })

		df.to_csv("Raw Crime Data\\KCPD-" + str(year) + ".csv", index = False)
