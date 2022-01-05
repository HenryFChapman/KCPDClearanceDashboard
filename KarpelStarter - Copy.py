import pandas as pd 
import os
from openpyxl import load_workbook
import sys, os

#This gets the latest date (or most recent file) from the Karpel Weekly Data Drop
def getNewestFile(weeklyUpload):

	#Initializes Blank List 
	allDates = []

	#Loops through the Weekly Data Drop Folder
	for item in os.listdir(weeklyUpload):

		#Pulls the Date from Each File in the Folder
		date = int(item.split("_")[1])

		#Appends it to a list
		allDates.append(date)

	#Removes all the duplicates
	allDates = list(set(allDates))

	#Sorts the List without Duplicates
	allDates.sort()

	#Grabs the most recent file
	mostRecent = str(allDates[-1])

	#Returns that most recent file. 
	return mostRecent

#This loads the most recent file. It renames columns so they are all standard accross the three types of case categories.
#It also consolidates every address column into one address
def loadMostRecentFile(newestFile, weeklyUpload):

	#Loads Weekly Upload Folder
	directoryList = os.listdir(weeklyUpload)

	#Sorts Folder So Newest Are Up Front
	directoryList.sort(reverse=True)

	i = 0
	updatedCompleteDFs = []
	fixedRowlabels = pd.ExcelFile('FixedRowLabels.xlsx')

	#Loops Through Weekly Upload Directory
	for item in directoryList:

		#Checking if it's the most recent file (Received,Disposed,Filed)
		#Change Here When Adding Case Dispositions
		if newestFile in item and ("Disp" in item or "Rcvd" in item or "Fld" in item) and ("_1800" in item):

			#Load the Most Recent File as a DataFrame
			tempUpdatedDF = pd.read_csv(weeklyUpload + item)

			#Fix the Misspelled/Incorrect Column Headers/Standardize Column Headers
			fixedRowLabel = pd.read_excel(fixedRowlabels, sheet_name = fixedRowlabels.sheet_names[i])
			fixedRowLabelDict = pd.Series(fixedRowLabel['New Name'].values,index=fixedRowLabel['Original Name']).to_dict()
			tempUpdatedDF = tempUpdatedDF.rename(columns=fixedRowLabelDict)

			#Concatenates Address Field into One Field, and drops the old fields that we don't need. 
			tempUpdatedDF["Def. Street Address"] = tempUpdatedDF["Def. Street Address"].fillna('').astype(str) + ", " + tempUpdatedDF["Def. Street Address2"].fillna('').astype(str) + ", " + tempUpdatedDF["Def. City"].fillna('').astype(str) + ", " + tempUpdatedDF["Def. State"].fillna('').astype(str) + ", " + tempUpdatedDF["Def. Zipcode"].fillna('').astype(str)
			tempUpdatedDF["Offense Street Address"] = tempUpdatedDF["Offense Street Address"].fillna('').astype(str) + ", " + tempUpdatedDF["Offense Street Address 2"].fillna('').astype(str) + ", " + tempUpdatedDF["Offense City"].fillna('').astype(str) + ", " + tempUpdatedDF["Offense State"].fillna('').astype(str) + ", " + tempUpdatedDF["Off. Zipcode"].fillna('').astype(str)
			tempUpdatedDF = tempUpdatedDF.drop(columns=["Def. Street Address2", "Def. City", "Def. State", "Def. Zipcode", "Offense Street Address 2", "Offense City", "Offense State", "Off. Zipcode", "Def. SSN"])

			updatedCompleteDFs.append(tempUpdatedDF)
			i = i + 1

	return updatedCompleteDFs

def loadKarpelCases(directory, mostRecent):
	karpelDataFrames = []

	#Old Received Cases
	oldReceivedCases = pd.read_csv("RawData\\1 - Received.csv")
	oldReceivedCases = oldReceivedCases[oldReceivedCases['Year']!=2022]
	oldReceivedCases = oldReceivedCases[['File #', "CRN", "Agency", "Enter Dt.", "Def. Name", "Def. Sex", "Def. Race", "Def. DOB", "Ref. Charge Code", "Ref. Charge Description"]]

	#New Received Cases
	receivedCases = pd.read_csv(directory + "Rcvd_"+mostRecent+"_1800.CSV", encoding='utf-8')

	receivedCases = receivedCases.rename({'Def  Name': 'Def. Name', 'Enter Dt ': 'Enter Dt.', 'Def  DOB': "Def. DOB", "Def  Race":"Def. Race", "Def Sex":"Def. Sex", "Ref  Charge":"Ref. Charge Code", "Ref  Charge Desctiption": "Ref. Charge Description"}, axis=1) 
	receivedCases = receivedCases[['File #', "CRN", "Agency", "Enter Dt.","Def. Name", "Def. Race", "Def. Sex", "Def. DOB", "Ref. Charge Code", "Ref. Charge Description"]]
	
	oldReceivedCases = oldReceivedCases.append(receivedCases)
	oldReceivedCases = oldReceivedCases[oldReceivedCases['Agency'] == 2]
	oldReceivedCases = oldReceivedCases.dropna(subset = ["CRN"])
	oldReceivedCases['CRN'] = oldReceivedCases['CRN'].astype(str).str.replace(r'\D+', '').str[:2] + "-" + oldReceivedCases['CRN'].astype(str).str.replace(r'\D+', '').str[2:].astype('int64').astype(str)
	karpelDataFrames.append(oldReceivedCases)

	#Old Filed Cases
	oldFiledCases = pd.read_csv("RawData\\2 - Filed.csv")
	oldFiledCases = oldFiledCases[oldFiledCases['Year']!=2022]
	oldFiledCases = oldFiledCases[['File #', "CRN", "Agency", "Enter Dt.", "Filing Dt.", "Def. Name", "Def. Sex", "Def. Race", "Def. DOB", "Ref. Charge Code", "Ref. Charge Description"]]

	#New Filed Cases
	filedCases = pd.read_csv(directory + "Fld_" + mostRecent + "_1800.CSV", encoding='utf-8')
	filedCases = filedCases.rename(columns={'Def  Name': 'Def. Name', 'Enter Dt ': 'Enter Dt.', 'Def  DOB': "Def. DOB", "Def  Race":"Def. Race", "Def Sex":"Def. Sex", "Ref. Charge":"Ref. Charge Code", "Ref. Charge Desctiption": "Ref. Charge Description", 'Filing Date.': 'Filing Dt.'})
	filedCases = filedCases[['File #', "CRN", "Agency", "Enter Dt.", "Filing Dt.", "Def. Name", "Def. Sex", "Def. Race", "Def. DOB", "Ref. Charge Code", "Ref. Charge Description"]]
	oldFiledCases = oldFiledCases.append(filedCases)
	oldFiledCases = oldFiledCases[oldFiledCases['Agency'] == 2]
	karpelDataFrames.append(oldFiledCases)

	#Old Disposed Cases
	oldDisposedCases = pd.read_csv("RawData\\3 - Disposed.csv")
	oldDisposedCases = oldDisposedCases[oldDisposedCases['Year']!=2022]
	oldDisposedCases = oldDisposedCases[["File #", "CRN","Agency", "Disp. Dt.", "Enter Dt.",  "Ref. Charge Code", "Ref. Charge Description", "Disp. Code", ]]

	#New Disposed Cases
	disposedCases = pd.read_csv(directory + "Disp_"+mostRecent+"_1800.CSV", encoding='utf-8')
	disposedCases = disposedCases.rename(columns={'Def  Name': 'Def. Name', 'Enter Dt ': 'Enter Dt.', 'Def  DOB': "Def. DOB", "Def  Race":"Def. Race", "Def Sex":"Def. Sex", "Charge Code":"Ref. Charge Code", "Charge Desctiption": "Ref. Charge Description", 'Filing Date.': 'Filing Dt.'})
	disposedCases = disposedCases[["File #", "CRN", "Agency", "Disp. Dt.", "Enter Dt.",  "Ref. Charge Code", "Ref. Charge Description", "Disp. Code", ]]
	oldDisposedCases = oldDisposedCases.append(disposedCases)
	
	dispositionReasons = pd.read_csv("Disposition Codes.csv")
	oldDisposedCases = oldDisposedCases.merge(dispositionReasons, on = "Disp. Code", how = 'left')
	oldDisposedCases = oldDisposedCases[oldDisposedCases['Agency'] == 2]

	karpelDataFrames.append(oldDisposedCases)

	#Old Refused Cases
	oldRefusedCases = pd.read_csv("RawData\\4 - Refused.csv")
	oldRefusedCases = oldRefusedCases[oldRefusedCases['Year']!=2022]
	disposedCases = disposedCases.rename(columns={'Def  Name': 'Def. Name', 'Enter Dt ': 'Enter Dt.', 'Def  DOB': "Def. DOB", "Def  Race":"Def. Race", "Def Sex":"Def. Sex", "Charge Code":"Ref. Charge Code", "Charge Desctiption": "Ref. Charge Description", 'Filing Date.': 'Filing Dt.'})
	oldRefusedCases = oldRefusedCases[["File #", "CRN", "Disp. Code", "Disp. Dt.", "Agency", "Enter Dt.", 'Ref. Charge Code', 'Ref. Charge Description', ]]

	#New Refused Cases
	notFiledCases = pd.read_csv(directory + "Ntfld_"+mostRecent+"_1800.csv")
	notFiledCases = notFiledCases.rename(columns={'Def  Name': 'Def. Name', 'Enter Dt ': 'Enter Dt.', 'Def  DOB': "Def. DOB", "Def  Race":"Def. Race", "Def Sex":"Def. Sex", "Charge Code":"Ref. Charge Code", "Ref.Charge Desctiption": "Ref. Charge Description", 'Filing Date.': 'Filing Dt.'})
	notFiledCases = notFiledCases[["File #", "CRN", "Disp. Code", "Disp. Dt.", "Agency", "Enter Dt.", 'Ref. Charge Code', 'Ref. Charge Description', ]]
	oldRefusedCases = oldRefusedCases.append(notFiledCases)

	refusalReasons = pd.read_csv("RefusalReasons.csv", encoding = 'utf-8')
	oldRefusedCases = oldRefusedCases.merge(refusalReasons, on = 'Disp. Code', how = 'left')
	#oldRefusedCases = oldRefusedCases[["File #", "CRN", "Reason",  "Disp. Dt.", "Agency", "Enter Dt.", "Ref. Charge Code", "Ref. Charge Description"]]
	oldRefusedCases = oldRefusedCases.rename(columns = {'Reason':'Disp. Code'})
	oldRefusedCases = oldRefusedCases[oldRefusedCases['Agency'] == 2]

	karpelDataFrames.append(oldRefusedCases)

	return karpelDataFrames


def karpelStarter():
	weeklyUpload = "H:\\Units Attorneys and Staff\\01 - Units\\DT Crime Strategies Unit\\Weekly Update\\"
	newestFile = getNewestFile(weeklyUpload)
	updatedDFs = loadKarpelCases(weeklyUpload, newestFile)

	return updatedDFs
