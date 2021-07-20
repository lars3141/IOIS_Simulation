#!/usr/bin/env python

import model
from utility import readCsv

# u = readCsv('disorder.csv')

def runExperiment (range):
    experimentModel = model.IoisModel(
        cCommunicate = range
    )

    out1, out2, out3, out4, out5 = experimentModel.run_model()
    return range, out1, out2, out3, out4, out5