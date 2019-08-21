import dataclasses as dclass

import source.hint    as hint
import source.keyword as keyword


@dclass.dataclass
class Plant(object):
    """
    Class to handle plant foraging (eating) behavior

    Variables:
        forage: mathematical function for how much can be eaten

    Methods:
        consume: run the behavior

    Constructors:
        setup: setup class
    """

    forage: hint.forage_plant = None

    @property
    def _use_forage(self) -> bool:
        """Determine if we use the forage model"""

        return self.forage is not None

    def _available(self, larva: hint.larva) -> float:
        """
        Get the amount of mass that can be foraged

        Args:
            larva: the larva foraging

        Returns:
            amount of food available
        """

        return self.forage(larva.mass, larva.plant, larva.genotype, larva.bt)

    def _consume(self, larva: hint.larva) -> None:
        """
        Consume available food

        Args:
            larva: the larva foraging

        Effects:
            eats the available amount of food as plant
        """

        available = self._available(larva)
        larva.add_plant(available)

    def consume(self, larva: hint.larva) -> None:
        """
        Run forage/consume when possible on plant

        Args:
            larva: the larva foraging

        Effects:
            consumes part of leaf
        """

        if self._use_forage:
            self._consume(larva)

    @classmethod
    def setup(cls, **kwargs) -> 'Plant':
        """
        Setup the class

        Args:
            **kwargs: simulation input models

        Returns:
            setup class
        """

        if keyword.plant_forage in kwargs:
            return cls(kwargs[keyword.plant_forage])
        else:
            return cls()
