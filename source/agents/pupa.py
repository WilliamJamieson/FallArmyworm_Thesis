import dataclasses as dclass

import source.hint    as hint
import source.keyword as keyword

import source.agents.insect as insect


@dclass.dataclass
class Pupa(insect.Insect):
    """
    Class to contain a pupa agent
        - inherits from base insect class

    Variables:
        survival:    survival system
        development: development system

    Methods:
        survive:   have the pupa survive
        develop:   have the pupa develop
    """

    survival:    hint.pupa_survival
    development: hint.pupa_development

    def survive(self) -> hint.agent_list:
        """
        Run the survive behavior

        Effects:
            run behavior to determine if this survives

        Returns:
            empty list
        """

        if self.alive:
            self.survival.survive(self)

        return []

    def develop(self) -> hint.agent_list:
        """
        Run the develop behavior

        Effects:
            run behavior to determine if this develops

        Returns:
            empty list
        """

        if self.alive:
            self.development.develop(self)

        return []

    @classmethod
    def initialize(cls, unique_id:  str,
                        simulation: hint.simulation,
                        location:   hint.location,
                        mass:       float,
                        genotype:   str) -> 'Pupa':
        """
        Initialize a new pupa agent

        Args:
            unique_id:  the agent's unique_id
            simulation: the master simulation
            location:   the agent's location
            mass:       the agent's mass
            genotype:   the agent's genotype

        Returns:
            A fully initialized agent
        """

        agent_key = keyword.pupa
        alive    = True
        age      = 0
        death    = keyword.alive

        survival    = simulation.behaviors.survive_pupa
        development = simulation.behaviors.develop_pupa

        return cls(agent_key, unique_id, simulation, location,
                   alive, mass, genotype, age, death,
                   survival, development)

    @classmethod
    def setup(cls, unique_id_num: int,
                   initial_key:   str,
                   simulation:    hint.simulation,
                   genotype:      str) -> 'Pupa':
        """
        Setup an initial population pupa

        Args:
            unique_id_num: unique_id number
            initial_key:   key for where agent was initialized
            simulation:    the master simulation
            genotype:      the agent's genotype

        Returns:
            a pupa initialized by a population
        """

        unique_id = '{}{}{}'.format(initial_key,
                                    unique_id_num,
                                    keyword.pupa)
        location  = simulation.space.new_location(keyword.pupa_depth)
        mass      = simulation.models[keyword.init_mature](genotype)

        return cls.initialize(unique_id, simulation, location, mass, genotype)

    @classmethod
    def advance(cls, larva: hint.larva) -> 'Pupa':
        """
        Create a pupa agent for this larva

        Args:
            larva: the larva in question

        Returns:
            A pupa version of this larva
        """

        location = larva.location[:keyword.pupa_depth]

        return cls.initialize(larva.unique_id,
                              larva.simulation,
                              location,
                              larva.mass,
                              larva.genotype)
