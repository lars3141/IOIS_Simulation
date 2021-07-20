import numpy as np
from random import choices

class Opportunity:
    """
    An opportunity
    """

    def __init__(self
        ,time
        ,model
        ,vector = None
    ):
        self.model = model
        if vector is None:
            self.vector = tuple(choices([0,1], weights=[model.unpredictability, 1 - model.unpredictability], k=10))
        else:
            self.vector = tuple(map(int, vector))
        self.payoff = np.random.normal(model.meanPayoff, model.sdPayoff)
        self.duration = np.random.normal(model.meanDuration, model.sdDuration)
        self.birth = time

    def perceive(self):
        out = np.copy(self.vector)
        for i in range(0, out.size):
            if np.random.binomial(1, self.model.ambiguity) == 1:
                out[i] = abs(out[i] - 1)
        return out

class OpportunityCollection:

    def __init__(self, model):
        self.opportunities = []
        self.model = model

    def newRandomOpportunities(self ,time):
        for i in range(0, np.random.poisson(self.model.velocity)):
            self.opportunities.append(Opportunity(time, self.model))

    def addOpportunity(self, time, vector = None):
        self.opportunities.append(Opportunity(time, self.model, vector))

    def removeOld (self, time):
        self.opportunities = [opp for opp in self.opportunities if opp.birth + opp.duration >= time]