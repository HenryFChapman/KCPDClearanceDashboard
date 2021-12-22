from KarpelStarter import karpelStarter
from dataGatherer import dataGatherer
from dataCleaner import dataCleaner
from caseHistoryGenerator import generateAllCaseHistory
import pandas as pd
import itertools


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

	listOfFNs = list(set(itertools.chain.from_iterable(tempDF['File #'].apply(list).tolist())))

	if listOfFNs == 0 or len(tempDF.index) == 0:
		continue

	generateAllCaseHistory(crimeCategory, numberOfIncidents, listOfFNs, karpelCases)

numberOfIncidents = len(kcpdCases.index)
kcpdCases = kcpdCases.dropna(subset = ['File #'])
listOfFNs = list(set(itertools.chain.from_iterable(kcpdCases['File #'].apply(list).tolist())))


generateAllCaseHistory("All", numberOfIncidents, listOfFNs, karpelCases)