import dataclasses as dclass

import source.hint    as hint
import source.keyword as keyword


@dclass.dataclass
class Larva(object):
    """
    Class to handle larva foraging (eating) behavior

    Variables:
        forage: mathematical function for how much can be eaten

    Methods:
        consume: run the behavior

    Constructors:
        setup: setup class
    """

    forage: hint.forage_larva = None

    @property
    def _use_forage(self) -> bool:
        """Determine if we use the forage model"""

        return self.forage is not None

    def _available(self, larva:  hint.larva,
                         target: hint.larva) -> float:
        """
        Get the amount of mass which can be foraged from a target larva

        Args:
            larva:  the larva foraging
            target: the larva being eaten

        Returns:
            amount of food which can be eaten
        """

        return self.forage(target.mass, larva.mass, larva.genotype)

    def _consume(self, larva:  hint.larva,
                       target: hint.larva) -> None:
        """
        Consume available food

        Args:
            larva:  the larva foraging
            target: the larva being eaten

        Effects:
            eats the available amount of food as larva
        """

        available    = self._available(larva, target)
        amount       = larva.add_larva(available)
        target.mass -= amount

        if target.alive:
            target.die(keyword.cannibalism)

    def consume(self, larva:  hint.larva,
                      target: hint.larva) -> None:
        """
        Run forage/consume when possible on target larva

        Args:
            larva:  the larva foraging
            target: the larva being eaten

        Effects:
            eats the target larva if foraging
        """

        if self._use_forage:
            self._consume(larva, target)

    @classmethod
    def setup(cls, **kwargs) -> 'Larva':
        """
        Setup the class

        Args:
            **kwargs: simulation input models

        Returns:
            setup class
        """

        if keyword.larva_forage in kwargs:
            return cls(kwargs[keyword.larva_forage])
        else:
            return cls()
