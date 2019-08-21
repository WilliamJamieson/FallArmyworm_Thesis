import dataclasses as dclass

import source.hint    as hint
import source.keyword as keyword


@dclass.dataclass
class Larva(object):
    """
    Class to handle larva survival behavior

    Variables:
        survival: mathematical function for if egg dies of survival

    Methods:
        survive: run the behavior

    Constructors:
        setup: setup class
    """

    survival: hint.survival_larva = None

    @property
    def _use_survival(self) -> bool:
        """Determine if we use the survive model"""

        return self.survival is not None

    @staticmethod
    def _starve(larva: hint.larva) -> None:
        """
        Check if larva starves

        Args:
            larva: the larva in question

        Effects:
            if starves then death by starvation
        """

        if larva.starve:
            larva.die(keyword.starve)

    def _survive(self, larva: hint.larva) -> bool:
        """
        Determine if the larva survives

        Args:
            larva: the larva in question

        Returns:
            boolean indicating survival
        """

        if self._use_survival and larva.alive:
            return self.survival(larva.mass, larva.genotype, larva.bt)
        else:
            return True

    def survive(self, larva: hint.larva) -> None:
        """
        Run survival model

        Args:
            larva: the larva in question

        Effects:
            Run one complete survival step
        """

        self._starve(larva)
        if not self._survive(larva):
            larva.die(keyword.survival)

    @classmethod
    def setup(cls, **kwargs) -> 'Larva':
        """
        Setup the class

        Args:
            **kwargs: simulation input models

        Returns:
            setup class
        """

        if keyword.larva_survival in kwargs:
            return cls(kwargs[keyword.larva_survival])
        else:
            return cls()
