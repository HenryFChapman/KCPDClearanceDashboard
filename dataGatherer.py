import os
import pandas as pd
import numpy as np
from sodapy import Socrata


def dataGatherer():
	#API Key ID : 7hhuc5nwifgpr7kwbxktaftlu
	#API Key Secret: 5tt36r2dh4ltvwxsw5i65uk21dc76xzmfkbumummr63z3sgvnb

	kcpdDataDictionary = {2017:"98is-shjt", 2018:"dmjw-d28i", 2019:"pxaa-ahcm", 2020:"vsgj-uufz", 2021:"w795-ffu6"}

	client = Socrata("data.kcmo.org","W4eVE8n4fpyTw7QMpZFbr6qWJ",username="7hhuc5nwifgpr7kwbxktaftlu",password="5tt36r2dh4ltvwxsw5i65uk21dc76xzmfkbumummr63z3sgvnb")

	for year in kcpdDataDictionary.keys():
		results = client.get(kcpdDataDictionary.get(year), limit = 300000)
		df = pd.DataFrame.from_dict(results)

		df = df.rename(columns={'location_1': 'location', 'report_date':'reported_date', 'firearmused_flag':'firearm_used_flag', 'report_time':'reported_time' })

		df.to_csv("Raw Crime Data\\KCPD-" + str(year) + ".csv", index = False)
