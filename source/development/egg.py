import dataclasses as dclass

import source.hint    as hint
import source.keyword as keyword

import source.agents.larva as larva


@dclass.dataclass
class Egg(object):
    """
    Class to handle egg development behavior

    Variables:
        development: mathematical function for if egg develops

    Methods:
        develop: run the behavior

    Constructors:
        setup: setup class
    """

    development: hint.development_egg = None

    @property
    def _use_development(self) -> bool:
        """Determine if we use the development model"""

        return self.development is not None

    def _develop(self, egg: hint.egg) -> bool:
        """
        Determine if the egg develops

        Args:
            egg: the egg in question

        Returns:
            if the egg develops or not
        """

        if self._use_development:
            return self.development(egg.mass, egg.age, egg.genotype)
        else:
            return False

    @staticmethod
    def _make_larva(egg: hint.egg) -> None:
        """
        Create a larva from the egg

        Args:
            egg: the egg in question

        Returns:
            the larva for egg to develop into
        """

        new = larva.Larva.advance(egg)
        new.activate()

    def develop(self, egg: hint.egg) -> None:
        """
        Run development on the egg

        Args:
            egg: the egg in question

        Effects:
            if egg develops, replace it with a larva
            else do nothing
        """

        if self._develop(egg):
            egg.deactivate()
            self._make_larva(egg)

    @classmethod
    def setup(cls, **kwargs) -> 'Egg':
        """
        Setup the class

        Args:
            **kwargs: simulation input models

        Returns:
            setup class
        """

        if keyword.egg_development in kwargs:
            return cls(kwargs[keyword.egg_development])
        else:
            return cls()
