import dataclasses as dclass

import source.hint    as hint
import source.keyword as keyword

import source.agents.pupa as pupa


@dclass.dataclass
class Larva(object):
    """
    Class to handle larva development behavior

    Variables:
        development: mathematical function for if larva develops

    Methods:
        develop: run the behavior

    Constructors:
        setup: setup class
    """

    development: hint.development_larva = None

    behavior: str = keyword.development_larva

    @property
    def _use_development(self) -> bool:
        """Determine if we use the development model"""

        return self.development is not None

    def _develop(self, larva: hint.larva) -> bool:
        """
        Determine if the larva develops

        Args:
            larva: the larva in question

        Returns:
            if the larva develops or not
        """

        if self._use_development:
            return self.development(larva.mass, larva.age, larva.genotype)
        else:
            return False

    @staticmethod
    def _make_pupa(larva: hint.larva) -> None:
        """
        Create a pupa version of this larva

        Args:
            larva: the larva in question

        Returns:
            a created pupa
        """

        new = pupa.Pupa.advance(larva)
        new.activate()

    def develop(self, larva: hint.larva) -> None:
        """
        Run development on the larva

        Args:
            larva: the larva in question

        Effects:
            if larva develops, replace it with a pupa
            else do nothing
        """

        if self._develop(larva):
            larva.deactivate()
            self._make_pupa(larva)

    @classmethod
    def setup(cls, **kwargs) -> 'Larva':
        """
        Setup the class

        Args:
            **kwargs: simulation input models

        Returns:
            setup class
        """

        if keyword.larva_development in kwargs:
            return cls(kwargs[keyword.larva_development])
        else:
            return cls()
