import dataclasses  as dclass
import numpy.random as rnd

import source.hint    as hint
import source.keyword as keyword


@dclass.dataclass
class Mate(object):
    """
    Class to handle adult mating:

    Variables:
        mating: mathematical function for the encounter of mates
        radius: mathematical function for the radius mates can be found

    Methods:
        mate: run the behavior

    Constructors:
        setup: setup class
    """

    mating: hint.mating      = None
    radius: hint.mate_radius = None

    behavior: str = keyword.mate

    @property
    def _use_mating(self) -> bool:
        """Determine if we can use mating"""

        return self.mating is not None

    @property
    def _use_radius(self) -> bool:
        """Determine if we can use radius"""

        return self.radius is not None

    @staticmethod
    def _mate_with(adult: hint.adult,
                   mate:  hint.adult) -> None:
        """
        Mate with the mate

        Args:
            adult: the adult in question
            mate: the target mate

        Effects:
            mate with the target
        """

        adult.set_mate(mate)
        mate.set_mate(adult)

    def _bounds(self, adult: hint.adult) -> dict:
        """
        Get the bounds on the radius for finding encounters

        Args:
            adult: the adult in question

        Returns:
            dict:
                {upper: radius
                 lower: 0}
        """

        if self._use_radius:
            radius = self.radius(adult.mass, adult.genotype)
        else:
            radius = 0

        return {keyword.upper: radius,
                keyword.lower: 0}

    def _mates(self, adult: hint.adult) -> hint.mates:
        """
        Get a list of mates for cannibalism

        Args:
            adult: the adult in question

        Returns:
            list of mates
        """

        return adult.mates(**self._bounds(adult))

    def _encounter(self, adult: hint.adult,
                         mates: hint.mates) -> bool:
        """
        Determine if this adult mates

        Args:
            adult: the adult in question
            mates: the list of possible mates

        Returns:
            if this adult mates
        """

        return self.mating(len(mates), adult.mass, adult.genotype)

    def _perform(self, adult: hint.adult) -> None:
        """
        Run a mating ritual

        Args:
            adult: the adult in question

        Effects:
            Perform a mating ritual
        """

        mates = self._mates(adult)

        if self._encounter(adult, mates):
            mate = rnd.choice(mates)
            self._mate_with(adult, mate)

    def mate(self, adult: hint.adult) -> None:
        """
        Performs a mating system ritual

        Args:
            adult: the adult in question

        Effects:
            Performs mating
        """

        if self._use_mating:
            self._perform(adult)

    @classmethod
    def setup(cls, **kwargs) -> 'Mate':
        """
        Setup the class

        Args:
            **kwargs: simulation input models

        Returns:
            setup class
        """

        if keyword.mating in kwargs:
            mating = kwargs[keyword.mating]
        else:
            mating = None

        if keyword.mate_radius in kwargs:
            radius = kwargs[keyword.mate_radius]
        else:
            radius = None

        return cls(mating, radius)
