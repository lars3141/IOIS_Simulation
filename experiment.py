#!/usr/bin/env python

import model
# from utility import readCsv

# u = readCsv('disorder.csv')

def runExperiment (value):
    """
    Create a new model with the parameter of interst as input

    Args:
        value: Input value of this experiment
    """
    #set-up the model
    experimentModel = model.IoisModel(
        #complexity = int(round(value * 10, 0))
        #,ambiguity = value
    )

    #run the model
    out1, out2, out3, out4, out5 = experimentModel.run_model()
    return (value, out1, out2, out3, out4, out5)