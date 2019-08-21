import dataclasses as dclass

import source.hint    as hint
import source.keyword as keyword


@dclass.dataclass
class Egg(object):
    """
    Class to handle egg foraging (eating) behavior

    Variables:
        forage: mathematical function for how much can be eaten

    Methods:
        consume: run the behavior

    Constructors:
        setup: setup class
    """

    forage: hint.forage_egg = None

    behavior: str = keyword.forage_egg

    @property
    def _use_forage(self) -> bool:
        """Determine if we use the forage model"""

        return self.forage is not None

    def _available(self, larva:    hint.larva,
                         egg_mass: hint.egg_mass) -> float:
        """
        Get the amount of mass which can be foraged from a target egg_mass

        Args:
            larva:    the larva foraging
            egg_mass: the egg_mass being eaten

        Returns:
            amount of food which can be eaten
        """

        return self.forage(egg_mass.mass, larva.mass, larva.genotype)

    def _consume(self, larva:    hint.larva,
                       egg_mass: hint.egg_mass) -> None:
        """
        Consume available food

        Args:
            larva:    the larva foraging
            egg_mass: the egg_mass being eaten

        Effects:
            eats the available amount of food as larva
        """

        available = self._available(larva, egg_mass)
        amount    = larva.add_egg(available)
        egg_mass.feed(amount)

    def consume(self, larva:    hint.larva,
                      egg_mass: hint.egg_mass) -> None:
        """
        Run forage/consume when possible on target egg_mass

        Args:
            larva:    the larva foraging
            egg_mass: the egg_mass being eaten

        Effects:
            consumes part of the egg_mass
        """

        if self._use_forage:
            self._consume(larva, egg_mass)

    @classmethod
    def setup(cls, **kwargs) -> 'Egg':
        """
        Setup the class

        Args:
            **kwargs: simulation input models

        Returns:
            setup class
        """

        if keyword.egg_forage in kwargs:
            return cls(kwargs[keyword.egg_forage])
        else:
            return cls()
