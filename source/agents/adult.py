import dataclasses as dclass
import itertools   as i_tools

import source.hint    as hint
import source.keyword as keyword

import source.agents.insect as insect


@dclass.dataclass
class Adult(insect.Insect):
    """
    Class to contain a adult agent
        - inherits from base insect class

    Variables:
        female:   if female or not
        num_eggs: number of egg_masses that can still be laid
        survival: survival system
        movement: movement system
        lay:      egg_laying system
        mate:     adult mating system

    Methods:
        survive: have the adult survive
        move:    have the larva move
    """

    num_eggs: int
    mate:     hint.adult_mate
    survival: hint.adult_survival
    movement: hint.adult_movement
    lay:      hint.lay
    mating:   hint.mate

    def __post_init__(self):
        """Setup some helper systems"""

        super().__post_init__()

        self._id_count = i_tools.count()

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

    def move(self) -> hint.agent_list:
        """
        Run the move behavior

        Effects:
            run behavior to move

        Returns:
            empty list
        """

        self.movement.move(self)

        return []

    def new_unique_id(self) -> str:
        """
        Create a new unique_id

        Returns:
            a unique_id
        """

        return '{}_{}{}'.format(self.unique_id,
                                next(self._id_count),
                                keyword.egg_mass)

    def new_egg_location(self) -> hint.location:
        """
        Create a new location for egg_mass

        Returns:
            a location for an egg_mass
        """

        location = self.location

        for _ in range(keyword.egg_depth - keyword.adult_depth):
            location = self.simulation.space.extend_location(location)

        return location

    def population(self) -> int:
        """
        Get the population of the plant the adult is on

        Returns:
            number of egg_masses and number of larvae
        """

        location_key = self.location.location_key

        num_eggs   = len(self.simulation.agents[location_key][keyword.egg_mass])
        num_larvae = len(self.simulation.agents[location_key][keyword.larva])

        return num_eggs + num_larvae

    def set_mate(self, mate: hint.adult) -> None:
        """
        Set the mate for adult

        Args:
            mate: the mate for the adult

        Effects:
            set the mate of the adult
        """

        if self.agent_key == keyword.male:
            if self.simulation.models[keyword.lifetime_male]:
                self.deactivate()
            elif self.simulation.models[keyword.limited]:
                self.transition(keyword.mated)
        else:
            self.mate = mate.genotype


    def _location_keys(self, **kwargs) -> hint.location_keys:
        """
        Get the location_keys for vertices in range

        Args:
            **kwargs: bounds for the range

        Returns:
            list of location keys
        """

        vertices = self.vertices(**kwargs)

        location_keys = []
        for vertex in vertices:
            loc                      = self.location.copy()
            loc[keyword.adult_level] = vertex
            location_keys.append(loc.location_key)

        return location_keys

    def mates(self, **kwargs) -> hint.mates:
        """
        Get a list of egg_masses within the space bounds given

        Args:
            **kwargs: bounds for the range

        Returns:
            list of target larvae and eggs
        """

        location_keys = self._location_keys(**kwargs)

        mates = []
        for location_key in location_keys:
            agent_bin = self.simulation.agents[location_key]
            mates    += agent_bin[keyword.male]

        return mates

    def reproduce(self) -> hint.agent_list:
        """
        Runs reproduction system:

        Returns:
            list of egg_masses which have been laid
        """

        if self.mate is not None:
            return self.lay.lay(self)
        else:
            self.mating.mate(self)

            return []

    def reset(self) -> None:
        """
        Reset the agent

        Effects:
            reset the agent
        """

        if self.agent_key == keyword.female:
            self.num_eggs = self.lay.reset(self)

            if not self.simulation.models[keyword.lifetime_female]:
                self.mate = None

        elif self.agent_key == keyword.mated:
            self.transition(keyword.male)


    def _set_sex(self) -> None:
        """
        Get the agent_key for the adult:

        Returns:
            the proper agent key for the sex
        """

        if self.mate is None:
            if self.simulation.models[keyword.init_sex](self.genotype):
                self.agent_key = keyword.female
            else:
                self.agent_key = keyword.male
        else:
            self.agent_key = keyword.female
            self.num_eggs  = self.lay.reset(self)

    @classmethod
    def initialize(cls, unique_id:  str,
                        simulation: hint.simulation,
                        location:   hint.location,
                        mass:       float,
                        genotype:   str,
                        mate:       hint.adult_mate = None) -> 'Adult':
        """
        Initialize a new adult agent

        Args:
            unique_id:  the agent's unique_id
            simulation: the master simulation
            location:   the agent's location
            mass:       the agent's mass
            genotype:   the agent's genotype
            mate:       the agent's mate

        Returns:
            A fully initialized agent
        """

        alive    = True
        age      = 0
        death    = keyword.alive
        num_eggs = 0

        survival = simulation.behaviors.survive_adult
        movement = simulation.behaviors.move_adult
        lay      = simulation.behaviors.lay
        mating   = simulation.behaviors.mate

        new = cls('', unique_id, simulation, location,
                  alive, mass, genotype, age, death, num_eggs, mate,
                  survival, movement, lay, mating)
        new._set_sex()

        return new

    @classmethod
    def setup(cls, unique_id_num: int,
                   initial_key:   str,
                   simulation:    hint.simulation,
                   genotype:      str,
                   mate:          hint.adult_mate = None) -> 'Adult':
        """
        Setup an initial population adult

        Args:
            unique_id_num: unique_id number
            initial_key:   key for where agent was initialized
            simulation:    the master simulation
            genotype:      the agent's genotype
            mate:       the agent's mate

        Returns:
            a adult initialized by a population
        """

        unique_id = '{}{}{}'.format(initial_key,
                                    unique_id_num,
                                    keyword.adult)
        location  = simulation.space.new_location(keyword.adult_depth)
        mass      = simulation.models[keyword.init_mature](genotype)

        return cls.initialize(unique_id, simulation, location,
                              mass, genotype, mate)

    @classmethod
    def advance(cls, pupa: hint.pupa) -> 'Adult':
        """
        Create a adult agent for this pupa

        Args:
            pupa: the pupa in question

        Returns:
            A adult version of this pupa
        """

        return cls.initialize(pupa.unique_id,
                              pupa.simulation,
                              pupa.location,
                              pupa.mass,
                              pupa.genotype)
