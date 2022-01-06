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
	names = []
	links = []

	for item in sankeys:
		justName = item.split(".")[0]
		names.append(justName.split(" - ")[1])
		justName = item.replace(" ", "%20")
		link = "https://kcpdclearance.firebaseapp.com/KCPDClearance/"+justName
		links.append(link)

	dataFrame = pd.DataFrame()
	dataFrame['Category'] = names
	dataFrame['Link'] = links
	dataFrame.to_csv("KCPDClearanceDirectory.csv", index = False)

#def countSplitCases():



def clearanceDashboardRunner():
	
	#dataGatherer()
	karpelCases = karpelStarter()
	kcpdCases = dataCleaner(karpelCases)
	chargeCategories = pd.read_excel("FBI NIBRS Offense Codes.xlsx")
	chargeCategories = chargeCategories[chargeCategories['Felony'] == "Yes"]
	crimeCategoriesList = list(set(chargeCategories['Category'].tolist()))

	for crimeCategory in crimeCategoriesList:

		print(crimeCategory)
		tempDF = kcpdCases[kcpdCases['Category'].astype(str).str.contains(crimeCategory)==True]
		numberOfIncidents = len(tempDF.index)
		tempDF = tempDF.dropna(subset = ['File #'])

		#Count Number of Non-Nulls (Number of Cases with at Least 1 Received Defendant)
		atLeast1ReferredCase = len(tempDF.index)

		receivedFileNumbers = list(set(itertools.chain.from_iterable(tempDF['File #'].apply(list).tolist())))

		if receivedFileNumbers == 0 or len(tempDF.index) == 0:
			continue

		generateAllCaseHistory(crimeCategory, numberOfIncidents, atLeast1ReferredCase, receivedFileNumbers, karpelCases)

	numberOfIncidents = len(kcpdCases.index)
	kcpdCases = kcpdCases.dropna(subset = ['File #'])
	atLeast1ReferredCase = len(kcpdCases.index)
	listOfFNs = list(set(itertools.chain.from_iterable(kcpdCases['File #'].apply(list).tolist())))

	generateAllCaseHistory("All", numberOfIncidents, atLeast1ReferredCase, listOfFNs, karpelCases)
	generateCSV()

clearanceDashboardRunner()