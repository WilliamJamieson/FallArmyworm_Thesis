import dataclasses  as dclass
import collections  as collect
import numpy.random as rnd
import scipy.stats  as stats

import source.hint    as hint
import source.keyword as keyword

import source.agents.adult    as adult
import source.agents.egg_mass as egg_mass
import source.agents.larva    as larva
import source.agents.pupa     as pupa


@dclass.dataclass
class Immigration(object):
    """
    Class to handle immigration of agents into the model
        - this is to prevent extinction of a given genotype
        - this is a constant input
        - the number of immigrants is drawn from a Poisson Distribution

    Variables:
        lam:       the mean number of immigrants each day
        genotype:  the genotype key of the agent to immigrate
        agent_key: type of agent to immigrate

    Methods:
        immigration: run immigration
    """

    lam:      float
    genotype: str
    agent_key: str

    def _number(self) -> int:
        """
        Get the number of immigrants

        Returns:
            the number of immigrants
        """

        return int(stats.poisson.rvs(self.lam))

    def _immigrate_egg_masses(self, simulation: hint.simulation) -> None:
        """
        Create and add immigrant egg_masses

        Args:
            simulation: the simulation

        Effects:
            adds the egg_masses
        """

        number = self._number()
        for _ in range(number):
            unique_id = simulation.new_unique_id()
            new       = egg_mass.EggMass.setup(unique_id,
                                               keyword.immigrant,
                                               simulation,
                                               self.genotype)
            new.activate()

    def _immigrate_larvae(self, simulation: hint.simulation) -> None:
        """
        Create and add immigrant larvae

        Args:
            simulation: the simulation

        Effects:
            adds the larvae
        """

        number = self._number()
        for _ in range(number):
            unique_id = simulation.new_unique_id()
            new       = larva.Larva.setup(unique_id,
                                          keyword.immigrant,
                                          simulation,
                                          self.genotype)
            new.activate()

    def _immigrate_pupae(self, simulation: hint.simulation) -> None:
        """
        Create and add immigrant pupae

        Args:
            simulation: the simulation

        Effects:
            adds the pupae
        """

        number = self._number()
        for _ in range(number):
            unique_id = simulation.new_unique_id()
            new       = pupa.Pupa.setup(unique_id,
                                        keyword.immigrant,
                                        simulation,
                                        self.genotype)
            new.activate()

    def _immigrate_adults(self, simulation: hint.simulation) -> None:
        """
        Create and add immigrant adults

        Args:
            simulation: the simulation

        Effects:
            adds the adults
        """

        number = self._number()
        for _ in range(number):
            unique_id = simulation.new_unique_id()
            new       = adult.Adult.setup(unique_id,
                                          keyword.immigrant,
                                          simulation,
                                          self.genotype)
            new.activate()

    def _immigrate_pregnant(self, simulation: hint.simulation) -> None:
        """
        Create and add immigrant pregnant

        Args:
            simulation: the simulation

        Effects:
            adds the pregnant
        """

        if self.genotype == keyword.hetero:
            parents = [keyword.homo_r, keyword.homo_s]
        else:
            parents = [self.genotype, self.genotype]

        number = self._number()
        for _ in range(number):
            rnd.shuffle(parents)
            unique_id = simulation.new_unique_id()
            new       = adult.Adult.setup(unique_id,
                                          keyword.immigrant,
                                          simulation,
                                          parents[0], parents[1])
            new.activate()

    def immigration(self, simulation: hint.simulation) -> None:
        """
        Create and add the agents to immigrate

        Args:
            simulation: the simulation

        Effects:
            immigrates agents into the agent's feed
        """

        if self.agent_key == keyword.egg_mass:
            self._immigrate_egg_masses(simulation)
        elif self.agent_key == keyword.larva:
            self._immigrate_larvae(simulation)
        elif self.agent_key == keyword.pupa:
            self._immigrate_pupae(simulation)
        elif self.agent_key == keyword.adult:
            self._immigrate_adults(simulation)
        elif self.agent_key == keyword.pregnant:
            self._immigrate_pregnant(simulation)


class Immigrations(collect.UserList):
    """
    Class to handle all the different immigration systems:

    Variables:
        - list: of all immigrations

    Methods:
        immigration: call all of the immigration classes

    Constructors:
        setup: setup the class
    """

    def __init__(self, immigration_list: hint.immigration_list):
        super().__init__(immigration_list)

    def immigration(self, simulation: hint.simulation) -> None:
        """
        Run immigration systems on agents

        Args:
            simulation: the simulation

        Effects:
            run all forms of immigration
        """

        for immigration in self:
            immigration.immigration(simulation)

    @classmethod
    def setup(cls, setup_tuples: hint.immigration_tuples) -> 'Immigrations':
        """
        Setup the immigration system

        Args:
            setup_tuples: list of setup arguments

        Returns:
            setup class
        """

        immigrations = []
        for setup in setup_tuples:
            immigrations.append(Immigration(*setup))

        return cls(immigrations)
