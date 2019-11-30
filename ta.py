# -*- coding: utf-8 -*-
"""
Created on Sun May 28 21:09:46 2017

@author: Pramesh Kumar
"""
import math
import time
import heapq
import numpy as np
from scipy import optimize

inputLocation = "Sioux Falls network/"

class Zone:
    def __init__(self, _tmpIn):
        self.zoneId = _tmpIn[0]
        self.lat = 0
        self.lon = 0
        self.destList = []


class Node:
    '''
    This class has attributes associated with any node
    '''
    def __init__(self, _tmpIn):
        self.Id = _tmpIn[0]
        self.lat = 0
        self.lon = 0
        self.outLinks = []
        self.inLinks = []
        self.label = float("inf")
        self.pred = ""
        self.inDegree = 0
        self.outDegree = 0
        self.order = 0 # Topological order
        self.wi = 0.0 # Weight of the node in Dial's algorithm
        self.xi = 0.0 # Toal flow crossing through this node in Dial's algorithm


class Link:
    '''
    This class has attributes associated with any link
    '''
    def __init__(self, _tmpIn):
        self.tailNode = _tmpIn[0]
        self.headNode = _tmpIn[1]
        self.capacity = float(_tmpIn[2]) # veh per hour
        self.length = float(_tmpIn[3]) # Length
        self.fft = float(_tmpIn[4]) # Free flow travel time (min)
        self.beta = float(_tmpIn[6])
        self.alpha = float(_tmpIn[5])
        self.speedLimit = float(_tmpIn[7])
        #self.toll = float(_tmpIn[9])
        #self.linkType = float(_tmpIn[10])
        self.flow = 0.0
        self.cost =  float(_tmpIn[4]) #float(_tmpIn[4])*(1 + float(_tmpIn[5])*math.pow((float(_tmpIn[7])/float(_tmpIn[2])), float(_tmpIn[6])))
        self.logLike = 0.0
        self.reasonable = True # This is for Dial's stochastic loading
        self.wij = 0.0 # Weight in the Dial's algorithm
        self.xij = 0.0 # Total flow on the link for Dial's algorithm


class Demand:
    def __init__(self, _tmpIn):
        self.fromZone = _tmpIn[0]
        self.toNode = _tmpIn[1]
        self.demand = float(_tmpIn[2])

def readDemand():
    inFile = open(inputLocation+ "demand.dat")
    tmpIn = inFile.readline().strip().split("\t")
    for x in inFile:
        tmpIn = x.strip().split("\t")
        tripSet[tmpIn[0], tmpIn[1]] = Demand(tmpIn)
        if tmpIn[0] not in zoneSet:
            zoneSet[tmpIn[0]] = Zone([tmpIn[0]])
        if tmpIn[1] not in zoneSet:
            zoneSet[tmpIn[1]] = Zone([tmpIn[1]])
        if tmpIn[1] not in zoneSet[tmpIn[0]].destList:
            zoneSet[tmpIn[0]].destList.append(tmpIn[1])

    inFile.close()
    print(len(tripSet), "OD pairs")
    print(len(zoneSet), "zones")

def readNetwork():
    inFile = open(inputLocation + "network.dat")
    tmpIn = inFile.readline().strip().split("\t")
    for x in inFile:
        tmpIn = x.strip().split("\t")
        linkSet[tmpIn[0], tmpIn[1]] = Link(tmpIn)
        if tmpIn[0] not in nodeSet:
            nodeSet[tmpIn[0]] = Node(tmpIn[0])
        if tmpIn[1] not in nodeSet:
            nodeSet[tmpIn[1]] = Node(tmpIn[1])
        if tmpIn[1] not in nodeSet[tmpIn[0]].outLinks:
            nodeSet[tmpIn[0]].outLinks.append(tmpIn[1])
        if tmpIn[0] not in nodeSet[tmpIn[1]].inLinks:
            nodeSet[tmpIn[1]].inLinks.append(tmpIn[0])

    inFile.close()
    print(len(nodeSet), "nodes")
    print(len(linkSet), "links")



###########################################################################################################################

readStart = time.time()

tripSet = {}
zoneSet = {}
linkSet = {}
nodeSet ={}



readDemand()
readNetwork()

originZones = set([k[0] for k in tripSet])
print("Reading the network data took", round(time.time() - readStart, 2), "secs")

#############################################################################################################################
#############################################################################################################################


def DijkstraHeap(origin):
    '''
    Calcualtes shortest path from an origin to all other destinations.
    The labels and preds are stored in node instances.
    '''
    for n in nodeSet:
        nodeSet[n].label = float("inf")
        nodeSet[n].pred = ""
    nodeSet[origin].label = 0.0
    nodeSet[origin].pred = "NA"
    SE = [(0, origin)]
    while SE:
        currentNode = heapq.heappop(SE)[1]
        currentLabel = nodeSet[currentNode].label
        for toNode in nodeSet[currentNode].outLinks:
            link = (currentNode, toNode)
            newNode = toNode
            newPred =  currentNode
            existingLabel = nodeSet[newNode].label
            newLabel = currentLabel + linkSet[link].cost
            if newLabel < existingLabel:
                heapq.heappush(SE, (newLabel, newNode))
                nodeSet[newNode].label = newLabel
                nodeSet[newNode].pred = newPred

def updateTravelTime():
    '''
    This method updates the travel time on the links with the current flow
    '''
    for l in linkSet:
        linkSet[l].cost = linkSet[l].fft*(1 + linkSet[l].alpha*math.pow((linkSet[l].flow*1.0/linkSet[l].capacity), linkSet[l].beta))

from scipy.optimize import fsolve
def findAlpha(x_bar):
    '''
    This uses unconstrained optimization to calculate the optimal step size required
    for Frank-Wolfe Algorithm

    ******************* Need to be revised: Currently not working.**********************************************
    '''
    #alpha = 0.0


    def df(alpha):
        sum_derivative = 0 ## this line is the derivative of the objective function.
        for l in linkSet:
            tmpFlow = (linkSet[l].flow + alpha*(x_bar[l] - linkSet[l].flow))
            #print("tmpFlow", tmpFlow)
            tmpCost = linkSet[l].fft*(1 + linkSet[l].alpha*math.pow((tmpFlow*1.0/linkSet[l].capacity), linkSet[l].beta))
            sum_derivative = sum_derivative + (x_bar[l] - linkSet[l].flow)*tmpCost
        return sum_derivative
    sol = optimize.root(df, np.array([0.1]))
    sol2 = fsolve(df, np.array([0.1]))
    #print(sol.x[0], sol2[0])
    return max(0.1, min(1, sol2[0]))
    '''
    def int(alpha):
        tmpSum = 0
        for l in linkSet:
            tmpFlow = (linkSet[l].flow + alpha*(x_bar[l] - linkSet[l].flow))
            tmpSum = tmpSum + linkSet[l].fft*(tmpFlow + linkSet[l].alpha * (math.pow(tmpFlow, 5) / math.pow(linkSet[l].capacity, 4)))
        return tmpSum

    bounds = ((0, 1),)
    init = np.array([0.7])
    sol = optimize.minimize(int, x0=init, method='SLSQP', bounds = bounds)

    print(sol.x, sol.success)
    if sol.success == True:
        return sol.x[0]#max(0, min(1, sol[0]))
    else:
        return 0.2
    '''

def tracePreds(dest):
    '''
    This method traverses predecessor nodes in order to create a shortest path
    '''
    prevNode = nodeSet[dest].pred
    spLinks = []
    while nodeSet[dest].pred != "NA":
        spLinks.append((prevNode, dest))
        dest = prevNode
        prevNode = nodeSet[dest].pred
    return spLinks




def loadAON():
    '''
    This method produces auxiliary flows for all or nothing loading.
    '''
    x_bar = {l: 0.0 for l in linkSet}
    SPTT = 0.0
    for r in originZones:
        DijkstraHeap(r)
        for s in zoneSet[r].destList:
            try:
                dem = tripSet[r, s].demand
            except KeyError:
                dem = 0.0
            SPTT = SPTT + nodeSet[s].label * dem
            if r != s:
                for spLink in tracePreds(s):
                    x_bar[spLink] = x_bar[spLink] + dem
    return SPTT, x_bar

def findReasonableLinks():
    for l in linkSet:
        if nodeSet[l[1]].label > nodeSet[l[0]].label:
            linkSet[l].reasonable = True
        else:
            linkSet[l].reasonable = False

def computeLogLikelihood():
    '''
    This method computes link likelihood for the Dial's algorithm
    '''
    for l in linkSet:
        if linkSet[l].reasonable == True: # If reasonable link
            linkSet[l].logLike = math.exp(nodeSet[l[1]].label - nodeSet[l[0]].label - linkSet[l].cost)


def topologicalOrdering():
    '''
    * Assigns topological order to the nodes based on the inDegree of the node
    * Note that it only considers reasonable links, otherwise graph will be acyclic
    '''
    for e in linkSet:
        if linkSet[e].reasonable == True:
                nodeSet[e[1]].inDegree = nodeSet[e[1]].inDegree + 1
    order = 0
    SEL = [k for k in nodeSet if nodeSet[k].inDegree == 0]
    while SEL:
        i = SEL.pop(0)
        order = order + 1
        nodeSet[i].order = order
        for j in nodeSet[i].outLinks:
            if linkSet[i, j].reasonable == True:
                nodeSet[j].inDegree = nodeSet[j].inDegree - 1
                if nodeSet[j].inDegree == 0:
                    SEL.append(j)
    if order < len(nodeSet):
        print("the network has cycle(s)")

def resetDialAttributes():
    for n in nodeSet:
        nodeSet[n].inDegree = 0
        nodeSet[n].outDegree = 0
        nodeSet[n].order = 0
        nodeSet[n].wi = 0.0
        nodeSet[n].xi = 0.0
    for l in linkSet:
        linkSet[l].logLike = 0.0
        linkSet[l].reasonable = True
        linkSet[l].wij = 0.0
        linkSet[l].xij = 0.0



def DialLoad():
    '''
    This method runs the Dial's algorithm and prepare a stochastic loading.
    '''
    resetDialAttributes()
    x_bar = {l: 0.0 for l in linkSet}
    for r in originZones:
        DijkstraHeap(r)
        findReasonableLinks()
        topologicalOrdering()
        computeLogLikelihood()

        '''
        Assigning weights to nodes and links
        '''
        order = 1
        while (order <= len(nodeSet)):
            i = [k for k in nodeSet if nodeSet[k].order == order][0] # Node with order no equal to current order
            if order == 1:
                nodeSet[i].wi = 1.0
            else:
                nodeSet[i].wi = sum([linkSet[k, i].wij for k in nodeSet[i].inLinks if linkSet[k, i].reasonable == True])
            for j in nodeSet[i].outLinks:
                if linkSet[i, j].reasonable == True:
                    linkSet[i, j].wij = nodeSet[i].wi*linkSet[i, j].logLike
            order = order + 1
        '''
        Assigning load to nodes and links
        '''
        order = len(nodeSet) # The loading works in reverse direction
        while (order >= 1):
            j = [k for k in nodeSet if nodeSet[k].order == order][0]  # Node with order no equal to current order
            try:
                dem = tripSet[r, j].demand
            except KeyError:
                dem = 0.0
            nodeSet[j].xj = dem + sum([linkSet[j, k].xij for k in nodeSet[j].outLinks if linkSet[j, k].reasonable == True])
            for i in nodeSet[j].inLinks:
                if linkSet[i, j].reasonable == True:
                    linkSet[i, j].xij = nodeSet[j].xj * (linkSet[i, j].wij / nodeSet[j].wi)
            order = order - 1
        for l in linkSet:
            if linkSet[l].reasonable == True:
                x_bar[l] = x_bar[l] + linkSet[l].xij

    return x_bar



def assignment(loading, algorithm, accuracy = 0.01, maxIter=100):
    '''
    * Performs traffic assignment
    * Type is either deterministic or stochastic
    * Algorithm can be MSA or FW
    * Accuracy to be given for convergence
    * maxIter to stop if not converged
    '''
    it = 1
    gap = float("inf")
    x_bar = {l: 0.0 for l in linkSet}
    startP = time.time()
    while gap > accuracy:
        if algorithm == "MSA" or it < 2:
            alpha = (1.0/it)
        elif algorithm == "FW":
            alpha = findAlpha(x_bar)
            #print("alpha", alpha)
        else:
            print("Terminating the program.....")
            print("The solution algorithm ", algorithm, " does not exist!")
        prevLinkFlow = np.array([linkSet[l].flow for l in linkSet])
        for l in linkSet:
            linkSet[l].flow = alpha*x_bar[l] + (1-alpha)*linkSet[l].flow
        updateTravelTime()
        if loading == "deterministic":
            SPTT, x_bar = loadAON()
            #print([linkSet[a].flow * linkSet[a].cost for a in linkSet])
            TSTT = round(sum([linkSet[a].flow * linkSet[a].cost for a in linkSet]), 3)
            SPTT = round(SPTT, 3)
            gap = round(abs((TSTT / SPTT) - 1), 5)
            # print(TSTT, SPTT, gap)
            if it == 1:
                gap = gap + float("inf")
        elif loading == "stochastic":
            x_bar = DialLoad()
            currentLinkFlow = np.array([linkSet[l].flow for l in linkSet])
            change = (prevLinkFlow -currentLinkFlow)
            if it < 3:
                gap = gap + float("inf")
            else:
                gap = round(np.linalg.norm(np.divide(change, prevLinkFlow,  out=np.zeros_like(change), where=prevLinkFlow!=0)), 2)

        else:
            print("Terminating the program.....")
            print("The loading ", loading, " is unknown")

        it = it + 1
        if it > maxIter:
            print("The assignment did not converge with the desired gap and max iterations are reached")
            print("current gap ", gap)
            break
    print("Assignment took", time.time() - startP, " seconds")
    print("assignment converged in ", it, " iterations")

def writeUEresults():
    outFile = open("UE_results.dat", "w")                                                                                                                                                                                                                                                                # IVT, WT, WK, TR
    tmpOut = "tailNode\theadNode\tcapacity\tlength\tfft\tUE_travelTime\tUE_flow"
    outFile.write(tmpOut+"\n")
    for i in linkSet:
        tmpOut = str(linkSet[i].tailNode) + "\t" + str(linkSet[i].headNode) + "\t" + str(linkSet[i].capacity) + "\t" + str(linkSet[i].length) + "\t" + str(linkSet[i].fft) + "\t" + str(linkSet[i].cost) + "\t" + str(linkSet[i].flow)
        outFile.write(tmpOut + "\n")
    outFile.close()


###########################################################################################################################



assignment("deterministic", "FW", accuracy = 0.001, maxIter=1000)
writeUEresults()
#assignment("stochastic", "MSA", accuracy = 0.01, maxIter=100)