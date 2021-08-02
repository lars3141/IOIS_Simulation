#!/usr/bin/env python

from experiment import runExperiment
from multiprocessing import Pool
from tqdm import tqdm
import csv
import warnings

warnings.filterwarnings("ignore")

if __name__ == '__main__':
    for i in range(10):
        intermediate = set()
        #set-up pools (number of Threads)
        p = Pool(8)
        intermediate = intermediate.union(tqdm(p.imap_unordered(runExperiment, [round(x * 0.01, 2) for x in range(101)]), total=101, desc = f'Itera. {i + 1:02d}'))
        p.close()
        p.join()
        with open('out.csv', 'a', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_NONNUMERIC)
            for r in intermediate:
                writer.writerow(r)