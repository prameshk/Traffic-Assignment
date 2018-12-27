import networkx as nx
import matplotlib.pyplot as plt

G=nx.Graph()



# for writing the results in excel
import xlwt
import xlrd # import xlrd python package to play with excel files
import time
# to have the mathematical functions
import math
# For solving optimization problem python has a module named CVXPY. The formulation is described below.
from cvxpy import *

import Convex_Combination
#CVX supports all the data types offered by np.
import numpy as np
# This is for creating priority Queue Data Type which will help us in creating a tree with different nodes.
try:
    from Queue import PriorityQueue
except:
    from queue import PriorityQueue

file_location = "chicago.xlsx" #defining excel file location

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
        G.add_edge(int(sheet.cell_value(rows, 0)), int(sheet.cell_value(rows, 1)))

with open("ChicagoSketch_node.tntp.txt", "r") as f:
    next(f)
    i = 0
    for line in f:
        line = line.rstrip()  # we're not interested in the newline at the end
        G.add_node(int(line.split()[0]), pos=(float(line.split()[1]), float(line.split()[2])), level=i)
        i = i + 1





pos = nx.spring_layout(G,scale=10)

plt.figure(2,figsize=(15,15))
nx.draw(G, nx.get_node_attributes(G, 'pos'), with_labels=True, node_size=0, font_size=6)
plt.savefig("graph.png", dpi = 1000)
plt.show()

