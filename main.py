#!/usr/bin/env python

from experiment import runExperiment
from multiprocessing import Pool
import csv

if __name__ == '__main__':
    results = set()
    for i in range(10):
        #set-up pools (number of Threads)
        p = Pool(8)
        results = results.union(p.map(runExperiment, [round(x * 0.01, 2) for x in range(101)]))
        p.close()
        p.join()
        print(f'Iteration {i + 1} finished.')

    with open('output.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_NONNUMERIC)
        for r in results:
            writer.writerow(r)