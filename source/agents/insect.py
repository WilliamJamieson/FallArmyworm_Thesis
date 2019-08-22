import dataclasses as dclass
import itertools   as i_tools

import source.hint    as hint
import source.keyword as keyword

import source.agents.agent as agent


@dclass.dataclass
class Insect(agent.Agent):
    """
    Base class to for insect agents
        - inherits from base agent class

    Variables:
        mass:     the agent's mass
        genotype: the agent's genotype
        age:      agent's age
        death:    agent's death state

    Methods:
        advance_age: have the insect advance it's age
    """

    mass:     float
    genotype: str
    age:      int
    death:    str

    def __post_init__(self):
        """Setup some helper systems"""

        self._age_count = i_tools.count(self.age + 1)

    @property
    def bt(self) -> str:
        """Get the bt state of the plant"""

        loc = self.location[:keyword.bt_depth]

        return self.simulation.agents[loc.location_key].environment.bt

    @property
    def plant(self) -> float:
        """Get the mass of the plant"""

        loc = self.location[:keyword.plant_depth]

        return self.simulation.agents[loc.location_key].environment.plant

    def advance_age(self) -> hint.agent_list:
        """
        Advance the age of the agent as a behavior

        Effects:
            advances age by 1

        Returns:
            empty list
        """

        self.age = next(self._age_count)

        return []

    def die(self, death: str = '') -> None:
        """
        Have agent die

        Args:
            death: the type of death

        Effects:
            sets alive to false
            sets death to the death
            deactivates agent
        """

        self.death = death
        super().die()
