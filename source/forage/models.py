import dataclasses   as dclass
import scipy.stats   as stats
import scipy.special as spcl
import numpy         as np
import numpy.random  as rnd

import source.hint    as hint
import source.keyword as keyword

import source.simulation.models as models


@dclass.dataclass
class PlantBase(models.Model):
    """
    Base class for Plant forage models

    Methods:
        __call__: call the model
    """

    model_key = keyword.plant_forage

    steps: int

    def __call__(self, mass:     float,
                       plant:    float,
                       genotype: str,
                       bt:       str) -> float:
        """
        Call the model

        Args:
            mass:     mass of larva
            plant:    mass of plant
            genotype: larva genotype
            bt:       plant type

        Returns:
            biomass which can be foraged
        """

        pass


@dclass.dataclass
class PlantAdLibitum(PlantBase):
    """
    Class for larvae consuming leaf ad libitum:
        - ignores leaf mass present
        - assumes leaf mass does not change (no recovery model)

        Outputs 5 time maximum amount of food which can be consumed

    Variables:
        max_gut: the maximum gut model

    Methods:
        __call__: call the model
    """

    max_gut: hint.max_gut

    def __call__(self, mass:     float,
                       plant:    float,
                       genotype: str,
                       bt:       str) -> float:
        """
        Call the model

        Args:
            mass:     mass of larva
            plant:    mass of plant
            genotype: larva genotype
            bt:       plant type

        Returns:
            biomass which can be foraged
        """

        return self.max_gut(mass) / self.steps


@dclass.dataclass
class PlantStarve(PlantBase):
    """
    Class for larvae consuming leaf with a normal distribution describing
        starvation

        takes maximum amount of consumed food available and multiplies it by
            a factor
        drawn from a normal distribution

    Variables:
        mu:    mean factor in product
        sigma: standard deviation

    Methods:
        __call__: call the model
    """

    theta:   float
    sigma:   float
    max_gut: hint.max_gut

    def _mu(self, mass: float) -> float:
        """
        Get the mean amount of food that can be consumed

        Args:
            mass: mass of the larva

        Returns:
            mean amount of food
        """

        factor = self.theta / self.steps

        return factor * self.max_gut(mass)

    def __call__(self, mass:     float,
                       plant:    float,
                       genotype: str,
                       bt:       str) -> float:
        """
        Call the model

        Args:
            mass:     mass of larva
            plant:    mass of plant
            genotype: larva genotype
            bt:       plant type

        Returns:
            biomass which can be foraged
        """

        return float(stats.truncnorm.rvs(0, np.inf,
                                         loc=self._mu(mass), scale=self.sigma))


@dclass.dataclass
class Egg(models.Model):
    """
    Class for describing the amount of food a larva can eat from an egg_mass
        amount = factor*mass

    Variables:
        factor: the scale factor

    Methods:
        __call__: call the model

    Constructors:
        setup: setup the mathematical model
    """

    model_key = keyword.egg_forage

    factor: float

    def __call__(self, egg_mass: float,
                       mass:     float,
                       genotype: str) -> float:
        """
        Call the model

        Args:
            egg_mass: mass of egg_mass
            mass:     mass of larva
            genotype: genotype of consumer

        Returns:
            amount of larva to eat
        """

        return self.factor*egg_mass


@dclass.dataclass
class Larva(models.Model):
    """
    Class for describing the amount of food a larva can eat from another larva

        amount = factor*mass

    Variables:
        factor: the scale factor

    Methods:
        __call__: call the model
    """

    model_key = keyword.larva_forage

    factor: float

    def __call__(self, target_mass: float,
                       mass:        float,
                       genotype:    str) -> float:
        """
        Call the model

        Args:
            target_mass: mass of target larva
            mass:        mass of larva
            genotype:    genotype of consumer

        Returns:
            amount of larva to eat
        """

        return self.factor*target_mass


@dclass.dataclass
class Loss(models.Model):
    """
    Class for describing the probability that a larva leaves a target food:

        Fixed probability

    Variables:
        prob: probability of leaving target
    """

    model_key = keyword.loss

    slope: hint.variable
    mid:   hint.variable

    max_gut:      hint.max_gut
    forage_egg:   hint.forage_egg
    forage_larva: hint.forage_larva

    def _diff(self, mass:        float,
                    target_mass: float,
                    genotype:    str,
                    target_key:  str) -> float:
        """
        Find the diff between amount and gut

        Args:
            mass:        mass of larva
            target_mass: mass of target
            genotype:    genotype of larva
            target_key:  type of target

        Returns:
            Food - gut
        """

        gut = self.max_gut(mass)

        if target_key == keyword.egg_mass:
            food = self.forage_egg(target_mass, mass, genotype)
        else:
            food = self.forage_larva(target_mass, mass, genotype)

        return food - gut

    def _prob(self, mass:        float,
                    target_mass: float,
                    genotype:    str,
                    target_key:  str) -> float:
        """
        Find the probability of staying

        Args:
            mass:        mass of larva
            target_mass: mass of target
            genotype:    genotype of larva
            target_key:  type of target

        Returns:
            probability of staying with food source
        """

        d = self._diff(mass, target_mass, genotype, target_key)
        r = self.slope[target_key]
        q = self.mid[  target_key]

        return 1 / (q * np.exp(-r*d) + 1)

    def __call__(self, mass:        float,
                       target_mass: float,
                       genotype:    str,
                       target_key:  str) -> bool:
        """
        Call the model

        Args:
            mass:        mass of larva
            target_mass: mass of target
            genotype:    genotype of larva
            target_key:  type of target

        Returns:
            if we leave the target
        """

        return rnd.random() <= self._prob(mass, target_mass,
                                          genotype, target_key)


@dclass.dataclass
class Fight(models.Model):
    """
    Class for describing results of a larva cannibalistic fight

        Win probability given by the function
            P(d) = 1/(1 + exp(-k*d))
        where d is the mass difference and k is the slope:
            d = m0 - m1
        so if m0 >> m1, p(d)->1
              m0 << m1, p(d)->0

    Variables:
        slope: the steepness of the model's transition

    Methods:
        __call__: call the model
    """

    model_key = keyword.fight

    slope: float

    def _prob(self, mass0: float,
                    mass1: float) -> float:
        """
        Evaluate the logistic model for probability

        Args:
            mass0: mass of larva running fight
            mass1: mass of target larva

        Returns:
            result of logistic evaluation
        """

        x = self.slope*(mass0 - mass1)

        # noinspection PyTypeChecker
        return spcl.expit(x)

    def __call__(self, mass0: float,
                       mass1: float) -> bool:
        """
        Call the mathematical model to make decision

        Args:
            mass0: mass of larva running fight
            mass1: mass of target larva

        Returns:
            if mass0 larva wins
        """

        return rnd.random() <= self._prob(mass0, mass1)


@dclass.dataclass
class Encounter(models.Model):
    """
    Class to contain encounter model for cannibalism

        Probability for an encounter is given via:
            p(n) = 1 - exp(-k*n)
        where n is the number of other individuals and k is the scale factor

    Variables:
        factor: scale factor for encounters

    Methods:
        __call__: call the model
    """

    model_key = keyword.encounter

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
            number:   number of other individuals
            mass:     mass of consumer
            genotype: genotype of consumer

        Returns:
            if an encounter occurs
        """

        return rnd.random() <= self._prob(number)


@dclass.dataclass
class Radius(models.Model):
    """
    Class to contain encounter radius model for cannibalism

    Variables:
        radius: the radius for encounters

    Methods:
        __call__: call the model
    """

    model_key = keyword.radius

    radius: float

    def __call__(self, mass:     float,
                       genotype: str) -> float:
        """
        Call the model to get the encounter radius

        Args:
            mass:     mass of larva
            genotype: genotype of larva

        Returns:
            the radius of encounters
        """

        return self.radius
