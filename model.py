from mesa import Model
from mesa.datacollection import DataCollector
import numpy as np

import agents
import schedule

class IoisModel(Model):

    def __init__(self
        ,velocity = 60 #Experiment 1
        ,unpredictability = 0.7569961461910347 # Experiment 1
        ,ambiguity = 0.1 # Experiment 2
        ,complexity = 6 # Experiment 2
        ,meanPayoff = 30
        ,sdPayoff = 5
        ,meanDuration = 20
        ,sdDuration = 5
        ,improvisation = 3
        ,patience = 6
        ,cUse = 0.8 # Experiment
        ,cCommunicate = 0.6 # Experiment
        ,cConnect = 0.6 # Experiment
        ,cBuild = 0.6 # Experiment
        ,useThreshold = 0.6
        ,useGain = 0.2
        ,commDensity = 0.5
        ,commThreshold = 0.4
        ,commGain = 0.2
        ,conNumber = 5
        ,conGain = 0.4
        ,buildCost = 60
        ,decreaseStrength = 0.1
        ,decreaseKnowledge = 0.1
        ,initialActors = 120

        ,verbose = False
    ):
        """
        Create a new model with the given parameters.

        Args:
            velocity: velocity with which opportunities appear
            unpredictability: unpredictability of opportunities
            ambiguity: ambigutity of opportunities
            complexity: complexity of environment
            meanPayoff: average payoff of opportunities
            sdPayoff: standart deviation of payoff of opportunities
            meanDuration: average duration of opportunities
            sdDuration: standart deviation of duration of opportunities
            improvisation: improvisation, determining number of '?' in AV
            patience: patience of actor, how of steps are conducted when no application is found
            cUse: chance to use application
            cCommunicate: chance to of an actor to communicate
            cConnect: chance to of an actor to connect to other actors
            cBuild: chance to of an actor to build a new application
            useThreshold: knowledge needed to use application
            useGain: knowledge gained when application is used
            commNumber: number of actors with which one communicates
            commDensity: how much information is shared in a communication
            commThreshold: strength of connection needed to communicate
            commGain: strength of connection gained when communicating
            conNumber: number of connections gained when connecting
            conGain: strength of connection gained when connecting
            buildCost: cost to build a new application
            decreaseStrength: strength decreased in every step in %
            decreaseKnowledge: knowledge decreased in every step in %
            initialActors: initial actors in the system
        """
        super().__init__()
        
        self.velocity = velocity
        self.unpredictability = unpredictability
        self.meanPayoff = meanPayoff
        self.sdPayoff = sdPayoff
        self.meanDuration = meanDuration
        self.sdDuration = sdDuration
        self.ambiguity = ambiguity
        self.improvisation = improvisation
        self.patience = patience
        self.cUse = cUse
        self.cCommunicate = cCommunicate
        self.cConnect = cConnect
        self.cBuild = cBuild
        self.complexity = complexity
        self.useThreshold = useThreshold
        self.useGain = useGain
        self.commDensity = commDensity
        self.commThreshold = commThreshold
        self.commGain = commGain
        self.conNumber = conNumber
        self.conGain = conGain
        self.buildCost = buildCost
        self.decreaseStrength = decreaseStrength
        self.decreaseKnowledge = decreaseKnowledge
        self.initialActors = initialActors

        self.verbose = verbose
 
        self.schedule = schedule.RandomActivationByTier(self)

        # Create actors:
        for i in range(self.initialActors):
            self.schedule.add(agents.Actor(i, self, (i % 3) + 1))

        self.avgApps = 0.0
        self.avgAppCon = 0.0
        self.avgActorConTime = 0.0

    def step(self):
        self.schedule.step()

        if self.verbose:
            print(
                [
                    "Time: ", self.schedule.time,
                    "Apps: ", self.schedule.getAppCount(),
                    "Pay: ", self.schedule.getAllPayoffs(),
                    "Cost", self.schedule.getAllCosts(),
                    "Actor Connections", self.schedule.getActorConnections(),
                    "Application Connections", self.schedule.getAppConnections()
                ]
            )

    def run_model(self, step_count=300, exp_begin=100):

        for i in range(step_count):
            #zero all cash-flow counters
            if i == exp_begin:
                for actor in self.schedule.actorList.values():
                    actor.payoffs = 0.0
                    actor.costs = 0.0
            #run step
            self.step()
            #collect data
            if i >= exp_begin:
                self.avgApps = (self.schedule.getAppCount() + self.avgApps * (i-exp_begin))/(i-exp_begin+1)
                self.avgAppCon = (self.schedule.getAppConnections() + self.avgAppCon * (i-exp_begin))/(i-exp_begin+1)
                self.avgActorConTime = (np.average([d['time'] for u,v,d in self.schedule.network.edges(data=True) if v in self.schedule.actorList and d['time'] > 0])
                    + self.avgActorConTime * (i-exp_begin))/(i-exp_begin+1)

        if self.verbose:
            print("")
            print("Average # Apps: ", self.avgApps)
            print("Average # App Connections: ", self.avgAppCon)
            print("Accumulated Payoffs: ", self.schedule.getAllPayoffs())
            print("Accumulated Costs: ", self.schedule.getAllCosts()),
            print("Average Actor Connection Time: ", self.avgActorConTime)

        return (
            self.avgApps
            ,self.avgAppCon
            ,self.schedule.getAllPayoffs()
            ,self.schedule.getAllCosts()
            ,self.avgActorConTime
        )
