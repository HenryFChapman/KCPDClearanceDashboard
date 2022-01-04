import pandas as pd 
from KarpelStarter import karpelStarter
import plotly.graph_objects as go
import numpy as np
from DispositionCounter import disposedCaseCounter, declinedCaseCounter

def factorize(s):
    a = pd.factorize(s, sort=True)[0]
    return (a + 0.01) / (max(a) + 0.1)


def reasonsToNodes(reasonDF, links):

	reasonDictionaries = reasonDF.to_dict(orient = 'records')
	#print(reasonDictionaries)

	links.extend(reasonDictionaries)

	return links

def generateAllCaseHistory(crimeCategory, numberOfIncidents, receivedFileNumbers, listOfKarpelCases):

	#print("Number of Incidents: " + str(numberOfIncidents))

	numberNotReferred = numberOfIncidents-len(receivedFileNumbers)
	#print("Number Not Referred: " + str(numberNotReferred))

	#Received - Count Unique File Numbers - Number of Received Cases
	#print("Received Cases: " + str(len(receivedFileNumbers)))

	#Filed - Count How Many of Those File Numbers Appear in Filed
	filedSet = set(listOfKarpelCases[1]['File #'].tolist())
	filedFileNumbers = filedSet.intersection(receivedFileNumbers)

	#Not Filed - Count How Many of Those File Numbers Appear in Not-Filed
	declinedSet = set(listOfKarpelCases[3]['File #'].tolist())
	declinedFileNumbers = declinedSet.intersection(receivedFileNumbers)
	declinedFileNumbers = declinedFileNumbers.difference(filedSet)
	declineReasons = declinedCaseCounter(declinedFileNumbers, listOfKarpelCases[3])

	#Under Review = Received - Filed - Not Filed
	reviewSet = set(receivedFileNumbers).difference(filedSet).difference(declinedFileNumbers)

	#Disposed Cases
	disposedSet = set(listOfKarpelCases[2]['File #'].tolist())
	disposedFileNumbers = disposedSet.intersection(receivedFileNumbers)
	disposedFileNumbers = list(disposedSet.intersection(filedFileNumbers))
	disposalReasons = disposedCaseCounter(disposedFileNumbers, listOfKarpelCases[2])
	#print(disposalReasons.head())

	#Currently Pending/Under Warrant Status
	#Currently Pending = Filed - Disposed
	activeSet = set(filedFileNumbers).difference(disposedFileNumbers)

	#Review Position
	reviewPos = len(reviewSet)/len(receivedFileNumbers)
	declinePos = reviewPos - len(declinedFileNumbers)/len(receivedFileNumbers)
	filedPos = declinePos - len(filedFileNumbers)/len(receivedFileNumbers)
	activePos = filedPos - len(activeSet)/len(receivedFileNumbers)
	disposedPos = len(declinedFileNumbers)/len(receivedFileNumbers)

	links = [
		{'source': 'A - Incidents Occured', 'target':'B - Received by Office', 'value': len(receivedFileNumbers)},
		{'source': 'A - Incidents Occured', 'target':'B - Not Received By Office', 'value':numberNotReferred},
		{'source': 'B - Received by Office', 'target':'C - Declined', 'value':len(declinedFileNumbers)},
		{'source': 'B - Received by Office', 'target':'C - Under Review', 'value':len(reviewSet)},
		{'source': 'B - Received by Office', 'target':'C - Cases Filed', 'value':len(filedFileNumbers)},
		{'source': 'C - Cases Filed', 'target':'D - Case Active', 'value':len(activeSet)},
		{'source': 'C - Cases Filed', 'target':'D - Cases Disposed', 'value':len(disposedFileNumbers)},
	]

	reasonsToNodes(disposalReasons, links)
	reasonsToNodes(declineReasons, links)
	#print(links)


	df = pd.DataFrame(links)

	#print(df.head())
	nodes = np.unique(df[["source","target"]], axis=None)
	nodes = pd.Series(index=nodes, data=range(len(nodes)))
	#print(nodes)


	#work out node position
	nodes = (
		nodes.to_frame("id").assign(
			x = lambda d: factorize(d.index.str[0]),
			y = lambda d: factorize(d.index.str[0])/5,
		)
	)

	#print(nodes['y'])

	fig = go.Figure(
    	go.Sankey(
    		arrangement = "snap",
    	    node={"label": nodes.index, "x": nodes["x"], "y": nodes["y"]},
    	    link={
    	        "source": nodes.loc[df["source"], "id"],
    	        "target": nodes.loc[df["target"], "id"],
     	       	"value": df["value"],
     	   },
    	)
	)

	fig.update_layout(title_text=crimeCategory, font_size=10, title_x=0.5)
	fig.write_html("Sankeys\\KCPDClearance - "+crimeCategory + ".html")


def generateJCPOCaseHistory(receivedFileNumbers, listOfKarpelCases):

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
	fig.write_html("TestOutput2.html")

