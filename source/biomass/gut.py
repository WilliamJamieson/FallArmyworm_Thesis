import dataclasses as dclass

import source.hint    as hint
import source.keyword as keyword


@dclass.dataclass
class Gut(object):
    """
    Class handle the gut behavior for larvae:

    Variables:
        max_gut: mathematical function for maximum gut volume

    Methods:
        amount: get the amount of food to eat

    Constructors:
        setup: setup the system from input arguments
    """

    max_gut: hint.max_gut

    @staticmethod
    def _volume(larva: hint.larva) -> float:
        """
        Get the volume of food eaten by a larva

        Args:
            larva: the larva in question

        Returns:
            volume of food larva has eaten
        """

        return larva.plant_gut + larva.egg_gut + larva.larva_gut

    def _remaining(self, larva: hint.larva) -> float:
        """
        Get the remaining volume of gut for larva

        Args:
            larva: the larva in question

        Returns:
            volume of food larva can eat
        """

        return self.max_gut(larva.mass) - self._volume(larva)

    def amount(self, larva:     hint.larva,
                     available: float) -> hint.amount_tuple:
        """
        Get the amount of food that can be consumed from the available

        Args:
            larva:     the larva in question
            available: the available food

        Returns:
            the amount that can be consumed
        """

        remaining = self._remaining(larva)

        if available >= remaining:
            return remaining, True
        else:
            return available, False

    @classmethod
    def setup(cls, **kwargs) -> 'Gut':
        """
        Setup the class

        Args:
            **kwargs: simulation input models

        Returns:
            setup class
        """

        return cls(kwargs[keyword.max_gut])
