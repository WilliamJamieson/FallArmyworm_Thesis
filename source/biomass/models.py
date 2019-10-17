import dataclasses as dclass
import numpy       as np
import scipy.stats as stats

import source.hint    as hint
import source.keyword as keyword

import source.simulation.models as models


@dclass.dataclass
class MaxGut(models.Model):
    """
    Class to contain a max_gut model:
        max_gut = mass^(3/4)

    Methods:
        __call__: call the model
    """

    model_key = keyword.max_gut

    def __call__(self, mass: float) -> float:
        """
        Run the mathematical model:
            max_gut = mass^(3/4)

        Args:
            mass: insect mass

        Returns:
            the result of the above equation (max_gut)
        """

        return mass**0.75


@dclass.dataclass
class Growth(models.Model):
    """
    Class to contain a growth model:
        growth = alpha*energy - beta*mass

    Variables:
        alpha: alpha constant
            dict:
                key:   genotype_key
                value: alpha value
        beta: beta constant
            dict:
                key:   genotype_key
                value: beta value

    Methods:
        __call__: call the model
    """

    model_key = keyword.growth

    alpha: hint.variable
    beta:  hint.variable

    def __call__(self, mass:     float,
                       energy:   float,
                       genotype: str) -> float:
        """
        Run the mathematical model
            growth = alpha*energy - beta*mass

        Args:
            mass:     insect mass
            energy:   insect energy
            genotype: insect genotype

        Returns:
            the result of the above equation (growth)
        """

        alpha = self.alpha[genotype]
        beta  = self.beta[ genotype]

        return alpha*energy - beta*mass


@dclass.dataclass()
class InitNum(models.Model):
    """
    Class to model initial number of eggs in egg mass:
        draw from Poisson distribution

    Variables:
        lam: average number of eggs in egg_mass

    Methods:
        __call__: call the model
    """

    model_key = keyword.init_num

    lam: float

    def __call__(self, genotype: str) -> int:
        """
        Args:
            genotype: the genotype of the mother

        Returns:
            number of eggs
        """

        return int(stats.poisson.rvs(self.lam))


@dclass.dataclass
class InitMass(models.Model):
    """
    Class to model an egg_mass's total mass
        draw from a normal distribution

    Variables:
        mu:    average mass of an egg_mass
            dict:
                key: genotype key
                value: mu value

        sigma: standard deviation in mass of egg_mass
            dict:
                key: genotype key
                value: sig value

    Methods:
        __call__: call the model
    """

    model_key = keyword.init_mass

    mu:      hint.variable
    sigma:   hint.variable

    def __call__(self, genotype: str) -> float:
        """
        Get the total mass of the egg_mass

        Args:
            genotype: insect genotype

        Returns:
            mass of egg_mass
        """

        mu    = self.mu[genotype]
        sigma = self.sigma[genotype]

        return float(stats.truncnorm.rvs(0, np.inf,
                                         loc=mu, scale=sigma))


@dclass.dataclass
class InitJuvenile(models.Model):
    """
    Class to contain a initial mass model for larvae:

    Variables:
        mu:    average mass of a larva
            dict:
                key: genotype key
                value: mu value

        sigma: standard deviation in mass of larva
            dict:
                key: genotype key
                value: sig value

    Methods:
        __call__: call the model
    """

    model_key = keyword.init_juvenile

    mu:    hint.variable
    sigma: hint.variable

    def __call__(self, genotype: str) -> float:
        """
        Get the mass of a new larva

        Args:
            genotype: insect genotype

        Returns:
            mass of egg_mass
        """

        mu    = self.mu[genotype]
        sigma = self.sigma[genotype]

        return float(stats.truncnorm.rvs(0, np.inf,
                                         loc=mu, scale=sigma))


@dclass.dataclass
class InitMature(models.Model):
    """
    Class to model the mass of a mature insect:
        - truncated normal between 0 and max

    Variables:
        mu:    average mass of a mature insect
            dict:
                key: genotype key
                value: mu value

        sigma: standard deviation in mass of larva
            dict:
                key: genotype key
                value: sig value

    Methods:
        __call__: call the model

    Constructors:
        setup: setup the mathematical model
    """

    model_key = keyword.init_mature

    mu:      hint.variable
    sigma:   hint.variable

    def __call__(self, genotype: str) -> float:
        """
        Get the mass of a new larva

        Args:
            genotype: insect genotype

        Returns:
            mass of egg_mass
        """

        mu    = self.mu[genotype]
        sigma = self.sigma[genotype]

        return float(stats.truncnorm.rvs(0, np.inf,
                                         loc=mu, scale=sigma))


@dclass.dataclass
class InitPlant(models.Model):
    """
    Class to model the mass of food in plant:
        - truncated normal between 0 and max

    Variables:
        mu: average mass food in plant

        sigma: standard deviation of food in plant

    Methods:
        __call__: call the model
    """

    model_key = keyword.init_plant

    mu:      float
    sigma:   float

    def __call__(self, bt: str) -> float:
        """
        Get the mass of food on the plant

        Args:
            bt: the bt state of the plant

        Returns:
            mass of food in plant
        """

        return float(stats.truncnorm.rvs(0, np.inf,
                                         loc=self.mu, scale=self.sigma))
