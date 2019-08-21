import dataclasses as dclass

import source.hint    as hint
import source.keyword as keyword

import source.agents.adult as adult


@dclass.dataclass
class Pupa(object):
    """
    Class to handle pupa development behavior

    Variables:
        development: mathematical function for if pupa develops

    Methods:
        develop: run the behavior

    Constructors:
        setup: setup class
    """

    development: hint.development_pupa = None

    @property
    def _use_development(self) -> bool:
        """Determine if we use the development model"""

        return self.development is not None

    def _develop(self, pupa: hint.pupa) -> bool:
        """
        Determine if the pupa develops

        Args:
            pupa: the pupa in question

        Returns:
            if the pupa develops or not
        """

        if self._use_development:
            return self.development(pupa.mass, pupa.age, pupa.genotype)
        else:
            return False

    @staticmethod
    def _make_adult(pupa: hint.pupa) -> None:
        """
        Create a adult from the pupa

        Args:
            pupa: the pupa in question

        Returns:
            the adult for pupa to develop into
        """

        new = adult.Adult.advance(pupa)
        new.activate()

    def develop(self, pupa: hint.pupa) -> None:
        """
        Run development on the pupa

        Args:
            pupa: the pupa in question

        Effects:
            if pupa develops, replace it with a adult
            else do nothing
        """

        if self._develop(pupa):
            pupa.deactivate()
            self._make_adult(pupa)

    @classmethod
    def setup(cls, **kwargs) -> 'Pupa':
        """
        Setup the class

        Args:
            **kwargs: simulation input models

        Returns:
            setup class
        """

        if keyword.pupa_development in kwargs:
            return cls(kwargs[keyword.pupa_development])
        else:
            return cls()
