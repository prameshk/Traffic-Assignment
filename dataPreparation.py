# -*- coding: utf-8 -*-
"""
Created on Sun May 28 21:09:46 2017

@author: Pramesh Kumar
"""


inputLocation = 'Raw Data/'
inputLocation2 = 'Data/'


od = {}
origin_no = 0  # our starting Origin number in case the file doesn't begin with one
with open(inputLocation+"SiouxFalls_trips.tntp", "r") as f:
    for line in f:
        line = line.rstrip()  # we're not interested in the newline at the end
        if not line:  # empty line, skip
            continue
        if line.startswith("Origin"):
            origin_no = int(line[7:].strip())  # grab the integer following Origin
        else:
            elements = line.split(";")  # get our elements by splitting by semi-colon
            for element in elements:  # loop through each of them:
                if not element:  # we're not interested in the last element
                    continue
                element_no, element_value = element.split(":")  # get our pair
                # beware, these two are now most likely padded strings!
                # that's why we'll strip them from whitespace and convert to integer/float
                if(origin_no != int(element_no.strip())):
                    od[(origin_no, int(element_no.strip()))] = float(element_value.strip())



network = {}
with open(inputLocation+"SiouxFalls_net.tntp", "r") as f:
    next(f)
    for line in f:
        line = line.rstrip()
        line = line.split(";")[0].split('\t')
        #print([line[1], line[2], line[3], line[4], line[5], line[6], line[7], line[8]])
        network[line[1], line[2]] = [line[1], line[2], line[3], line[4], line[5], line[6], line[7], line[8]]






def printOD_flows():
    outFile = open(inputLocation2+"demand.dat", "w")
    tmpOut = "origin\tdest\tdemand"
    outFile.write(tmpOut+"\n")
    for d in od:
        tmpOut = str(d[0])+"\t"+str(d[1])+"\t"+str(od[d])
        outFile.write(tmpOut+"\n")
    outFile.close()

def printNetwork():
    outFile = open(inputLocation2+"network.dat", "w")
    tmpOut = "origin\tdest\tcapacity\tlength\tfft\talpha\tbeta\tspeedLimit"
    outFile.write(tmpOut+"\n")
    for link in network:
        tmpOut ='\t'.join(network[link])
        outFile.write(tmpOut+"\n")
    outFile.close()




printOD_flows()
printNetwork()