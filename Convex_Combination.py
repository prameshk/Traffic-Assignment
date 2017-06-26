# -*- coding: utf-8 -*-
"""
Created on Sun May 28 19:12:20 2017

@author: Pramesh Kumar
"""
import math
import numpy as np
from collections import OrderedDict
from math import *
from scipy import optimize

class data:
    def __init__(self, net, od, flow):
        self.from_node = np.array(net[0])
        self.to_node = np.array(net[1])
        self.capacity = np.array(net[2])
        self.length = np.array(net[3])
        self.fft = np.array(net[4])
        self.alpha = np.array(net[5])
        self.beta = np.array(net[6])
        self.nodes = np.union1d(self.from_node, self.to_node)
        self.od = od
        self.flow = np.array(flow)


    def ttf(self):
        return self.fft*(1 + self.alpha*np.power((self.flow/self.capacity), self.beta))
    def edges(self):
        links = []
        for x in range(len(self.from_node)):
            links.append((self.from_node[x], self.to_node[x]))
        return links

    def network(self):
        graph = {}
        for x in range(len(self.edges())):
            graph[self.from_node[x], self.to_node[x]] = [self.from_node[x], self.to_node[x], self.ttf()[x], self.flow[x]]
        return graph



    def dial_graph(self):
        dial_g = {}
        for x in range(len(self.from_node)):
            dial_g.setdefault(self.from_node[x], {})[self.to_node[x]] = self.ttf()[x]
        return dial_g

    def reverse_dial_graph(self):
        reverse_dial_g = {}
        for x in range(len(self.to_node)):
            reverse_dial_g.setdefault(self.to_node[x], []).append(self.from_node[x])
        return reverse_dial_g





class shortest_path(data):
    def label_correcting(self, start_node):
        links_visited = []
        label = {}
        # We assign only origin node in Scan Eligible List initially
        SEL = [start_node]
        # This step is to assign 0 node label to origin node and infinite values to all other nodes
        pred = {start_node: 0}
        for i in self.nodes:
            if (i == start_node):
                label[i] = 0
            else:
                label[i] = float("inf")

                # This is an important step to check all the nodes and assign a shortest label everytime
        while SEL:
            a = SEL.pop(0)  # removes the first element in SEL and assigns it to
            for b, c in self.network().items():  # checking for nodes connected to a and their distances from a
                if (c[0] == a):
                    if (label[c[1]] > label[c[0]] + c[2]):  # condition for updating labels
                        label[c[1]] = label[c[0]] + c[2]
                        pred[c[1]] = a  # assign the predecessor for following shortest path
                        SEL.append(c[1])  # Adding node to Scan Eligible List
        label_ascending = OrderedDict(sorted(label.items(), key=lambda kv: kv[1]))  # For Dial's network loading
        label_descending = OrderedDict(sorted(label.items(), key=lambda kv: kv[1], reverse=True))  # For Dial's network loading
        return label, label_ascending, label_descending, pred  # This calls the function defined below

    #The visited links for shortest path
    def visited_links(self, start_node, end_node, pred):
        links_visited = []
        # To maintain all the links in shortest path
        links_visited.append((pred[end_node], end_node))

        start = start_node
        end = end_node
        for i in range(100000):
            start = start
            end = pred[end]
            if (start == end):
                break
            else:
                links_visited.append((pred[end], end))
        return links_visited[::-1]


#This class has multiple inheritances. If you wanna call any method of class, please make sure you provide input data and the start and end node
class stochastic_loading(data, shortest_path):
    def dial(self, start_node):
        #This will call the function to calculate the label for all the nodes
        label, ascending_label, descending_label, pred = self.label_correcting(start_node)
        # Step 1: To calculate link likelihood
        # We maintain a dictionary of link likelihood of different links
        Lij = {}
        #Let's loop through all the links in the network
        for x in self.edges():
            li = self.network()[x][0] #This is the upnode of the link
            lj = self.network()[x][1] #This is the down node of the link
            tij = self.network()[x][2] #This is the travel time of the link
            if(label[lj] > label[li]): #This condition checks if the link is reasonable or not based on the link label
                Lij.setdefault(li, {})[lj] = exp(label[lj] - label[li] - tij) #Then we can store the information in a dictionary

        # Step 2: To calcualte the node and link weight
        wi = {}
        Wij = {}
        for i in ascending_label:
            wi[i] = 0 #Let's make weight of every node in the network as zero except the start node below
        wi[start_node] = 1
        #let's loop through all the ascending labels and assign the weight
        for key in ascending_label: #This will loop through all the nodes in the ascending order of their labels
            if (key != start_node):
                for z in self.reverse_dial_graph()[key]: #This will search the reverse dial graph which looks like {1:[2, 3], } for the particular node and return the nodes which are connected to it
                    try:
                        wi[key] = wi[key] + Wij[z][key] #This will update all the node weights depending on what is the node weights of the immediate predecessor nodes
                    except KeyError:
                        continue
            #This step will update all the link weights using the Lij and the node weights
            if (key != ascending_label.items()[-1][0]):
                try:
                    for value, time in Lij[key].items(): # this will take all the links emerging from the "key" node and it will look for only reasonable links in Lij other wise it will continue in the except Keyerror case
                        Wij.setdefault(key, {})[value] = wi[key] * Lij[key][value]
                except KeyError:
                    continue
        # Step 3: To calculate the node and link flows
        xi = {}
        Xij = {}
        largest_label = 0
        for x in descending_label:
            xi[x] = 0
        for key in descending_label:
            if (key != start_node):
                if (key == descending_label.items()[0][0]):
                    xi[key] = xi[key] + self.od[(start_node, key)]
                else:
                    for z, f in self.dial_graph()[key].items():
                        try:
                            xi[key] = xi[key] + Xij[key][z] + self.od[(start_node, key)]
                        except KeyError:
                            continue

            if (key != start_node):
                for i in self.reverse_dial_graph()[key]:
                    try:
                        Xij.setdefault(i, {})[key] = xi[key] * Wij[i][key] / wi[key]
                    except KeyError:
                        continue
        return Xij, label


#This class does the assignment part using MSA, again this class has also multiple inheritances
class assignment(data, shortest_path, stochastic_loading):
    def finding_alpha(self, x, y):
        alpha = 0.0
        def df(a):
            sum = 0
            for links in self.edges():
                sum = sum + (y[self.edges().index(links)] - self.flow[
                    self.edges().index(links)]) * self.fft[self.edges().index(links)] * (
                            1 + self.alpha[self.edges().index(links)] * np.power(((x[self.edges().index(links)] + a * (y[self.edges().index(links)] - x[self.edges().index(links)])) / self.capacity[self.edges().index(links)]), self.beta[self.edges().index(links)]))
            return sum
        sol = optimize.root(df, 0)
        return max(0, min(1, sol.x[0]))



    def msa_sue(self):
        #This is for initial flow
        for k in self.nodes:
            Xij, label = self.dial(k)
            for a, b in Xij.items():
                for s in b.items():
                    self.flow[self.edges().index((a, s[0]))] = self.flow[self.edges().index((a, s[0]))] + s[1]
                    #self.flow[self.network().keys().index((a, s[0]))] = self.flow[self.network().keys().index((a, s[0]))] + s[1]
        print self.flow
        x_old =  [0]*len(self.edges())
        for k in range(2, 100):
            y = [0]*len(self.edges())
            #For calculating shortest path travel time
            SPTT = 0
            for g in self.nodes:
                label, ascending_label, descending_label, pred = self.label_correcting(g)
                for z, j in self.od.items():
                    if(z[0] == g):
                        SPTT = SPTT + j*label[z[1]]
            print SPTT
            #For calculating Total system travel time
            TSTT = 0
            for link in self.network().items():
                TSTT = TSTT + link[1][3]*link[1][2]
            print TSTT

            gap = 1.0*(TSTT-SPTT)/SPTT
            norm = np.linalg.norm(np.divide((self.flow - x_old), self.flow))
            if(norm < 0.1):
                break
            else:
                for z in self.nodes:
                    Xij, label = self.dial(z)
                    for a, b in Xij.items():
                        for s in b.items():
                            y[self.edges().index((a, s[0]))] = self.flow[self.edges().index((a, s[0]))] + s[1]
                            #y[self.network().keys().index((a, s[0]))] = self.flow[self.network().keys().index((a, s[0]))] + s[1]
                #Updating the link travel time
                alp = 1.0 / k
                #alp = self.finding_alpha(self.flow, y)
                x_old = self.flow
                self.flow = self.flow + alp*(y - self.flow)




            print "k = ", k, ' TSTT =', TSTT, ', SPTT =', SPTT, ', gap =', round(norm, 3)
        return self.flow





    def msa_ue(self):
        for g in self.nodes:
            label, ascending_label, descending_label, pred = self.label_correcting(g)
            for z, j in self.od.items():
                if (z[0] == g):
                    for links in self.visited_links(z[0], z[1], pred):
                        self.flow[self.edges().index(links)] = self.flow[self.edges().index(links)] + j
                        #self.flow[self.network().keys().index(links)] = self.flow[self.network().keys().index(links)] + j
        print self.flow

        for k in range(2, 1000):
            y = [0]*len(self.edges())
            #For calculating shortest path travel time
            SPTT = 0
            for g in self.nodes:
                label, ascending_label, descending_label, pred = self.label_correcting(g)
                for z, j in self.od.items():
                    if(z[0] == g):
                        SPTT = SPTT + j*label[z[1]]
            print SPTT

        #For calculating Total system travel time
            TSTT = 0
            for link in self.network().items():
                TSTT = TSTT + link[1][3]*link[1][2]
            print TSTT
            gap = 1.0 * (TSTT - SPTT) / SPTT
            if (gap < 0.1):
                break
            else:
                for node in self.nodes:
                    label, ascending_label, descending_label, pred = self.label_correcting(node)
                    for z, j in self.od.items():
                        if (z[0] == node):
                            for links in self.visited_links(z[0], z[1], pred):
                                y[self.edges().index(links)] = y[self.edges().index(links)] + j
                                #y[self.network().keys().index(links)] = y[self.network().keys().index(links)] + j
                #a = 1.0 / k
                a = self.finding_alpha(self.flow, y)
                # Updating the link travel time
                self.flow = self.flow + a * (y - self.flow)

            print "k = ", k, ' TSTT =', TSTT, ', SPTT =', SPTT, ', gap =', round(gap, 3)

        return self.flow, k, gap, TSTT, SPTT
