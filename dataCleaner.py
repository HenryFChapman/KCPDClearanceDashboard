import pandas as pd 
import os 

def dataCleaner(karpelCases):

	chargeCategories = pd.read_excel("FBI NIBRS Offense Codes.xlsx")
	crimeDataDirectory = "Raw Crime Data\\"

	allCleanData = []

	#yearDictionary = dict()

	for item in os.listdir(crimeDataDirectory):

		df = pd.read_csv(crimeDataDirectory+item, low_memory=False)
		#df['ibrs'] = df['ibrs'].astype(str)

		#Isolate Patrol Zones that we want 
		df = df[(df['area'] == 'EPD') | (df['area'] == 'MPD') | (df['area'] == 'CPD') | (df['area'] == 'SPD')]

		#Drop NA Codes
		df = df.dropna(subset = ['ibrs'])
		df['ibrs'] = df['ibrs'].astype(str)

		#Convert Report Number/Remove Leading Zeroes on Codes
		#1. Remove non-numeric characters
		#2. Convert to string
		#3. Cut off year (first two characters)
		#4. Convert to integer
		df['CRN'] = df['report_no'].astype(str).str.replace(r'\D+', '').str[:2] + "-" + df['report_no'].astype(str).str.replace(r'\D+', '').str[2:].astype('int64').astype(str)

		df = df[['CRN', 'reported_date', 'reported_time', 'offense', 'ibrs', 'description', 'address', 'city', 'zip_code', 'area', 'dvflag', 'involvement', 'race', 'sex', 'firearm_used_flag', 'age', 'location']]		
		df = df.merge(chargeCategories.astype(str), on = "ibrs", how = 'left')

		#Filter Just Felony Categories
		df = df[df['Felony']=="Yes"]

		incidents = df.groupby('CRN')['Category'].apply(set).to_frame().reset_index()

		referredFileNumbers = karpelCases[0].groupby('CRN')['File #'].apply(set).to_frame().reset_index()
		incidents = incidents.merge(referredFileNumbers, on = 'CRN', how = 'left')

		allCleanData.append(incidents)

		#year = item.split("-")[1].split(".")[0]

		#yearDictionary.update({year:incidents})

	allCleanData = pd.concat(allCleanData)

	return allCleanData