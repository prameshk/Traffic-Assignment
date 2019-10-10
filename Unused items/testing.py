# -*- coding: utf-8 -*-
"""
Created on Sun May 28 21:09:46 2017

@author: Pramesh Kumar
"""

#This is for calling graph 
import xlrd # import xlrd python package to play with excel files
import time
import Convex_Combination

file_location = "network.xlsx" #defining excel file location

workbook = xlrd.open_workbook(file_location) #assigning workbook

sheet = workbook.sheet_by_index(0) #assigning sheet of that workbook


net = [[] for i in range(7)]
for rows in range(sheet.nrows): #This will read no. of rows
    if(rows != 0):
        net[0].append(int(sheet.cell_value(rows, 0)))
        net[1].append(int(sheet.cell_value(rows, 1)))
        net[2].append(sheet.cell_value(rows, 2))
        net[3].append(sheet.cell_value(rows, 3))
        net[4].append(sheet.cell_value(rows, 4))
        net[5].append(sheet.cell_value(rows, 5))
        net[6].append(sheet.cell_value(rows, 6))

#This step reads the O-D demand from the text file and we need to feed this into the class graph
od = {}  # we'll store our result in this dict
origin_no = 0  # our starting Origin number in case the file doesn't begin with one
with open("C:\Users\kumar372\Desktop\Trial - Copy\SiouxFalls_trips.tntp.txt", "r") as f:
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

print od.items()




y = Convex_Combination.shortest_path(net,od, [0]*76)

print "this", y.label_correcting(1)[3]
#print "links visited", y.visited_links(1, 21, y.label_correcting(1)[3])
start_time = time.time()

z = Convex_Combination.stochastic_loading(net, od, [0]*76)
#for a, b in od.items():
print z.dial(2)

a = Convex_Combination.assignment(net, od, [0]*76)
print a.msa_ue()

print("--- %s seconds ---" % (time.time() - start_time))


