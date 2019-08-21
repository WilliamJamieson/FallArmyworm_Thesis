import dataclasses as dclass

import source.hint    as hint
import source.keyword as keyword


@dclass.dataclass
class Adult(object):
    """
    Class to handle adult survival behavior

    Variables:
        survival: mathematical function for if adult dies of survival

    Methods:
        survive: run the behavior

    Constructors:
        setup: setup class
    """

    survival: hint.survival_adult = None

    @property
    def _use_survival(self) -> bool:
        """Determine if we use the survival model"""

        return self.survival is not None

    def _survive(self, adult: hint.adult) -> bool:
        """
        Determine if the adult survives

        Args:
            adult: the adult in question

        Returns:
            if the adult survives or not
        """

        if self._use_survival:
            return self.survival(adult.mass, adult.genotype)
        else:
            return True

    def survive(self, adult: hint.adult) -> None:
        """
        Run the survival model

        Args:
            adult: the adult in question

        Effects:
            kills adult if it fails to survive
        """

        if not self._survive(adult):
            adult.die(keyword.survival)

    @classmethod
    def setup(cls, **kwargs) -> 'Adult':
        """
        Setup the class

        Args:
            **kwargs: simulation input models

        Returns:
            setup class
        """

        if keyword.adult_survival in kwargs:
            return cls(kwargs[keyword.adult_survival])
        else:
            return cls()
