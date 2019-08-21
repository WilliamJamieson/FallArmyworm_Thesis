import dataclasses as dclass

import source.hint as hint

import source.biomass.gut  as agent_gut
import source.biomass.mass as agent_mass

import source.development.egg   as agent_develop_egg
import source.development.larva as agent_develop_larva
import source.development.pupa  as agent_develop_pupa

import source.forage.cannibalism as agent_cannibalism
import source.forage.egg         as agent_forage_egg
import source.forage.larva       as agent_forage_larva
import source.forage.plant       as agent_forage_plant

import source.movement.adult as agent_move_adult
import source.movement.larva as agent_move_larva

import source.reproduction.lay  as agent_lay
import source.reproduction.mate as agent_mate

import source.survival.adult as agent_survive_adult
import source.survival.egg   as agent_survive_egg
import source.survival.larva as agent_survive_larva
import source.survival.pupa  as agent_survive_pupa


@dclass.dataclass
class Behaviors(object):
    """
    Class to handle all of the behavior actions:

    Variables:
        gut:  gut  behavior
        mass: mass behavior

        develop_egg:   egg   development behavior
        develop_larva: larva development behavior
        develop_pupa:   pupa development behavior

        cannibalism:  cannibalism     behavior
        forage_egg:   egg   consuming behavior
        forage_larva: larva consuming behavior
        forage_plant: plant consuming behavior

        move_adult: adult movement behavior
        move_larva: larva movement behavior

        lay:  egg   laying behavior
        mate: adult mating behavior

        survive_adult: adult survival behavior
        survive_egg:   egg   survival behavior
        survive_larva: larva survival behavior
        survive_pupa:  pupa  survival behavior
    """

    gut:  hint.gut  = None
    mass: hint.mass = None

    develop_egg:   hint.egg_development   = None
    develop_larva: hint.larva_development = None
    develop_pupa:  hint.pupa_development  = None

    cannibalism:  hint.cannibalism  = None
    forage_egg:   hint.egg_forage   = None
    forage_larva: hint.larva_forage = None
    forage_plant: hint.plant_forage = None

    move_adult: hint.adult_movement = None
    move_larva: hint.larva_movement = None

    lay:  hint.lay  = None
    mate: hint.mate = None

    survive_adult: hint.adult_survival = None
    survive_egg:   hint.egg_survival   = None
    survive_larva: hint.larva_survival = None
    survive_pupa:  hint.pupa_survival  = None

    def make_biomass(self, **kwargs) -> None:
        """
        Create the biomass behaviors

        Args:
            **kwargs: input mathematical models

        Effects:
            create the biomass behaviors if needed
        """

        if self.gut is None:
            self.gut = agent_gut.Gut.setup(**kwargs)

        if self.mass is None:
            self.mass = agent_mass.Mass.setup(**kwargs)

    def make_development(self, **kwargs) -> None:
        """
        Create the development behaviors

        Args:
            **kwargs: input mathematical models

        Effects:
            create the development behaviors if needed
        """

        if self.develop_egg is None:
            self.develop_egg = agent_develop_egg.Egg.setup(**kwargs)

        if self.develop_larva is None:
            self.develop_larva = agent_develop_larva.Larva.setup(**kwargs)

        if self.develop_pupa is None:
            self.develop_pupa = agent_develop_pupa.Pupa.setup(**kwargs)

    def make_forage(self, **kwargs) -> None:
        """
        Create the forage behaviors

        Args:
            **kwargs: input mathematical models

        Effects:
            create the forage behaviors if needed
        """

        if self.cannibalism is None:
            self.cannibalism = agent_cannibalism.Cannibalism.setup(**kwargs)

        if self.forage_egg is None:
            self.forage_egg = agent_forage_egg.Egg.setup(**kwargs)

        if self.forage_larva is None:
            self.forage_larva = agent_forage_larva.Larva.setup(**kwargs)

        if self.forage_plant is None:
            self.forage_plant = agent_forage_plant.Plant.setup(**kwargs)

    def make_movement(self, **kwargs) -> None:
        """
        Create the movement behaviors

        Args:
            **kwargs: input mathematical models

        Effects:
            create the movement behaviors if needed
        """

        if self.move_adult is None:
            self.move_adult = agent_move_adult.Adult.setup(**kwargs)

        if self.move_larva is None:
            self.move_larva = agent_move_larva.Larva.setup(**kwargs)

    def make_reproduction(self, **kwargs) -> None:
        """
        Create the reproduction behaviors

        Args:
            **kwargs: input mathematical models

        Effects:
            create the reproduction behaviors if needed
        """

        if self.lay is None:
            self.lay = agent_lay.Lay.setup(**kwargs)

        if self.mate is None:
            self.mate = agent_mate.Mate.setup(**kwargs)

    def make_survival(self, **kwargs) -> None:
        """
        Create the survival behaviors

        Args:
            **kwargs: input mathematical models

        Effects:
            create the survival behaviors if needed
        """

        if self.survive_adult is None:
            self.survive_adult = agent_survive_adult.Adult.setup(**kwargs)

        if self.survive_egg is None:
            self.survive_egg = agent_survive_egg.Egg.setup(**kwargs)

        if self.survive_larva is None:
            self.survive_larva = agent_survive_larva.Larva.setup(**kwargs)

        if self.survive_pupa is None:
            self.survive_pupa = agent_survive_pupa.Pupa.setup(**kwargs)

    @classmethod
    def setup(cls, **kwargs) -> 'Behaviors':
        """
        Setup all of the behaviors

        Args:
            **kwargs: input mathematical models

        Returns:
            setup class with all behaviors
        """

        new = cls()

        new.make_biomass(     **kwargs)
        new.make_development( **kwargs)
        new.make_forage(      **kwargs)
        new.make_movement(    **kwargs)
        new.make_reproduction(**kwargs)
        new.make_survival(    **kwargs)

        return new
