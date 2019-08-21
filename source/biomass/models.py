import dataclasses as dclass
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

        sigma: standard deviation in egg_mass

        maximum: maximum allowed size
            dict:
                key: genotype key
                value: max_size

    Methods:
        __call__: call the model
    """

    model_key = keyword.init_mass

    mu:      hint.variable
    sigma:   float
    maximum: hint.variable

    def _lower(self, mu: float) -> float:
        """
        Get mass distribution lower bound

        Args:
            mu: mean of distribution

        Returns:
            adjusted lower bound
        """

        return (-mu)/self.sigma

    def _upper(self, mu:       float,
                     number:   int,
                     genotype: str) -> float:
        """
        Get mass distribution upper bound

        Args:
            mu:       mean of distribution
            number:   number of eggs
            genotype: genotype of insect

        Returns:
            adjusted upper bound
        """

        upper = number*self.maximum[genotype]

        return (upper - mu)/self.sigma

    def __call__(self, number:   int,
                       genotype: str) -> float:
        """
        Get the total mass of the egg_mass

        Args:
            number:   number of eggs
            genotype: insect genotype

        Returns:
            mass of egg_mass
        """

        mu = self.mu[genotype]

        lower = self._lower(mu)
        upper = self._upper(mu, number, genotype)

        return float(stats.truncnorm.rvs(lower, upper,
                                         loc=mu, scale=self.sigma))


@dclass.dataclass
class InitJuvenile(models.Model):
    """
    Class to contain a initial mass model for larvae:
        Is made of 2 parts:
            1. model for number of eggs in an egg_mass
            2. model for mass of egg_mass

    Variables:
        lam: average number of eggs in egg_mass

        mu:    average mass of an egg_mass
            dict:
                key: genotype key
                value: mu value

        sigma: standard deviation in egg_mass

        maximum: maximum allowed size
            dict:
                key: genotype key
                value: max_size

    Methods:
        __call__: call the model
    """

    model_key = keyword.init_juvenile

    lam:     float
    mu:      hint.variable
    sigma:   float
    maximum: hint.variable

    def _number(self) -> float:
        """
        Get the number of eggs in egg_mass

        Returns:
            the number of eggs
        """

        return stats.poisson.rvs(self.lam)

    def _lower(self, mu: float) -> float:
        """
        Get mass distribution lower bound

        Args:
            mu: mean of distribution

        Returns:
            adjusted lower bound
        """

        return (-mu)/self.sigma

    def _upper(self, mu:       float,
                     number:   float,
                     genotype: str) -> float:
        """
        Get mass distribution upper bound

        Args:
            mu:       mean of distribution
            number:   number of eggs
            genotype: genotype of insect

        Returns:
            adjusted upper bound
        """

        upper = number*self.maximum[genotype]

        return (upper - mu)/self.sigma

    def _total_mass(self, number:   float,
                          genotype: str) -> float:
        """
        Get the total mass of the egg_mass

        Args:
            number:   number of eggs
            genotype: insect genotype

        Returns:
            mass of egg_mass
        """

        mu = self.mu[genotype]

        lower = self._lower(mu)
        upper = self._upper(mu, number, genotype)

        return stats.truncnorm.rvs(lower, upper, loc=mu, scale=self.sigma)

    def __call__(self, genotype: str) -> float:
        """
        Run complete statistical model:
            egg_mass/egg_num

        Args:
            genotype: insect genotype

        Returns:
            initial mass for one larva
        """

        num  = self._number()
        mass = self._total_mass(num, genotype)

        return float(mass/num)


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

        sigma: standard deviation in mass

        maximum: maximum allowed size
            dict:
                key: genotype key
                value: max_size

    Methods:
        __call__: call the model

    Constructors:
        setup: setup the mathematical model
    """

    model_key = keyword.init_mature

    mu:      hint.variable
    sigma:   float
    maximum: hint.variable

    def _lower(self, mu: float) -> float:
        """
        Get mass distribution lower bound

        Args:
            mu: mean of distribution

        Returns:
            adjusted lower bound
        """

        return (-mu) / self.sigma


    def _upper(self, mu:       float,
                     genotype: str) -> float:
        """
        Get mass distribution upper bound

        Args:
            mu:       mean of distribution
            genotype: genotype of insect

        Returns:
            adjusted upper bound
        """

        upper = self.maximum[genotype]

        return (upper - mu) / self.sigma

    def __call__(self, genotype: str) -> float:
        """
        Get the mass of the mature insect

        Args:
            genotype: insect genotype

        Returns:
            mass of mature insect
        """

        mu = self.mu[genotype]

        lower = self._lower(mu)
        upper = self._upper(mu, genotype)

        return float(stats.truncnorm.rvs(lower, upper,
                                         loc=mu, scale=self.sigma))


@dclass.dataclass
class InitPlant(models.Model):
    """
    Class to model the mass of food in plant:
        - truncated normal between 0 and max

    Variables:
        mu: average mass food in plant

        sigma: standard deviation of food in plant

        maximum: maximum allowed food

    Methods:
        __call__: call the model
    """

    model_key = keyword.init_plant

    mu:      float
    sigma:   float
    maximum: float

    def _lower(self) -> float:
        """
        Get mass distribution lower bound

        Returns:
            adjusted lower bound
        """

        return (-self.mu) / self.sigma


    def _upper(self) -> float:
        """
        Get mass distribution upper bound

        Returns:
            adjusted upper bound
        """

        return (self.maximum - self.mu) / self.sigma

    def __call__(self, bt: str) -> float:
        """
        Get the mass of food on the plant

        Args:
            bt: the bt state of the plant

        Returns:
            mass of food in plant
        """

        lower = self._lower()
        upper = self._upper()

        return float(stats.truncnorm.rvs(lower, upper,
                                         loc=self.mu, scale=self.sigma))
