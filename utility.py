import csv
import numpy as np

def readCsv(path):
    """
    Helping methode to read a Csv as Dict 

    Args:
        path: path of the csv incl. file name
    """
    with open('disorder.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quoting=csv.QUOTE_NONNUMERIC)
        return {row[0]: row[1] for row in reader}

def match(v1, v2):
    """
    Helping methode to match two different vectors and calculate the matching score

    Args:
        v1: Application vector or numerical vector (perceived, opportunity, realized)
        v2: Numerical vector (perceived, opportunity, realized)
    """
    sum = 0.0
    for a,b in zip(v1, v2):
        if a == '?':
            sum += 0.5
        elif int(a) == b:
            sum += 1.0
    return sum