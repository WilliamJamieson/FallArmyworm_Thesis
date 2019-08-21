import dataclasses as dclass

import source.hint    as hint
import source.keyword as keyword


@dclass.dataclass
class Pupa(object):
    """
    Class to handle pupa survival behavior

    Variables:
        survival: mathematical function for if pupa dies of survival

    Methods:
        survive: run the behavior

    Constructors:
        setup: setup class
    """

    survival: hint.survival_pupa = None

    behavior: str = keyword.survival_pupa

    @property
    def _use_survival(self) -> bool:
        """Determine if we use the survival model"""

        return self.survival is not None

    def _survive(self, pupa: hint.pupa) -> bool:
        """
        Determine if the pupa survives

        Args:
            pupa: the pupa in question

        Returns:
            if the pupa survives or not
        """

        if self._use_survival:
            return self.survival(pupa.mass, pupa.genotype)
        else:
            return True

    def survive(self, pupa: hint.pupa) -> None:
        """
        Run the survival model

        Args:
            pupa: the pupa in question

        Effects:
            kills pupa if it fails to survive
        """

        if not self._survive(pupa):
            pupa.die(keyword.survival)

    @classmethod
    def setup(cls, **kwargs) -> 'Pupa':
        """
        Setup the class

        Args:
            **kwargs: simulation input models

        Returns:
            setup class
        """

        if keyword.pupa_survival in kwargs:
            return cls(kwargs[keyword.pupa_survival])
        else:
            return cls()
