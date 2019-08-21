import dataclasses  as dclass
import numpy        as np
import numpy.random as rnd
import scipy.stats  as stats

import source.keyword as keyword

import source.simulation.models as models


@dclass.dataclass
class InitSex(models.Model):
    """
    Class to contain a model for the adult sex:
        P is the probability of being female

    Variables:
        prob: the probability of being female

    Methods:
        __call__: call the model

    Constructors:
        setup: setup the mathematical model
    """

    model_key = keyword.init_sex

    prob: float

    def __call__(self, genotype: str) -> bool:
        """
        Call model to determine if female

        Args:
            genotype: the adult's genotype

        Returns:
            if this is female
        """

        return rnd.random() <= self.prob


@dclass.dataclass
class Mating(models.Model):
    """
    Class to contain encounter model for mating

        Probability for an encounter is given via:
            p(n) = 1 - exp(-k*n)
        where n is the number of other individuals and k is the scale factor

    Variables:
        factor: scale factor for encounters

    Methods:
        __call__: call the model
    """

    model_key = keyword.mating

    factor: float

    def _prob(self, number: int) -> float:
        """
        Get the probability for an encounter

        Args:
            number: number of other individuals

        Returns:
            probability of an encounter
        """

        exp = -self.factor*number

        return 1 - np.exp(exp)

    def __call__(self, number:   int,
                       mass:     float,
                       genotype: str) -> bool:
        """
        Make an encounter decision

        Args:
            number    number of other individuals
            mass:     mass of consumer
            genotype: genotype of consumer

        Returns:
            if an encounter occurs
        """

        return rnd.random() <= self._prob(number)


@dclass.dataclass
class Radius(models.Model):
    """
    Class to contain mate radius model

    Variables:
        radius: the radius for mates

    Methods:
        __call__: call the model
    """

    model_key = keyword.mate_radius

    radius: float

    def __call__(self, mass:     float,
                       genotype: str) -> float:
        """
        Call the model to get the encounter radius
        Args:
            mass:     mass of adult
            genotype: genotype of adult

        Returns:
            the radius of encounters
        """

        return self.radius


@dclass.dataclass
class Fecundity(models.Model):
    """
    Class to contain fecundity model for adults
        Mean (mu(t)) is given by
            mu(t) = 2*m/(1 + exp(r*t))
        where
            m = maximum
            r = decay rate

        Sample value from Poisson distribution with mu(t) as mean

    Variables:
        maximum: maximum probability
        decay:   decay rate after maximum

    Methods:
        __call__: call the model
    """

    model_key = keyword.fecundity

    maximum: float
    decay:   float

    def _lam(self, time: int) -> float:
        """
        Get the mean for the distribution

        Args:
            time: time as adult

        Returns:
            mean of Poisson distribution
        """

        return (self.maximum * 2)/(np.exp(self.decay * time) + 1)

    def __call__(self, age:      int,
                       mass:     float,
                       genotype: str) -> int:
        """
        Get the number of egg masses which can be laid

        Args:
            age:      time as adult
            mass:     mass of adult
            genotype: genotype of adult

        Returns:
            Number of egg_masses
        """

        lam = self._lam(age)

        return int(stats.poisson.rvs(lam))


@dclass.dataclass
class Density(models.Model):
    """
    Class to density model for laying eggs:
        Probability that density is low enough:
            P(n) = exp(-(n/a)^b)
        where
            n = number of eggs and larvae
            a = eta
            b = gamma

    Variables:
        eta:   density scale parameter
        gamma: density exponent

    Methods:
        __call__: call the model
    """

    model_key = keyword.density

    eta:   float
    gamma: float

    def _prob(self, number: int) -> float:
        """
        Get the probability

        Args:
            number: number of eggs/larvae

        Returns:
            the probability
        """

        return np.exp(-((number/self.eta)**self.gamma))

    def __call__(self, number:   int,
                       mass:     float,
                       genotype: str) -> bool:
        """
        Determine if density is low enough

        Args:
            number:   number of eggs and larvae
            mass:     mass of the adult
            genotype: genotype of adult

        Returns:
            if the density is low enough
        """

        return rnd.random() <= self._prob(number)
