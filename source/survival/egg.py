import dataclasses as dclass

import source.hint    as hint
import source.keyword as keyword


@dclass.dataclass
class Egg(object):
    """
    Class to handle egg survival behavior

    Variables:
        survival: mathematical function for if egg dies of survival

    Methods:
        survive: run the behavior

    Constructors:
        setup: setup class
    """

    survival: hint.survival_egg = None

    behavior: str = keyword.survival_egg

    @property
    def _use_survival(self) -> bool:
        """Determine if we use the survival model"""

        return self.survival is not None

    def _survive(self, egg: hint.egg) -> bool:
        """
        Determine if the egg survives

        Args:
            egg: the egg in question

        Returns:
            if the egg survives or not
        """

        if self._use_survival:
            return self.survival(egg.mass, egg.genotype, egg.bt)
        else:
            return True

    def survive(self, egg: hint.egg) -> None:
        """
        Run the survival model

        Args:
            egg: the egg in question

        Effects:
            kills egg if it fails to survive
        """

        if not self._survive(egg):
            egg.die(keyword.survival)

    @classmethod
    def setup(cls, **kwargs) -> 'Egg':
        """
        Setup the class

        Args:
            **kwargs: simulation input models

        Returns:
            setup class
        """

        if keyword.egg_survival in kwargs:
            return cls(kwargs[keyword.egg_survival])
        else:
            return cls()
