import dataclasses  as dclass
import itertools    as i_tools
import numpy.random as rnd
import pickle       as pk

import source.hint    as hint
import source.keyword as keyword

import source.agents.adult    as adult
import source.agents.egg_mass as egg_mass
import source.agents.larva    as larva
import source.agents.pupa     as pupa


@dclass.dataclass
class Simulation(object):
    """
    Class to contain the whole simulation:
    """

    space:       hint.space
    agents:      hint.agents
    schedule:    hint.schedule
    models:      hint.models
    behaviors:   hint.behaviors
    database:    hint.database
    emigration:  hint.emigrations
    immigration: hint.immigrations

    timestep: int = 0

    def __post_init__(self):
        """Setup some helper systems"""

        self._id_count   = i_tools.count()

    def count_step(self) -> int:
        """
        Count a step

        Returns:
            the step count
        """

        self.timestep += 1

        return self.timestep

    def new_unique_id(self) -> int:
        """
        Generate a new unique_id

        Returns:
            a new unique_id
        """

        return next(self._id_count)

    def populate_egg_masses(self, nums: hint.init_pop) -> None:
        """
        Create initial egg_masses

        Args:
            nums: (num_homo_r, num_hetero, num_homo_s)

        Effects:
            adds egg_masses of the different amounts to the simulation
        """

        for index, genotype in enumerate(keyword.genotype_keys):
            for _ in range(nums[index]):
                unique_id = self.new_unique_id()
                new       = egg_mass.EggMass.setup(unique_id,
                                                   keyword.init,
                                                   self,
                                                   genotype)
                new.activate()

    def populate_larvae(self, nums: hint.init_pop) -> None:
        """
        Create the initial larvae

        Args:
            nums: (num_homo_r, num_hetero, num_homo_s)

        Effects:
            adds larvae of the different amounts to the simulation
        """

        for index, genotype in enumerate(keyword.genotype_keys):
            for _ in range(nums[index]):
                unique_id = self.new_unique_id()
                new       = larva.Larva.setup(unique_id,
                                              keyword.init,
                                              self,
                                              genotype)
                new.activate()

    def populate_pupae(self, nums: hint.init_pop) -> None:
        """
        Create the initial pupae

        Args:
            nums: (num_homo_r, num_hetero, num_homo_s)

        Effects:
            adds pupae of the different amounts to the simulation
        """

        for index, genotype in enumerate(keyword.genotype_keys):
            for _ in range(nums[index]):
                unique_id = self.new_unique_id()
                new       = pupa.Pupa.setup(unique_id,
                                            keyword.init,
                                            self,
                                            genotype)
                new.activate()

    def populate_adults(self, nums: hint.init_pop) -> None:
        """
        Create the initial adults

        Args:
            nums: (num_homo_r, num_hetero, num_homo_s)

        Effects:
            adds adults of the different amounts to the simulation
        """

        for index, genotype in enumerate(keyword.genotype_keys):
            for _ in range(nums[index]):
                unique_id = self.new_unique_id()
                new       = adult.Adult.setup(unique_id,
                                              keyword.init,
                                              self,
                                              genotype)
                new.activate()

    def populate_pregnant(self, nums: hint.init_pop) -> None:
        """
        Create the initial pregnant adults

        Args:
            nums: (num_homo_r, num_hetero, num_homo_s)

        Effects:
            adds pregnant of the different amounts to the simulation
        """

        for index, genotype in enumerate(keyword.genotype_keys):
            for _ in range(nums[index]):
                if genotype == keyword.hetero:
                    parents = [keyword.homo_r, keyword.homo_s]
                else:
                    parents = [genotype, genotype]
                rnd.shuffle(parents)

                unique_id = self.new_unique_id()
                new       = adult.Adult.setup(unique_id,
                                              keyword.init,
                                              self,
                                              parents[0],
                                              parents[1])
                new.activate()

    def populate(self, nums: hint.init_pops) -> None:
        """
        Create the initial populations

        Args:
            nums: (egg_masses, larvae, pupae, adults, pregnant)

        Effects:
            adds the initial population to simulation
        """

        self.populate_egg_masses(nums[0])
        self.populate_larvae(    nums[1])
        self.populate_pupae(     nums[2])
        self.populate_adults(    nums[3])
        self.populate_pregnant(  nums[4])

    def step(self) -> None:
        """
        Advance the simulation forward one step

        Effect:
            advance simulation forward by 1
        """

        self.count_step()

        self.schedule.   perform(    self.space, self.agents)
        self.immigration.immigration(self)
        self.emigration. emigration( self.agents)
        self.agents.     record()
        self.database.   save(self)

    def save(self, filename: str) -> None:
        """
        Pickle the simulation to a file for reuse

        Args:
            filename: name of pickle file

        Effects:
            write entire simulation to a file
        """

        with open(filename, 'wb') as sim_dump:
            pk.dump(self, sim_dump, protocol=pk.HIGHEST_PROTOCOL)
