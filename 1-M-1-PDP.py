from gurobipy import *
import time
import copy
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os 
import math


class Data(object):
    def __init__(self):
        self.customer_num = 0
        self.node_num = 0
        self.vehicle_num = 0
        self.coor_X = {}
        self.coor_Y = {}
        self.demand = {}
        self.pickdemand = {}
        self.service_time = {}
        self.ready_time = {}
        self.due_time = {}
        self.dis_matrix = {}
        self.arcs = {}
        self.capacity = 0

    def load_data_from_csv(self, csv_path, customer_num, vehicle_num):
        """Load data from CSV file."""
        np.random.seed(0)
        self.customer_num = customer_num
        self.node_num = customer_num
        self.vehicle_num = vehicle_num
        self.capacity = 200  # Default capacity
        
        # Read CSV file
        df = pd.read_csv(csv_path)
        
        # Load only required number of nodes
        for i in range(min(self.node_num, len(df))):
            row = df.iloc[i]
            node_ID = int(row['node_id'])
            self.coor_X[node_ID] = row['coor_x']
            self.coor_Y[node_ID] = row['coor_y']
            self.demand[node_ID] = row['demand']
            self.pickdemand[node_ID] = int((0.5 + np.random.random()) * row['demand'])
            self.ready_time[node_ID] = row['ready_time']
            self.due_time[node_ID] = row['due_time']
            self.service_time[node_ID] = row['service_time']

        # Create distance matrix
        for i in range(self.node_num):
            for j in range(self.node_num):
                temp = (self.coor_X.get(i, 0) - self.coor_X.get(j, 0)) ** 2 + \
                       (self.coor_Y.get(i, 0) - self.coor_Y.get(j, 0)) ** 2
                self.dis_matrix[i, j] = round(math.sqrt(temp), 1)
                self.arcs[i, j] = 1 if i != j else 0  
        return self

    def printData(self, data):
        print("------Dataset Info--------------\n")
        print("Vehicle Count = %4d" % data.vehicle_num)
        print("Customer Count = %4d" % data.customer_num)
        print("Node Count = %4d" % data.node_num)
        for i in data.demand.keys():
            print("%10.0f" % (data.demand[i]), "%10.0f" % data.ready_time[i],
                  "%10.0f" % data.due_time[i], "%10.0f" % data.service_time[i])
        print("-------Distance Matrix-------\n")
        for i in range(data.node_num):
            for j in range(data.node_num):
                print("%6.2f" % (data.dis_matrix[i, j]), end=" ")


if __name__ == '__main__':
    stime = time.time()
    data = Data()
    
    # Set parameters
    customer_num = 11  
    vehicle_num = 25
    
    # Load data from CSV
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(current_dir, "data", "c101_nodes.csv")
    data = data.load_data_from_csv(csv_path, customer_num, vehicle_num)
    data.capacity = 50
    
    print("---pickup demand---\n")
    print(data.pickdemand)
    print("---delivery demand---\n")
    print(data.demand)
    data.printData(data)
    
    PDVRP = Model()

    x = {}  # Decision variable x
    for i in range(data.node_num):
        for j in range(data.node_num):
            for k in range(vehicle_num):
                if i != j:
                    x[i, j, k] = PDVRP.addVar(obj=data.dis_matrix[i, j], vtype=GRB.BINARY, name='x_'+str(i)+'_'+str(j)+'_'+str(k))
    
    y = {}  # Decision variable y
    for i in range(data.node_num):
        for j in range(data.node_num):
            if i != j:
                y[i, j] = PDVRP.addVar(lb=0, vtype=GRB.CONTINUOUS, name='y_' + str(i) + '_' + str(j))

    z = {}  # Decision variable z
    for i in range(data.node_num):
        for j in range(data.node_num):
            if i != j:
                z[i, j] = PDVRP.addVar(lb=0, vtype=GRB.CONTINUOUS, name='z_' + str(i) + '_' + str(j))
    
    # Constraint 1: Vehicle arrival constraint
    for i in range(1, data.node_num):
        expr1 = LinExpr(0)
        for j in range(data.node_num):
            for k in range(vehicle_num):
                if i != j:
                    expr1.addTerms(1, x[i, j, k])
        PDVRP.addConstr(expr1 == 1, name='cons1')
    
    # Constraint 2: Flow balance constraint
    for i in range(data.node_num):
        for k in range(vehicle_num):
            expr2 = LinExpr(0)
            for j in range(data.node_num):
                if i != j:
                    expr2.addTerms(1, x[i, j, k])
                    expr2.addTerms(-1, x[j, i, k])
            PDVRP.addConstr(expr2 == 0, name='cons2')
    
    # Constraint 3: Single visit constraint
    for i in range(data.node_num):
        for k in range(vehicle_num):
            expr3 = LinExpr(0)
            for j in range(data.node_num):
                if i != j:
                    expr3.addTerms(1, x[i, j, k])
            PDVRP.addConstr(expr3 <= 1, name="cons3")

    # Constraint 4: Vehicle capacity constraint
    for i in range(data.node_num):
        for j in range(data.node_num):
            if i != j:
                expr4 = LinExpr(0)
                expr4.addTerms(1, y[i, j])
                expr4.addTerms(1, z[i, j])
                for k in range(vehicle_num):
                    expr4.addTerms(-data.capacity, x[i, j, k])
                PDVRP.addConstr(expr4 <= 0, name='cons4')
    
    # Constraint 5: Delivery constraint
    for i in range(1, data.node_num):
        expr5 = LinExpr(0)
        for j in range(data.node_num):
            if i != j:
                expr5.addTerms(1, y[i, j])
                expr5.addTerms(-1, y[j, i])
        PDVRP.addConstr(expr5 == data.demand[i], name='cons5')

    # Constraint 6: Pickup constraint
    for i in range(1, data.node_num):
        expr6 = LinExpr(0)
        for j in range(data.node_num):
            if i != j:
                expr6.addTerms(1, z[j, i])
                expr6.addTerms(-1, z[i, j])
        PDVRP.addConstr(expr6 == data.pickdemand[i], name='cons6')

    PDVRP.Params.lazyConstraints = 1
    PDVRP.optimize()
    
    # Print solution
    Slist = []
    S = []
    S.append(0)
    for i in range(data.node_num):
        for j in range(data.node_num):
            for k in range(vehicle_num):
                if i != j and x[i, j, k].x > 0.1:
                    print(x[i, j, k].VarName)
    
    for i in range(1, data.node_num):
        for k in range(vehicle_num):
            if i not in S and x[0, i, k].x > 1 - 1e-3:
                print("[0-" + str(i), end='')
                currNode = i
                S.append(currNode)
                flag = True
                while flag:
                    flag = False
                    for j in range(1, data.node_num):
                        if j not in S and x[currNode, j, k].x > 1 - 1e-3:
                            print("-" + str(j), end='')
                            currNode = j
                            S.append(currNode)
                            flag = True
                            break
                print("-0]")
                Slist.append(S)
                S = [0]

    Graph = nx.DiGraph()
    nodes_name = [0]
    cor_xy = [[data.coor_X[0], data.coor_Y[0]]]
    edges = []
    for route in Slist:
        edge = []
        edges.append([route[0], route[1]])
        for i in route[1:]:
            nodes_name.append(i)
            cor_xy.append([data.coor_X[i], data.coor_Y[i]])
            edge.append(i)
            if len(edge) == 2:
                edges.append(copy.deepcopy(edge))
                edge.pop(0)
        edge.append(0)
        edges.append(edge)
    Graph.add_nodes_from(nodes_name)
    Graph.add_edges_from(edges)

    pos_location = {nodes_name[i]: x for i, x in enumerate(cor_xy)}
    nodes_color_dict = ['r'] + ['gray'] * (data.node_num - 1)
    colorpool = ["turquoise", "slateblue", "cyan", "peru", "gold", "green"]
    edge_color_dict0 = []
    for edge in Graph.edges():
        for typei in range(len(Slist)):
            if edge[0] in Slist[typei] and edge[1] in Slist[typei]:
                edge_color_dict0.append(colorpool[typei])

    e_labels = {}
    for edge0 in edges:
        e_labels[(edge0[0], edge0[1])] = data.dis_matrix[edge0[0], edge0[1]]
    nx.draw_networkx(Graph, pos_location, node_size=200, node_color=nodes_color_dict, edge_color=edge_color_dict0, labels=None,
                     font_size=8)
    
    data_file_path = os.path.join(current_dir, "images", "fig2pdp10.png")
    plt.savefig(data_file_path, dpi=800)
    print("Figure saved to:", data_file_path)
