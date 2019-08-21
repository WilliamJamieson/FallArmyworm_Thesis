import dataclasses  as dclass
import numpy.random as rnd
import scipy.stats  as stats

import source.hint    as hint
import source.keyword as keyword

import source.simulation.models as models


@dclass.dataclass
class BaseTime(models.Model):
    """
    Class to contain development model based on time
        USES CDF for Normal Distribution for probability
        Checks if minimum time has been achieved

    Variables:
        mu:      mean time for development
        sigma:   standard deviation in mean time
        minimum: minimum time to wait
    """

    mu:      float
    sigma:   float
    minimum: float

    def _prob(self, age: int) -> float:
        """
        Get a probability to test against

        Args:
            age: time agent has existed

        Returns:
            a probability of development
        """

        if self.minimum <= age:
            return stats.norm.cdf(age, loc=self.mu, scale=self.sigma)
        else:
            return 0

    def __call__(self, mass:     float,
                 age:      int,
                 genotype: str) -> bool:
        """
        Determine if an agent develops

        Args:
            mass:     mass of agent
            age:      time agent has existed
            genotype: genotype of the agent

        Returns:
            if egg develops or not
        """

        return rnd.random() <= self._prob(age)


@dclass.dataclass
class Egg(BaseTime):
    """
    Class to contain development model for egg
        USES CDF for Normal Distribution for probability
        Checks if minimum time has been achieved

    Variables:
        mu:      mean time for development
        sigma:   standard deviation in mean time
        minimum: minimum time to wait
    """

    model_key = keyword.egg_development


@dclass.dataclass
class Pupa(BaseTime):
    """
    Class to contain development model for pupa
        USES CDF for Normal Distribution for probability
        Checks if minimum time has been achieved

    Variables:
        mu:      mean time for development
        sigma:   standard deviation in mean time
        minimum: minimum time to wait
    """

    model_key = keyword.pupa_development


@dclass.dataclass
class Larva(models.Model):
    """
    Class to contain development model for larva
        USES CDF for Normal Distribution for probability
        Checks if minimum time has been achieved

    Variables:
        mu:      mean mass for development
        sigma:   standard deviation in mean mass
        minimum: minimum time to wait
    """

    model_key = keyword.larva_development

    mu:      hint.variable
    sigma:   hint.variable
    minimum: hint.variable

    def _prob(self, mass:     float,
                    age:      int,
                    genotype: str) -> float:
        """
        Get a probability to test against

        Args:
            mass:     mass of larva
            age:      time larva has existed
            genotype: genotype of larva

        Returns:
            a probability of development
        """

        minimum = self.minimum[genotype]

        if minimum <= age:
            mu    = self.mu[genotype]
            sigma = self.sigma[genotype]

            return stats.norm.cdf(mass, loc=mu, scale=sigma)
        else:
            return 0

    def __call__(self, mass:     float,
                       age:      int,
                       genotype: str) -> bool:
        """
        Determine if a larva develops

        Args:
            mass:     mass of larva
            age:      time larva has existed
            genotype: genotype of the larva

        Returns:
            if egg develops or not
        """

        return rnd.random() <= self._prob(mass, age, genotype)
