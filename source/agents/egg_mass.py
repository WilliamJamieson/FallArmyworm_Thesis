import dataclasses  as dclass
import collections  as collect
import itertools    as i_tools
import numpy        as np
import numpy.random as rnd

import source.hint    as hint
import source.keyword as keyword

import source.agents.agent as agent
import source.agents.egg   as agent_egg


class Eggs(collect.UserList):
    """
    Class to handle the eggs for an egg_mass

    Variables:
        - list:
            list of eggs in class

        mass: mass of single egg
    """

    def __init__(self, eggs: hint.eggs,
                       mass: float):
        super().__init__(eggs)

        self.mass = mass

    def activate(self) -> None:
        """
        Activate the eggs in list in simulation

        Effects:
            activates all the eggs
        """

        for egg in self:
            egg.activate()

    def deactivate(self) -> None:
        """
        Deactivate the eggs in list in simulation

        Effects:
            deactivates all the eggs
        """

        for egg in self:
            egg.deactivate()

    def cannibalize(self, number: int) -> None:
        """
        Cannibalize a number of eggs

        Args:
            number: the number of eggs to cannibalize

        Effects:
            randomly remove that number of eggs
        """

        rnd.shuffle(self)

        for index in range(number):
            self[index].die(keyword.cannibalism)

    @classmethod
    def initialize(cls, egg_mass:  hint.egg_mass,
                        genotypes: hint.genotypes,
                        mass:      float) -> 'Eggs':
        """
        Initialize a collection of eggs for egg_mass

        Args:
            egg_mass:   the egg_mass
            mass:       the mass for each egg
            genotypes:  the list of egg genotypes

        Returns:
            a setup collection of eggs
        """

        eggs = []
        for genotype in genotypes:
            unique_id  = egg_mass.new_unique_id()
            simulation = egg_mass.simulation
            location   = egg_mass.location.copy()

            new = agent_egg.Egg.initialize(unique_id,
                                           simulation,
                                           location,
                                           mass,
                                           genotype,
                                           egg_mass)
            eggs.append(new)

        return cls(eggs, mass)


@dclass.dataclass
class EggMass(agent.Agent):
    """
    Base class to for insect agents
        - inherits from base agent class

    Variables:
        eggs: list of eggs in egg_mass
        active: determine if this is active
    """

    eggs: hint.egg_mass_eggs

    def __post_init__(self):
        """Setup some helper systems"""

        self._id_count = i_tools.count()

    @property
    def active(self) -> bool:
        """Determine if this egg mass is still active"""

        return (len(self.eggs) > 0) and self.alive

    @property
    def inactive(self) -> bool:
        """Determine if this egg mass is not active"""

        return (len(self.eggs) <= 0) and self.alive

    @property
    def mass(self) -> float:
        """Get the total mass of egg_mass"""

        return len(self.eggs) * self.eggs.mass

    def activate(self) -> None:
        """
        Activate this egg_mass and all its eggs in the simulation

        Effects:
            activates this agent
        """

        super().activate()
        self.eggs.activate()

    def deactivate(self) -> None:
        """
        Deactivate this egg_mass and all its eggs in the simulation

        Effects:
            deactivates this agent
        """

        super().deactivate()
        self.eggs.deactivate()

    def _feed_number(self, amount: float) -> int:
        """
        Get the number of eggs to feed on

        Args:
            amount: the amount of mass to remove

        Returns:
            the number of eggs to remove
        """

        raw   = amount/self.eggs.mass
        ceil  = int(np.ceil( raw))
        floor = int(np.floor(raw))

        number = len(self.eggs)

        if ceil <= number:
            return ceil
        elif floor <= number:
            return floor
        else:
            raise RuntimeError('Tried to consume too much egg')

    def feed(self, amount: float) -> None:
        """
        Feed on amount of eggs

        Args:
            amount: amount to eat

        Effects:
            Cannibalizes amount of eggs
        """

        number = self._feed_number(amount)
        self.eggs.cannibalize(number)

        if self.inactive:
            self.deactivate()

    def remove(self, egg: hint.egg) -> None:
        """
        Remove the egg from the egg_mass

        Args:
            egg: the egg to remove

        Effects:
            removes the egg from the class
        """

        self.eggs.remove(egg)

    def reset(self) -> hint.agent_list:
        """
        Reset the agent

        Effects:
            reset the agent if needed
        """

        if self.inactive:
            self.deactivate()

        return []

    def new_unique_id(self) -> str:
        """
        Create a new unique_id

        Returns:
            a unique_id
        """

        return '{}{}'.format(self.unique_id, next(self._id_count))

    @staticmethod
    def _alleles(genotype: str) -> hint.alleles:
        """
        Get the alleles for the given genotype

        Args:
            genotype: the genotype_key

        Returns:
            tuple of alleles
        """

        if genotype == keyword.homo_r:
            return keyword.homo_r_alleles
        elif genotype == keyword.hetero:
            return keyword.hetero_alleles
        elif genotype == keyword.homo_s:
            return keyword.homo_s_alleles
        else:
            raise RuntimeError('Invalid genotype_key: {}'.format(genotype))

    @staticmethod
    def _generate_genotype(mother_alleles: hint.alleles,
                           father_alleles: hint.alleles) -> str:
        """
        Generate the genotype

        Args:
            mother_alleles: the mother's alleles
            father_alleles: the father's alleles

        Returns:
            a new genotype
        """

        mother = rnd.choice(mother_alleles)
        father = rnd.choice(father_alleles)

        allele_key = mother + father

        if allele_key == keyword.homo_r_value:
            return keyword.homo_r
        elif allele_key == keyword.hetero_value:
            return keyword.hetero
        else:
            return keyword.homo_s

    def genotypes(self, number: int,
                        mother: str,
                        father: str) -> hint.genotypes:
        """
        Generate a list of genotypes from the mother and father

        Args:
            number: number to make
            mother: mother's genotype_key
            father: father's genotype_key

        Returns:
            list of genotypes
        """

        mother_alleles = self._alleles(mother)
        father_alleles = self._alleles(father)

        genotypes = []
        for _ in range(number):
            genotypes.append(self._generate_genotype(mother_alleles,
                                                     father_alleles))

        return genotypes

    @classmethod
    def empty(cls, unique_id:  str,
                   simulation: hint.simulation,
                   location:   hint.location) -> 'EggMass':
        """
        Initialize a new egg_mass without realized eggs_system

        Args:
            unique_id:  the agent's unique_id
            simulation: the master simulation
            location:   the agent's location

        Returns:
            An empty egg_mass system
        """

        agent_key = keyword.egg_mass
        alive     = True

        eggs = Eggs([], -1)

        return cls(agent_key, unique_id, simulation, location, alive, eggs)

    @classmethod
    def initialize(cls, unique_id:  str,
                        simulation: hint.simulation,
                        location:   hint.location,
                        mother:     str,
                        father:     str) -> 'EggMass':
        """
        Initialize a new egg_mass agent

        Args:
            unique_id:  the agent's unique_id
            simulation: the master simulation
            location:   the agent's location
            mother:     mother's genotype_key
            father:     father's genotype_key

        Returns:
            a fully initialized egg_mass
        """

        new = cls.empty(unique_id, simulation, location)

        number    = simulation.models[keyword.init_num](mother)
        mass      = simulation.models[keyword.init_mass](number, mother)
        genotypes = new.genotypes(number, mother, father)
        new.eggs  = Eggs.initialize(new, genotypes, mass)

        return new

    @classmethod
    def setup(cls, unique_id_num: int,
                   initial_key:   str,
                   simulation:    hint.simulation,
                   genotype:      str) -> 'EggMass':
        """
        Setup an initial population egg_mass

        Args:
            unique_id_num: unique_id number
            initial_key:   key for where agent was initialized
            simulation:    the master simulation
            genotype:      the effective genotypes of eggs

        Returns:
            a egg_mass initialized by a population
        """

        if genotype == keyword.hetero:
            parents = [keyword.homo_r, keyword.homo_s]
        else:
            parents = [genotype, genotype]
        rnd.shuffle(parents)

        unique_id = '{}{}{}'.format(initial_key,
                                    unique_id_num,
                                    keyword.egg_mass)
        location  = simulation.space.new_location(keyword.egg_depth)

        return cls.initialize(unique_id, simulation, location,
                              parents[0], parents[1])

    @classmethod
    def birth(cls, adult: hint.adult) -> 'EggMass':
        """
        Create an egg_mass from this adult

        Args:
            adult: the adult in question

        Returns:
            a brand new egg_mass
        """

        unique_id  = adult.new_unique_id()
        simulation = adult.simulation
        location   = adult.new_egg_location()
        mother     = adult.genotype
        father     = adult.mate

        return cls.initialize(unique_id, simulation, location, mother, father)
