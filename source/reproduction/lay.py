import dataclasses as dclass

import source.hint    as hint
import source.keyword as keyword

import source.agents.egg_mass as agent_egg_mass


@dclass.dataclass
class Lay(object):
    """
    Class to handle egg laying behavior:

    Variables:
        trials:    the number of times ot attempt to lay
        fecundity: mathematical function for number of egg_masses to lay
        density:   mathematical function for the density of agents in local
                                                                        area

    Methods:
        reset: reset the number of egg_masses to lay
        lay:   run the behavior

    Constructors:
        setup: setup class
    """

    trials:    int            = 0
    fecundity: hint.fecundity = None
    density:   hint.density   = None

    @property
    def _use_fecundity(self) -> bool:
        """Determine if we have a fecundity model"""

        return self.fecundity is not None

    @property
    def _use_density(self) -> bool:
        """Determine if we have a density model"""

        return self.density is not None

    def reset(self, adult: hint.adult) -> int:
        """
        Reset the number of egg_masses to lay

        Args:
            adult: the adult in question

        Effects:
            Sets number to number of egg masses
        """

        if self._use_fecundity:
            return self.fecundity(adult.mass, adult.age, adult.genotype)
        else:
            return 0


    def _check_density(self, adult:  hint.adult,
                             number: int) -> bool:
        """
        Check if density is low enough

        Args:
            adult:  the adult in question
            number: the local number of insects

        Returns:
            the result of the model test
        """

        if self._use_density:
            return self.density(number, adult.mass, adult.genotype)
        else:
            return True

    def _lay_egg_mass(self, adult:  hint.adult,
                            number: int) -> hint.egg_lay:
        """
        Try to lay an egg mass

        Args:
            adult:  the adult in question
            number: the local number of insects

        Returns:
            eggs to lay
        """

        if self._check_density(adult, number):
            adult.num_eggs -= 1
            return [agent_egg_mass.EggMass.birth(adult)], number + 1
        else:
            return [], number

    def _lay(self, adult: hint.adult) -> hint.egg_masses:
        """
        Run loop to create egg_masses

        Args:
            adult: the adult in question

        Returns:
            list of egg_masses
        """

        number = adult.population()

        egg_masses = []
        for _ in range(self.trials):
            if adult.num_eggs <= 0:
                break
            else:
                new, number = self._lay_egg_mass(adult, number)
                egg_masses.extend(new)

        return egg_masses

    def lay(self, adult: hint.adult) -> hint.egg_masses:
        """
        Run egg lay system

        Args:
            adult: the adult in question

        Returns:
            list of egg_masses
        """

        if adult.num_eggs > 0:
            return self._lay(adult)
        else:
            return []

    @classmethod
    def setup(cls, **kwargs) -> 'Lay':
        """
        Setup the class

        Args:
            **kwargs: simulation input models

        Returns:
            setup class
        """

        if keyword.trials in kwargs:
            trials = kwargs[keyword.trials]
        else:
            trials = 0

        if keyword.fecundity in kwargs:
            fecundity = kwargs[keyword.fecundity]
        else:
            fecundity = None

        if keyword.density in kwargs:
            density = kwargs[keyword.density]
        else:
            density = None

        return cls(trials, fecundity, density)
