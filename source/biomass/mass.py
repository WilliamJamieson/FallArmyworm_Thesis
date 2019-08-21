import dataclasses as dclass

import source.hint    as hint
import source.keyword as keyword


@dclass.dataclass
class Mass(object):
    """
    Class to handle the mass increase behavior for larvae:

    Variables:
        max_gut: mathematical function for maximum gut volume
        growth:  mathematical function for growth  of  mass

    Methods:
        grow: get the amount to grow

    Constructors:
        setup: setup the system from input arguments
    """

    max_gut: hint.max_gut
    growth:  hint.growth

    behavior: str = keyword.mass

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

    def _ratio(self, larva: hint.larva) -> float:
        """
        Get the ratio of gut volume to max_gut

        Args:
            larva: the larva in question

        Returns:
            volume/max_gut
        """

        return self._volume(larva) / self.max_gut(larva.mass)

    def _energy(self, mass:  float,
                      ratio: float) -> float:
        """
        Get the energy adjusted for RK4 shift

        Args:
            mass:  mass for the energy
            ratio: gut/max_gut ratio

        Returns:
            ratio*max_gut(shift mass)
        """

        return ratio*self.max_gut(mass)

    def _rhs(self, larva: hint.larva,
                   ratio: float,
                   shift: float) -> float:
        """
        The right hand side for an RK4 approx of the growth equation

        Args:
            larva: the larva in question
            ratio: gut/max_gut ratio
            shift: amount to shift

        Returns:
            rhs for RK4
        """

        mass   = larva.mass + shift
        energy = self._energy(mass, ratio)

        return self.growth(mass, energy, larva.genotype)

    def grow(self, larva: hint.larva) -> float:
        """
        Get the amount the larva grows

        Args:
            larva: the larva in question

        Returns:
            the amount the larva grows this step
        """

        ratio = self._ratio(larva)

        k1 = self._rhs(larva, ratio, 0)
        k2 = self._rhs(larva, ratio, k1/2)
        k3 = self._rhs(larva, ratio, k2/2)
        k4 = self._rhs(larva, ratio, k3)

        return (k1 + k2*2 + k3*2 + k4)/6

    @classmethod
    def setup(cls, **kwargs) -> 'Mass':
        """
        Setup the class

        Args:
            **kwargs: simulation input models

        Returns:
            setup class
        """

        return cls(kwargs[keyword.max_gut],
                   kwargs[keyword.growth])
