from KarpelStarter import karpelStarter
from dataGatherer import dataGatherer
from dataCleaner import dataCleaner
from caseHistoryGenerator import generateAllCaseHistory
import pandas as pd
import itertools
import os
import shutil

def generateCSV():

	sankeys = os.listdir("Sankeys\\KCPDClearance\\")

	years = []
	categories = []
	links = []

	for item in sankeys:

		justName = item.split(".")[0]
		justName = justName.split(" - ")
		year = justName[1]
		years.append(year)
		category = justName[2]
		categories.append(category)

		justName = item.replace(" ", "%20")
		link = "https://kcpdclearance.firebaseapp.com/KCPDClearance/"+justName
		links.append(link)

	dataFrame = pd.DataFrame()
	dataFrame['Year'] = years
	dataFrame['Category'] = categories
	dataFrame['Link'] = links

	#Replacing All with *All
	dataFrame.loc[(dataFrame.Category == 'Overall Referrals'),'Category']='*Overall Referrals'

	dataFrame.to_csv("KCPDClearanceDirectory.csv", index = False)

def clearanceDashboardRunner():
	
	dataGatherer()
	karpelCases = karpelStarter()
	kcpdCases = dataCleaner(karpelCases)
	chargeCategories = pd.read_excel("FBI NIBRS Offense Codes.xlsx")
	chargeCategories = chargeCategories[chargeCategories['Felony'] == "Yes"]
	crimeCategoriesList = list(set(chargeCategories['Category'].tolist()))

	listOfYears = list(set(kcpdCases['Year'].tolist()))
	categoriesToInclude = ['Fraud', 'Homicide', 'Assault', 'Robbery', 'Burglary', 'Arson', 'Drugs', 'Embezzlement',
							'Family Offenses', 'Forgery', 'Kidnapping or Abduction', 'Motor Vehicle Theft', 'Sex Offenses', 'Weapons Law Violations']

	for crimeCategory in crimeCategoriesList:

		if crimeCategory not in categoriesToInclude:
			continue

		tempCategory = kcpdCases[kcpdCases['Category'].astype(str).str.contains(crimeCategory)==True]
	
		for year in listOfYears:			
			tempDF = tempCategory[tempCategory['Year'] == year]
			numberOfIncidents = len(tempDF.index)
			tempDF = tempDF.dropna(subset = ['File #'])

			#Count Number of Non-Nulls (Number of Cases with at Least 1 Received Defendant)
			atLeast1ReferredCase = len(tempDF.index)

			receivedFileNumbers = list(set(itertools.chain.from_iterable(tempDF['File #'].apply(list).tolist())))

			if receivedFileNumbers == 0 or len(tempDF.index) == 0:
				continue

			tempTitle = str(year) + " - " + crimeCategory
			generateAllCaseHistory(tempTitle, numberOfIncidents, atLeast1ReferredCase, receivedFileNumbers, karpelCases)

		numberOfIncidents = len(tempCategory.index)
		tempCategory = tempCategory.dropna(subset = ['File #'])
		atLeast1ReferredCase = len(tempCategory.index)
		listOfFNs = list(set(itertools.chain.from_iterable(tempCategory['File #'].apply(list).tolist())))

		generateAllCaseHistory("All - " + crimeCategory, numberOfIncidents, atLeast1ReferredCase, listOfFNs, karpelCases)

	for year in listOfYears:
		tempDF = kcpdCases[kcpdCases['Year']==year]
		numberOfIncidents = len(tempDF.index)
		tempDF = tempDF.dropna(subset = ['File #'])

		#Count Number of Non-Nulls (Number of Cases with at Least 1 Received Defendant)
		atLeast1ReferredCase = len(tempDF.index)

		receivedFileNumbers = list(set(itertools.chain.from_iterable(tempDF['File #'].apply(list).tolist())))

		if receivedFileNumbers == 0 or len(tempDF.index) == 0:
			continue

		tempTitle = str(year) + " - Overall Referrals"
		generateAllCaseHistory(tempTitle, numberOfIncidents, atLeast1ReferredCase, receivedFileNumbers, karpelCases)


	numberOfIncidents = len(kcpdCases.index)
	kcpdCases = kcpdCases.dropna(subset = ['File #'])
	atLeast1ReferredCase = len(kcpdCases.index)
	listOfFNs = list(set(itertools.chain.from_iterable(kcpdCases['File #'].apply(list).tolist())))

	generateAllCaseHistory("All - Overall Referrals", numberOfIncidents, atLeast1ReferredCase, listOfFNs, karpelCases)


clearanceDashboardRunner()

generateCSV()
