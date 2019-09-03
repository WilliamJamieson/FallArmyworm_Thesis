import dataclasses as dclass

import source.hint    as hint
import source.keyword as keyword

import source.agents.insect as insect


@dclass.dataclass
class Larva(insect.Insect):
    """
    Class to contain a larva agent
        - inherits from base insect class

    Variables:
        plant_gut:    amount of plant that the larva has eaten
        egg_gut:      amount of egg   that the larva has eaten
        larva_gut:    amount of larva that the larva has eaten
        full:         boolean if larva is full
        gut:          gut system
        biomass:      biomass system
        survival:     survival system
        development:  development system
        movement:     movement system
        forage_plant: forage a plant system
        forage_egg:   forage an egg  system
        forage_larva: forage a larva system
        loss:         target loss/consume system
        cannibalism:  perform cannibalism system

    Methods:
        add_plant:     add plant to the gut storage
        add_egg:       add egg   to the gut storage
        add_larva:     add larva to the gut storage
        grow:          have larva grow in mass
        survive:       have the larva survive
        develop:       have the larva develop
        move:          have the larva move
        consume_egg:   consume egg material
        consume_larva: consume larva material
        targets:       get cannibalism targets
        consume:       have larva consume mass
    """

    plant_gut:    float
    egg_gut:      float
    larva_gut:    float
    full:         bool
    starve:       bool
    gut:          hint.gut
    biomass:      hint.mass
    survival:     hint.larva_survival
    development:  hint.larva_development
    movement:     hint.larva_movement
    forage_plant: hint.plant_forage
    forage_egg:   hint.egg_forage
    forage_larva: hint.larva_forage
    loss:         hint.target_loss
    cannibalism:  hint.cannibalism

    target: hint.target = None

    @property
    def active(self) -> bool:
        """Determine if this larva is still active"""

        return self.mass > 0

    @property
    def _can_consume(self) -> bool:
        """Determine if this larva can consume"""

        return self.alive and (not self.full)

    @property
    def _has_target(self) -> bool:
        """Determine if this larva has a valid target"""

        return (self.target is not None) and self.target.active

    def add_plant(self, available: float) -> float:
        """
        Consume plant from the available amount

        Args:
            available: the amount available

        Effects:
            adds amount consumed to plant_gut
            checks if agent is full

        Returns:
            the amount consumed
        """

        amount, full    = self.gut.amount(self, available)
        self.plant_gut += amount

        if full:
            self.full = True

        return amount

    def add_egg(self, available: float) -> float:
        """
        Consume egg from the available amount

        Args:
            available: the amount available

        Effects:
            adds amount consumed to egg_gut
            checks if agent is full

        Returns:
            the amount consumed
        """

        amount, full    = self.gut.amount(self, available)
        self.egg_gut += amount

        if full:
            self.full = True

        return amount

    def add_larva(self, available: float) -> float:
        """
        Consume larva from the available amount

        Args:
            available: the amount available

        Effects:
            adds amount consumed to larva_gut
            checks if agent is full

        Returns:
            the amount consumed
        """

        amount, full    = self.gut.amount(self, available)
        self.larva_gut += amount

        if full:
            self.full = True

        return amount

    def grow(self) -> hint.agent_list:
        """
        Grow the larva as behavior

        Effects:
            increase the mass of the larva

        Returns:
            empty list
        """

        if self.alive:
            growth = self.biomass.grow(self)
            if growth < 0:
                self.starve = True
            else:
                self.mass += growth

        return []

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

    def move(self) -> hint.agent_list:
        """
        Run the move behavior

        Effects:
            run behavior to move

        Returns:
            empty list
        """

        if self._can_consume and (not self._has_target):
            self.movement.move(self)

        return []

    def _consume_plant(self) -> None:
        """
        Run consume plant behavior

        Effects:
            consume the plant
        """

        if self._can_consume:
            self.forage_plant.consume(self)

    def consume_egg(self, egg_mass: hint.egg_mass) -> None:
        """
        Run consume egg behavior

        Args:
            egg_mass: the egg_mass to consume

        Effects:
            consume the egg_mass
        """

        self.target = egg_mass
        self.forage_egg.consume(self, egg_mass)

    def consume_larva(self, target: hint.larva) -> None:
        """
        Run consume larva behavior

        Args:
            target: the target to consume

        Effects:
            consume the target
        """

        self.target = target
        self.forage_larva.consume(self, target)

    def _consume_target(self) -> None:
        """
        Run consume behavior on the target

        Effects:
            consumes the target
        """

        if self._has_target and self.alive:
            self.loss.consume(self)

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
            loc[keyword.larva_level] = vertex
            location_keys.append(loc.location_key)

        return location_keys

    def targets(self, **kwargs) -> hint.targets:
        """
        Get a list of egg_masses within the space bounds given

        Args:
            **kwargs: bounds for the range

        Returns:
            list of target larvae and eggs
        """

        location_keys = self._location_keys(**kwargs)

        targets = []
        for location_key in location_keys:
            agent_bin = self.simulation.agents[location_key]
            targets  += agent_bin[keyword.egg_mass].agents
            targets  += agent_bin[keyword.larva].agents

        targets.remove(self)

        return targets

    def consume(self) -> hint.agent_list:
        """
        Run the full consume behavior

        Effects:
            consumes other agents and mass

        Returns:
            empty list
        """

        if not self.full:
            self._consume_target()
            self.cannibalism.cannibalism(self)
            self._consume_plant()

        return []

    def reset(self) -> hint.agent_list:
        """
        Reset the agent

        Effects:
            sets gut volumes to zero
            sets full to false
        """

        self.plant_gut = 0
        self.egg_gut   = 0
        self.larva_gut = 0

        self.full = False

        return []

    @classmethod
    def initialize(cls, unique_id:  str,
                        simulation: hint.simulation,
                        location:   hint.location,
                        mass:       float,
                        genotype:   str) -> 'Larva':
        """
        Initialize a new larva agent

        Args:
            unique_id:  the agent's unique_id
            simulation: the master simulation
            location:   the agent's location
            mass:       the agent's mass
            genotype:   the agent's genotype

        Returns:
            A fully initialized agent
        """

        agent_key = keyword.larva
        alive    = True
        age      = 0
        death    = keyword.alive

        plant_gut = 0
        egg_gut   = 0
        larva_gut = 0
        full      = False
        starve    = False

        gut          = simulation.behaviors.gut
        biomass      = simulation.behaviors.mass
        survival     = simulation.behaviors.survive_larva
        development  = simulation.behaviors.develop_larva
        movement     = simulation.behaviors.move_larva
        cannibalism  = simulation.behaviors.cannibalism
        forage_plant = simulation.behaviors.forage_plant
        forage_egg   = simulation.behaviors.forage_egg
        forage_larva = simulation.behaviors.forage_larva
        loss         = simulation.behaviors.target

        return cls(agent_key, unique_id, simulation, location, alive,
                   mass, genotype, age, death,
                   plant_gut, egg_gut, larva_gut, full, starve,
                   gut, biomass, survival, development, movement,
                   forage_plant, forage_egg, forage_larva, loss, cannibalism)

    @classmethod
    def setup(cls, unique_id_num: int,
                   initial_key:   str,
                   simulation:    hint.simulation,
                   genotype:      str) -> 'Larva':
        """
        Setup an initial population larva

        Args:
            unique_id_num: unique_id number
            initial_key:   key for where agent was initialized
            simulation:    the master simulation
            genotype:      the agent's genotype

        Returns:
            a larva initialized by a population
        """

        unique_id = '{}{}{}'.format(initial_key,
                                    unique_id_num,
                                    keyword.larva)
        location  = simulation.space.new_location(keyword.larva_depth)
        mass      = simulation.models[keyword.init_juvenile](genotype)

        return cls.initialize(unique_id, simulation, location, mass, genotype)

    @classmethod
    def advance(cls, egg: hint.egg) -> 'Larva':
        """
        Create a larva agent for this egg

        Args:
            egg: the egg in question

        Returns:
            A larva version of this egg
        """

        return cls.initialize(egg.unique_id,
                              egg.simulation,
                              egg.location,
                              egg.mass,
                              egg.genotype)
