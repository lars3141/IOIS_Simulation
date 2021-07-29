#!/usr/bin/env python

from experiment import runExperiment
from multiprocessing import Pool
from tqdm import tqdm
import csv

if __name__ == '__main__':
    results = set()
    for i in range(1):
        #set-up pools (number of Threads)
        p = Pool(8)
        results = results.union( tqdm(p.imap_unordered(runExperiment, [round(x * 0.05, 2) for x in range(0,16)]), total=16) )
        p.close()
        p.join()
        print(f'Iteration {i + 1} finished.')

    with open('output.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_NONNUMERIC)
        for r in results:
            writer.writerow(r)