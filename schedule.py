from mesa.time import RandomActivation
import environment
import agents
import numpy as np
import utility
import networkx as nx
from random import choice
#import snap

class RandomActivationByTier(RandomActivation):
    """
    A scheduler which activates each type of agent once per step, in random
    order, with the order reshuffled every step.

    Assumes that all agents have a step() method.
    """

    def __init__(self, model):
        super().__init__(model)
        self.network = nx.Graph()
        self.actorList = {}
        self.appList = {}
        self.allOpportunities = {
            1 : environment.OpportunityCollection(model),
            2 : environment.OpportunityCollection(model),
            3 : environment.OpportunityCollection(model),
            4 : environment.OpportunityCollection(model)
        }

    def add(self, agent):
        """
        Add an Agent object to the schedule

        Args:
            agent: An Agent to be added to the schedule.
        """

        id = agent.unique_id
        self._agents[id] = agent
        self.network.add_node(id)
        if isinstance(agent, agents.Actor):
            self.actorList[id] = agent
        elif isinstance(agent, agents.Application):
            self.appList[id] = agent

    def remove(self, keys):
        """
        Remove the given agent from the schedule.
        """
        self.network.remove_nodes_from(keys)
        for key in keys:
            if isinstance(self._agents[key], agents.Actor):
                del self.actorList[key]
            elif isinstance(self._agents[key], agents.Application):
                del self.appList[key]
            del self._agents[key] # delete more efficient

    def step(self):
        """
        Executes the step of each agent tier, one at a time, in random order.

        """
        self.allOpportunities[1].newRandomOpportunities(self.time)

        for u,v,d in self.network.edges(data=True):
            if v in self.actorList:
                d['strength'] *= (1-self.model.decreaseStrength)
                if d['strength'] >= self.model.commThreshold:
                    d['time'] += 1
                else:
                    d['time'] = 0
            else:
                d['strength'] *= (1-self.model.decreaseKnowledge)
            
        for op in self.allOpportunities.values():
            op.removeOld(self.time)

        toDelete = [key for key in self.appList if self.appList[key].lastUsed < self.time - 10]
        if len(toDelete) > 0:
            self.remove(toDelete)

        for tier in range(1, max([agent.tier for agent in self.actorList.values()])+1):
            keys = [key for key in self.actorList if self.actorList[key].tier == tier]
            self.model.random.shuffle(keys)
            for key in keys:
                try:
                    opportunity = choice(self.allOpportunities[tier].opportunities)
                except IndexError:
                    continue
                app = self.actorList[key].step(opportunity.perceive(), self)
                if app is not None:
                    realized = app.improvise()
                    
                    cost = app.cost(self)
                    if opportunity.payoff > cost:
                        self.actorList[key].costs += cost
                        if utility.match(opportunity.vector, realized) >= self.model.complexity:
                            app.lastUsed = self.time
                            self.actorList[key].payoffs += opportunity.payoff
                            self.allOpportunities[tier+1].addOpportunity(self.time, realized)
        self.steps += 1
        self.time += 1

    def get_highest_id(self):
        return max(self._agents.keys())

    def getAppCount(self):
        return len(self.appList)

    def getAllPayoffs(self):
        return np.sum([self.actorList[key].payoffs for key in self.actorList])
    
    def getAllCosts(self):
        return np.sum([self.actorList[key].costs for key in self.actorList])

    def getActorConnections(self):
        return len([edge for edge in self.network.edges(data=True) if edge[1] in self.actorList 
            and edge[2]['strength'] >= self.model.commThreshold])
    
    def getAppConnections(self):
        return len([edge for edge in self.network.edges(data=True) if edge[1] in self.appList 
            and edge[2]['strength'] >= self.model.commThreshold])