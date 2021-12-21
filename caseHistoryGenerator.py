import pandas as pd 
from KarpelStarter import karpelStarter
import plotly.graph_objects as go

#Under Review - Subtract (Received - Filed - Not Filed = Under Review)

#Currently Pending/Under Warrant Status (Filed - Disposed = Currently Pending/Under Warrant Status)
#Disposed = Count How Many of Those File Fumbers Appear in Disposed Cases

listOfFNs = list(set(pd.read_excel("testCases.xlsx")['File #'].tolist()))
listOfKarpelCases = karpelStarter()

def generateCaseHistory(receivedFileNumbers, listOfKarpelCases):

	#Received - Count Unique File Numbers - Number of Received Cases
	print("Received Cases: " + str(len(receivedFileNumbers)))

	#Filed - Count How Many of Those File Numbers Appear in Filed
	filedSet = set(listOfKarpelCases[1]['File #'].tolist())
	filedFileNumbers = filedSet.intersection(receivedFileNumbers)
	print("Filed Cases: " + str(len(filedFileNumbers)))

	#Not Filed - Count How Many of Those File Numbers Appear in Not-Filed
	declinedSet = set(listOfKarpelCases[3]['File #'].tolist())
	declinedFileNumbers = declinedSet.intersection(receivedFileNumbers)
	declinedFileNumbers = declinedFileNumbers.difference(filedSet)
	print("Declined Cases: " + str(len(declinedFileNumbers)))

	#Under Review = Received - Filed - Not Filed
	reviewSet = set(receivedFileNumbers).difference(filedSet).difference(declinedFileNumbers)
	print("Cases Under Review: " + str(len(reviewSet)))

	#Disposed Cases
	disposedSet = set(listOfKarpelCases[2]['File #'].tolist())
	disposedFileNumbers = disposedSet.intersection(receivedFileNumbers)
	disposedFileNumbers = list(disposedSet.intersection(filedFileNumbers))
	print("Disposed Cases: " + str(len(disposedFileNumbers)))

	#Currently Pending/Under Warrant Status
	#Currently Pending = Filed - Disposed
	activeSet = set(filedFileNumbers).difference(disposedFileNumbers)
	print("Currently Active Cases: " + str(len(activeSet)))

	#Review Position
	reviewPos = len(reviewSet)/len(receivedFileNumbers)
	declinePos = reviewPos - len(declinedFileNumbers)/len(receivedFileNumbers)
	filedPos = declinePos - len(filedFileNumbers)/len(receivedFileNumbers)
	activePos = filedPos - len(activeSet)/len(receivedFileNumbers)
	disposedPos = len(declinedFileNumbers)/len(receivedFileNumbers)

	yPositions = []

	fig = go.Figure(data=[go.Sankey(
	arrangement = "snap",
	node = dict(
	  pad = 15,
	  thickness = 20,
	  line = dict(color = "black", width = 0.5),
	  label = ["Received", "Declined", "Under Review", "Filed", "Case Active", "Disposed"],
	  x = [0, 0.2, 0.2, 0.2, 0.4, 0.6],
	  #y = [0,0,0,0,0,0],
	  y = [0, reviewPos, declinePos, filedPos, activePos],
	  color = "blue"
	),
	link = dict(
	  source = [0, 0, 0, 3, 3], # indices correspond to labels, eg A1, A2, A1, B1, ...
	  target = [1, 2, 3, 4, 5],
	  value = [len(declinedFileNumbers), len(reviewSet), len(filedFileNumbers), len(activeSet), len(disposedFileNumbers)]
	))])

	fig.update_layout(title_text="Basic Sankey Diagram", font_size=10)
	fig.write_html("TestOutput.html")


generateCaseHistory(listOfFNs, listOfKarpelCases)