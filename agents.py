from mesa import Agent
import numpy as np
from utility import match
from operator import itemgetter
from random import choices

class Actor(Agent):
    """
    An actor, that can take different actions.
    """

    def __init__(self, unique_id, model, tier):
        super().__init__(unique_id, model)
        self.tier = tier
        self.payoffs = 0.0
        self.costs = 0.0

    def use(self, perceived, schedule):
        """
        The agent uses an opportunity

        Args:
            perceived: Perceived vector of current opportunity
            schedule: schedule the actor acts in
        """
        #find matching value of available apps
        results = {edge[1]: (match(schedule.appList[edge[1]].av, perceived), edge) for edge in schedule.network.edges(self.unique_id, data=True) if edge[1] in schedule.appList and
            edge[2]['strength'] >= self.model.useThreshold}
        if len(results) > 0:
            best = max(results.values(), key=itemgetter(0))
            if best[0] >= self.model.complexity:
                #increase strength
                best[1][2]['strength'] = min(best[1][2]['strength'] + self.model.useGain, 1)
                return schedule.appList[best[1][1]]
        return None
    
    def communicate(self, schedule):
        """
        The agent communicates

        Args:
            schedule: schedule the actor acts in
        """
        edgesToAdd = []
        connections = [edge for edge in schedule.network.edges(self.unique_id, data=True) if edge[1] in schedule.actorList and schedule.actorList[edge[1]].tier != self.tier and edge[2]['strength'] >= self.model.commThreshold]
        for s,actorKey,d in connections:

            d['strength'] = min(d['strength'] + self.model.commGain, 1)
            
            for app in set(schedule.network.neighbors(actorKey)) | set(schedule.network.neighbors(s)):
                if app in schedule.appList:
                    try:
                        ownKnow = schedule.network[self.unique_id][app]
                    except KeyError:
                        edgesToAdd.append((self.unique_id, app, schedule.network[actorKey][app]['strength'] * self.model.commDensity))
                        continue
                    try:
                        otherKnow = schedule.network[actorKey][app]
                    except KeyError:
                        edgesToAdd.append((actorKey, app, ownKnow['strength'] * self.model.commDensity))
                        continue
                    diff = ownKnow['strength'] - otherKnow['strength']
                    if diff > 0:
                        otherKnow['strength'] += diff * self.model.commDensity
                    elif diff < 0:
                        ownKnow['strength'] += -diff * self.model.commDensity
                
        schedule.network.add_weighted_edges_from(edgesToAdd, 'strength')

    
    def connect(self, schedule):
        """
        The agent connects

        Args:
            schedule: schedule the actor acts in
        """
        edgesToAdd = []
        for actor in choices([key for key in schedule.actorList if schedule.actorList[key].tier != self.tier], k=self.model.conNumber):
            try:
                schedule.network[self.unique_id][actor]['strength'] = min(schedule.network[self.unique_id][actor]['strength'] + self.model.conGain, 1)
            except KeyError:
                edgesToAdd.append((self.unique_id, actor, self.model.conGain))
        schedule.network.add_weighted_edges_from(edgesToAdd, 'strength')
        schedule.network.add_weighted_edges_from([(a,b,0) for a,b,c in edgesToAdd], 'time')
                
    def build(self, perceived, schedule):
        """
        The agent builds a new application

        Args:
            perceived: Perceived vector of current opportunity
            schedule: schedule the actor acts in
        """
        newApp = Application(schedule.get_highest_id()+1, self.model, perceived, schedule.time)
        schedule.add(newApp)
        schedule.network.add_weighted_edges_from([(newApp.unique_id, self.unique_id, 1.0)], 'strength')
        return newApp

    def step(self, perceived ,schedule):
        """
        One step of the actor, including use of applcations, 
        communication to peer, connectio to new peers and build of a new application.

        Args:
            perceived: Perceived vector of current opportunity
            schedule: schedule the actor acts in
        """
        aBest = None
        i = self.model.patience
        use = True
        while i > 0 and aBest is None:
            if np.random.random(1)[0] <= self.model.cUse:
                if use:
                    use = False
                    aBest = self.use(perceived, schedule)
                    if aBest is not None:
                        break
                    i -= 1
                if np.random.random(1)[0] <= self.model.cCommunicate:
                    use = True
                    self.communicate(schedule)
                    i -= 1
                    continue
                if np.random.random(1)[0] <= self.model.cConnect:
                    self.connect(schedule)
                    i -= 1
                    continue
            i -= 1
        if np.random.random(1)[0] <= self.model.cBuild and aBest is None:
            aBest = self.build(perceived, schedule)
            self.costs += self.model.buildCost
        return aBest



class Application(Agent):
    """
    An IT Application
    """
    
    def __init__(self
        , unique_id
        , model
        , perceived
        , time
    ):
        super().__init__(unique_id, model)
        self.av = self.build_vector(np.copy(perceived)) #perceived opportunity, app is build on
        self.birth = time
        self.lastUsed = time
        
    def build_vector(self, perceived):
        """
        Helping methode to create a new application vector

        Args:
            perceived: Perceived vector of current opportunity

        Returns:
            application vector
        """
        array = perceived.astype(str)
        while np.count_nonzero(array == '?') < self.model.improvisation:
            array[np.random.randint(0, array.size)] = '?'
        return tuple(array)
    
    def improvise(self):
        """
        Improvisation of application vector

        Args:
            perceived: Perceived vector of current opportunity
        
        Returns:
            improvised vector
        """
        return tuple([np.random.randint(0, 2) if p == '?' else int(p) for p in np.copy(self.av)])

    def cost(self, schedule):
        """
        Total cost of application usage

        Args:
            schedule: schedule the application exists in
        
        Returns:
            total cost of application
        """
        #cost of connection
        cost = np.sum([1 for actor in schedule.network.neighbors(self.unique_id) if actor in schedule.actorList])
        #cost of age
        cost =+ schedule.time - self.birth
        return cost