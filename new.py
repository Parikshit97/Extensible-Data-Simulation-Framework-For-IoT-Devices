import array
import anytree
import time
import random
from pprint import pprint
from anytree import Node, RenderTree, AsciiStyle, PostOrderIter
filepath = open("/Users/parikshitnarang/Desktop/UTC/config.txt", "r")
outputfile=open("outputfile1.txt","w+")

treeTopNode = Node("dummy", formulae="")
configTopNode = Node("dummy")
debug=False;

def displayTree(root):
	#print(RenderTree(root))
	for pre, fill, node in RenderTree(root):
    			print("%s%s" % (pre, node.name))

def displayTreeWithFormula(root):
	print(RenderTree(root))
	for pre, fill, node in RenderTree(root):
    			print("%s%s %s" % (pre, node.name, node.formulae))

def addChildConfTree(ParentNode , ChildNode):
	Node(ChildNode,parent=ParentNode)
def checkIfPresent(NodeMetaName):
	thisline = NodeMetaName.split(",")
	parent=thisline[0]
	child=thisline[1]
	return find(parent, lambda node: node.name == child)

def addChilds(ParentNode, ChildNameConfName, NoOfInstances, formula):
	print("Adding child: " + ParentNode + " " + ChildNameConfName + " " + str(NoOfInstances))
	# ParentNode = "Root", L_DC
	if(ParentNode == "Root"):
		# Use counter to add ChildNameConfName_01.. Num of instances to treeTopNode
		configNodes = anytree.search.findall(configTopNode, filter_ = lambda node: node.name == ChildNameConfName)
		if(configNodes.__len__() == 0):
			createdNode = Node(ChildNameConfName, configTopNode, formulae="")
			createNodes(treeTopNode, ChildNameConfName, NoOfInstances, "")
		#else:
		#	print configNodes
		#	print (ChildNameConfName + " is already present")
	else:
		configNodes = anytree.search.findall(configTopNode, filter_ = lambda node: node.name == ChildNameConfName)
		if(configNodes.__len__() == 0):
			nodes = anytree.search.findall(treeTopNode, filter_=lambda node: node.name.startswith(ParentNode))
			#nodes = anytree.search.findall(treeTopNode, filter_=lambda node: node.name in ("1", "2"))
			# Loop for all nodes, and add child 01..N child for each node
			for nodename in nodes:
				createNodes(nodename, ChildNameConfName, NoOfInstances, formula)

			confNode = anytree.search.findall(configTopNode, filter_=lambda node: node.name == ParentNode)	
			Node(ChildNameConfName, confNode[0], formulae="")
		#else:
		#	print configNodes
		#	print (ChildNameConfName + " is already present")

def createNodes(parentNode, childNodeName, instances, formula):
	i = 1
	while(i <= instances):
		if(instances == 1):
			Node(childNodeName, parentNode, formulae=formula)
		else:	
			Node(childNodeName + str(i), parentNode, formulae=formula)
		i = i + 1

def initialize():
	treeTopNode = Node("Root", formulae="")

def createData(dataTime):
	for node in PostOrderIter(treeTopNode):
		if(node.is_leaf):
			# Gauge 100,200
			if(hasattr(node,'formulae')):
				#print node.formulae
				splits = node.formulae.split("#")
				function = splits[0]
				argSplits = splits[1].split(",")
				argSplitslength=argSplits.__len__()
				j=0
				while(j<argSplitslength):
					argSplits[j]=int(argSplits[j],10)
					j=j+1
				data = 0
				if(not hasattr(node,'data')):
					node.data = 0
				if(function == "Gauge"):
					data = getGaugeValue(node.data,argSplits)
					node.data = data
				if(function == 'Counter'):
					data = getCounterValue(node.data, argSplits)
					node.data = data
				if(function=='Random'):
					data=getRandomValue(argSplits)
					node.data=data
				print (node.path)
				print (node.data)
				count=len(node.path)
				pointName = ""
				j=0
				for i in range(len(node.path)):
					pointName = pointName + "/" + node.path[i].name 
				print(pointName + " " + str(dataTime) + " "+ str(node.data))	
				outputfile.write(pointName + " " + str(dataTime) + " "+ str(node.data)+"\n")
				#pprint(vars(node))

			#print node.xyz
def getRandomValue(argSplits):
	return random.randint(argSplits[0] , argSplits[1])

def getGaugeValue(oldValue, argSplits):
	newValue = oldValue + 1
	if(newValue > argSplits[1]):
		newValue = argSplits[0]
	return newValue

def getCounterValue(oldValue, argSplits):
	newValue = oldValue + argSplits[2]
	if(newValue > argSplits[1]):
		newValue = argSplits[0]
	return newValue

def load(filepath):
	print("Starting processing")
	initialize()
	lines = filepath.readlines()
	for i in lines:
		print("Processing line " + i)
		root=-1
		if(i=="\n" or i.startswith("#")==True):
			continue		
#		thisline = i.split(" ")[0].split("x")
		thisline = i.split("/")
# C_DC(10)/L_DC(20)/CHS_HS(5)/CHLR_R(10)/P_LCTDW Gauge(100,100)
		arrayLength=thisline.__len__()
		j=0
		prevNode = "NA"
		formula = ""
		while(j < arrayLength):
			print("Processing line segment: " + thisline[j])
			if(thisline[j].startswith("P")):
				furtherSplit = thisline[j].split(" ")
				nodeType = furtherSplit[0]
				nodeNumber = 1
				if(furtherSplit.__len__() != 1):
					formula = furtherSplit[1]
			else:
				nodeSplits = thisline[j].split("(");
				if(nodeSplits.__len__() == 1):
					nodeType = nodeSplits[0]
					nodeNumber = 1
				else:
					print(nodeSplits)
					nodeType = nodeSplits[0]
					nodeNumber = int(nodeSplits[1].split(")")[0],10)

			if(prevNode == "NA"):
				addChilds("Root", nodeType, nodeNumber, "")
				prevNode = nodeType
			else:
				addChilds(prevNode, nodeType, nodeNumber, formula)
				prevNode = nodeType
			j = j + 1
	if debug:
		displayTreeWithFormula(treeTopNode)
		displayTree(configTopNode)
	i=0
	starttime=time.time()
	x=starttime
	while(i<100):
		createData(x)
		x=x+15*60*1000
		i=i+1
	endTime=time.time()
	print("hello",endTime-starttime)
	#currentTime = time.time()
	#createData(currentTime)
	#x = currentTime + 15*60*1000;
	#createData(x)
	#endTime=time.time()
	#print(int(endTime)-int(currentTime))
#	currentTime = currentTime + 15*60*1000;
#	createData(currentTime)
load(filepath)
outputfile.close();
