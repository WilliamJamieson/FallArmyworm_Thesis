import dataclasses  as dclass
import collections  as collect
import numpy.random as rnd
import scipy.stats  as stats

import source.hint    as hint
import source.keyword as keyword

import source.space.location as agent_location


@dclass.dataclass
class Emigration(object):
    """
    Class to handle emigration of agents out of model
        - this is to limit the reproductive complexities in the model

        - Assumes the population should be normally distributed

    Variables:
        mu:         average adult population that is allowed
        sigma:      standard deviation in that population
        agent_keys: agent_keys for the population

    Methods:
        emigration: run emigration
    """

    location = agent_location.Location([0]).location_key

    mu:         float
    sigma:      float
    agent_keys: hint.agent_keys

    def _remove(self, population: int) -> bool:
        """
        Determine if the agent emigrates

        Args:
            population: the current population of agents

        Returns:
            if the agent migrates
        """

        return rnd.random() <= stats.norm.cdf(population,
                                              loc=self.mu, scale=self.sigma)

    def _emigrate(self, agent:      hint.agent,
                        population: int) -> int:
        """
        Determine if the adult agent emigrates

        Args:
            agent:      the agent in question
            population: the current population

        Effects:
            emigrates the agent or not

        Returns:
            new population
        """

        if self._remove(population):
            agent.die(keyword.emigrate)

            return population - 1
        else:
            return population


    def _agents(self, agents: hint.agents) -> hint.agent_list:
        """
        Get the current agents

        Args:
            agents: the agents system

        Returns:
            the list of agents
        """

        population = []
        for agent_key in self.agent_keys:
            population.extend(agents[self.location][agent_key].agents)

        return population

    def emigration(self, agents: hint.agents) -> None:
        """
        Emigrate agents out of system

        Args:
            agents: the space agents system

        Effects:
            removes a collection of agents from the system
        """

        population = self._agents(agents)
        pop        = len(population)

        for agent in population:
            pop = self._emigrate(agent, pop)


class Emigrations(collect.UserList):
    """
    Class to handle all the different emigration systems:

    Variables:
        - list: of all emigrations

    Methods:
        emigration: call all of the Emigration classes
    """

    def __init__(self, emigration_list: hint.emigration_list):
        super().__init__(emigration_list)

    def emigration(self, agents:  hint.agents) -> None:
        """
        Run emigration systems on agents

        Args:
            agents: the agents system

        Returns:
            list of agents to emigrate out of system
        """

        for emigration in self:
            emigration.emigration(agents)

    @classmethod
    def setup(cls, setup_tuples: hint.emigration_tuples) -> 'Emigrations':
        """
        Setup the emigration system

        Args:
            setup_tuples: list of setup arguments

        Returns:
            setup class
        """

        emigrations = []
        for setup in setup_tuples:
            emigrations.append(Emigration(*setup))

        return cls(emigrations)
