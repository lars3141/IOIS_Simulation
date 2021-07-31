#!/usr/bin/env python

from experiment import runExperiment
from multiprocessing import Pool
from tqdm import tqdm
import csv

if __name__ == '__main__':
    for i in range(10):
        #set-up pools (number of Threads)
        p = Pool(8)
        intermediate = tqdm(p.imap_unordered(runExperiment, [round(x * 0.01, 2) for x in range(101)]), total=101)
        p.close()
        p.join()
        print(f'Iteration {i + 1} finished.')
        with open('out.csv', 'a', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_NONNUMERIC)
            for r in intermediate:
                writer.writerow(r)