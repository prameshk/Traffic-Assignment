import numpy as np
import math
import time
import heapq # For shortest paths
from collections import defaultdict
from scipy import optimize

#inputLocation = "Chicago Sketch Network/"
inputLocation = "TC Network/"
class Zones:
    def __init__(self, _tmpIn):
        self.zoneId = _tmpIn[0]
        self.lat = float(_tmpIn[1])
        self.lon = float(_tmpIn[2])


class Node:
    def __init__(self, _tmpIn):
        self.Id = _tmpIn[0]
        self.lat = float( _tmpIn[0])
        self.lon = float( _tmpIn[1])
        self.outLinks = []
        self.inLinks = []
        self.labels = 0 # time, cost, mode(may be?), IVT, WT, WK, TR
        self.preds = ("", "") # one is node and other link

class Link:
    def __init__(self, _tmpIn):
        self.tailNode = _tmpIn[0]
        self.headNode = _tmpIn[1]
        self.capacity = float(_tmpIn[2]) # veh per hour
        self.length = float(_tmpIn[3]) # Length
        self.fft = float(_tmpIn[4]) # Free flow travel time (min)
        self.beta = float(_tmpIn[6])
        self.alpha = float(_tmpIn[5])
        self.flow = float(_tmpIn[7])
        self.speedLimit = float(_tmpIn[8])
        self.toll = float(_tmpIn[9])
        self.linkType = float(_tmpIn[10])
        self.time =  float(_tmpIn[4])*(1 + float(_tmpIn[5])*math.pow((float(_tmpIn[7])/float(_tmpIn[2])), float(_tmpIn[6])))


def BPR(flow, fft, alpha, beta, capacity):
    return fft*(1  + alpha*(math.pow((flow/capacity), beta)))

def updateTravelTime():
    for l in linkSet:
        linkSet[l].time = linkSet[l].fft*(1 + linkSet[l].alpha*math.pow((linkSet[l].flow/linkSet[l].capacity), linkSet[l].beta))


class Demand:
    def __init__(self, _tmpIn):
        self.origin = _tmpIn[0]
        self.dest =  _tmpIn[1]
        self.trips = float(_tmpIn[2])

def readZones():
    inFile = open(inputLocation + "ft_input_zones.dat")
    tmpIn = inFile.readline().strip().split("\t")
    for x in inFile:
        tmpIn = x.strip().split("\t")
        zoneSet[tmpIn[0]] = Node(tmpIn)
    inFile.close()
    print len(zoneSet), "zones"

def readNodes():
    inFile = open(inputLocation + "nodes.dat")
    tmpIn = inFile.readline().strip().split("\t")
    for x in inFile:
        tmpIn = x.strip().split("\t")
        nodeSet[tmpIn[0]] = Node(tmpIn)
    inFile.close()
    print len(nodeSet), "nodes"

def readNetwork():
    inFile = open(inputLocation + "network.dat")
    tmpIn = inFile.readline().strip().split("\t")
    for x in inFile:
        tmpIn = x.strip().split("\t")
        linkId = (tmpIn[0], tmpIn[1])
        linkSet[linkId] = Link(tmpIn)
        if tmpIn[0] not in nodeSet:
            print "Error: Node not present"
        else:
            nodeSet[tmpIn[0]].outLinks.append(tmpIn[1])
        if tmpIn[1] not in nodeSet:
            print "Error: Node not present"
        else:
            nodeSet[tmpIn[1]].inLinks.append(tmpIn[0])
    inFile.close()
    print len(linkSet), "links"

def readDemand():
    inFile = open(inputLocation + "demand.dat")
    tmpIn = inFile.readline().strip().split("\t")
    for x in inFile:
        tmpIn = x.strip().split("\t")
        demandId = (tmpIn[0] , tmpIn[1])
        tripSet[demandId] = Demand(tmpIn)
        originZones[tmpIn[0]].add(tmpIn[1])
    inFile.close()
    print len(originZones), "origins"
    print len(tripSet), "OD pairs"



def Dijkstra(origin): # Takes origin node
    for n in nodeSet:
        nodeSet[n].label = float("inf")
        nodeSet[n].pred = ("", "")
        nodeSet[origin].label = 0
    SE = [(0, origin)]
    it = 0
    while SE:
        currentNode = heapq.heappop(SE)[1]
        currentLabel = nodeSet[currentNode].label
        it = it + 1
        for toNode in nodeSet[currentNode].outLinks:
            link = (currentNode, toNode)
            newNode = toNode
            newPred =  (currentNode, link)
            existingLabel = nodeSet[newNode].label
            newLabel = currentLabel + linkSet[link].time
            if newLabel < existingLabel:
                heapq.heappush(SE, (newLabel, newNode))
                nodeSet[newNode].label = newLabel
                nodeSet[newNode].pred = newPred
    return it

def tracePreds(dest):
    prevNode, prevLink = nodeSet[dest].pred
    spLinks = [prevLink]
    while prevNode != "":
        prevNode, prevLink = nodeSet[prevNode].pred
        if prevLink != "":
            spLinks.append(prevLink)
    return spLinks

def findAlpha(x_bar):
    alpha = 0.0
    def df(alpha):
        sum_derivative = 0 ## this line is the derivative of the objective function.
        for l in linkSet:
            sum_derivative = sum_derivative + (x_bar[l] - linkSet[l].flow)*BPR((linkSet[l].flow + alpha*(x_bar[l] - linkSet[l].flow)), linkSet[l].fft, linkSet[l].alpha, linkSet[l].beta, linkSet[l].capacity)
        return sum_derivative
    sol = optimize.root(df, 0)
    return max(0, min(1, sol.x[0]))




def assignment(type, algorithm, accuracy):
    it = 1
    gap = float("inf")
    x_bar = {}
    for l in linkSet:
        x_bar[l] = 0.0
    while gap > accuracy:
        if algorithm == "MSA" or it < 2:
            alpha = (1.0/it)
        if algorithm == "FW":
            alpha = findAlpha(x_bar)
        for l in linkSet:
            linkSet[l].flow = alpha*x_bar[l] + (1-alpha)*linkSet[l].flow
        updateTravelTime()
        for l in linkSet:
            x_bar[l] = 0.0
        SPTT = 0.0
        start = time.time()
        for r in originZones:
            Dijkstra(r)
            destinations = originZones[r]
            for s in destinations:
                dem = tripSet[r, s].trips
                SPTT = SPTT + nodeSet[s].label*dem
                if r != s:
                    for spLink in tracePreds(s):
                        x_bar[spLink] = x_bar[spLink] + dem
        print "one O took", time.time() - start
        TSTT = sum([linkSet[a].flow*linkSet[a].time for a in linkSet])
        gap = abs((TSTT / SPTT) - 1)
        print TSTT, SPTT, gap
        if it == 1:
            gap = gap  + float("inf")
        it = it + 1
        if it > 10:
            print "The assignment did not converge with the desired gap"
            print "current gap ", gap
            break
    return "assignment converged in ", it, " iterations"


def print_UE_flows():
    outFile = open("tc_UE_flow.dat", "w")
    tmpOut = "\tfromNode\ttoNode\tflow\ttravelTime"
    outFile.write(tmpOut+"\n")
    for l in linkSet:
        tmpOut = "\t"+str(linkSet[l].tailNode)+"\t"+str(linkSet[l].headNode)+"\t"+str(linkSet[l].flow)+"\t"+str(linkSet[l].time)
        outFile.write(tmpOut+"\n")
    outFile.close()

def printODtravelTimes():
    outFile = open("ft_input_drivingTime.dat", "w")
    tmpOut = "fromTAZ\ttoTAZ\ttravelTime"
    outFile.write(tmpOut + "\n")
    for z in zoneSet:
        Dijkstra(z)
        for z2 in zoneSet:
            tmpOut = str(z) + "\t" + str(z2) + "\t"  + str(nodeSet[z2].label)
            outFile.write(tmpOut + "\n")
    outFile.close()






start = time.time()
linkSet ={}
nodeSet ={}
zoneSet = {}
originZones = defaultdict(set)
tripSet = {}


readNodes()
readNetwork()
readDemand()
readZones()
print "Time spent in reading network", (time.time() - start), "seconds"

start = time.time()
assignment("UE", "MSA", 0.0001)
print "Time spent in assignment", (time.time() - start)/60, "minutes"

print_UE_flows()
printODtravelTimes()
