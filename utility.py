import csv
import agents
import numpy as np

def readCsv(path):
    d = dict()
    with open(path, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quoting=csv.QUOTE_NONNUMERIC)
        for row in reader:
            d[row[0]] = row[1]
    return d

def match(v1, v2):
    sum = 0.0
    for a,b in zip(v1, v2):
        if a == '?':
            sum += 0.5
        elif int(a) == b:
            sum += 1.0
    return sum

def applicationCost(application, schedule):
    cost = np.sum([1 for actor in schedule.network.neighbors(application.unique_id) if actor in schedule.actorList])
    cost =+ schedule.time - application.birth
    return cost