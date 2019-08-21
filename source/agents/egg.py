import dataclasses as dclass

import source.hint    as hint
import source.keyword as keyword

import source.agents.insect as insect


@dclass.dataclass
class Egg(insect.Insect):
    """
    Class to contain an egg agent
        - inherits from base insect class

    Variables:
        egg_mass:    the egg_mass this egg belongs to
        survival:    survival system
        development: development system

    Methods:
        survive: have the egg survive
        develop: have the egg develop
    """

    egg_mass:    hint.egg_mass
    survival:    hint.egg_survival
    development: hint.egg_development

    def deactivate(self) -> None:
        """
        Deactivate the agent

        Effects:
            adds    agent to   inactive
            removes agent from active   (if there)
        """

        super().deactivate()
        self.egg_mass.remove(self)

    def survive(self) -> hint.agent_list:
        """
        Run the survive behavior

        Effects:
            run behavior to determine if this survives

        Returns:
            empty list
        """

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

        self.development.develop(self)

        return []

    @classmethod
    def initialize(cls, unique_id:  str,
                        simulation: hint.simulation,
                        location:   hint.location,
                        mass:       float,
                        genotype:   str,
                        egg_mass:   hint.egg_mass) -> 'Egg':
        """
        Initialize a new egg agent

        Args:
            unique_id:  the agent's unique_id
            simulation: the master simulation
            location:   the agent's location
            mass:       the agent's mass
            genotype:   the agent's genotype
            egg_mass:   the egg_mass for egg

        Returns:
            A fully initialized agent
        """

        agent_key = keyword.egg
        alive    = True
        age      = 0
        death    = keyword.alive

        survival    = simulation.behaviors.survive_egg
        development = simulation.behaviors.develop_egg

        return cls(agent_key, unique_id, simulation, location,
                   alive, mass, genotype, age, death, egg_mass,
                   survival, development)
