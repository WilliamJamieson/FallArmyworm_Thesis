import dataclasses   as dclass
import numpy         as np
import numpy.random  as rnd

import source.hint    as hint
import source.keyword as keyword

import source.simulation.models as models


@dclass.dataclass
class Larva(models.Model):
    """
    Class to describe survival model for larvae
        - assumes probability is a general logistic:
            P(m) = L + (U-L)/(1 + exp(-k(m-m0)))

            L  = minimum probability
            U  = maximum probability
            m0 = inflection point
            k  = steepness
            m  = mass


    Variables:
        minimum:    minimum probability
        maximum:    maximum probability
        inflection: inflection point
        steepness:  steepness of transition

    Methods:
        __call__: call the model
    """

    model_key = keyword.larva_survival

    minimum: hint.bt_variable
    maximum: hint.bt_variable

    inflection: hint.variable
    steepness:  hint.variable

    def _logistic(self, mass:     float,
                        genotype: str,
                        bt:       str) -> float:
        """
        Evaluate the generalized logistic function above

        Args:
            mass:     insect mass
            genotype: larva's genotype
            bt:       bt state of plant

        Returns:
            value of generalized logistic function described
        """

        lower = self.minimum[bt][genotype]
        upper = self.maximum[bt][genotype]

        m0 = self.inflection[genotype]
        k  = self.steepness[ genotype]

        top = upper - lower
        bot = np.exp(-k*(mass - m0)) + 1

        return lower + top/bot

    def __call__(self, mass:     float,
                       genotype: str,
                       bt:       str) -> bool:
        """
        Run the survival model

        Args:
            mass:     insect mass
            genotype: larva's genotype
            bt:       bt state of plant

        Returns:
            result of flipping a coin weighted by logistic function's resulting
            probability
        """

        return rnd.random() <= self._logistic(mass, genotype, bt)


@dclass.dataclass
class LarvaFixed(models.Model):
    """
    Class to describe a survival model for larvae with fixed probabilities

    Variables:
        prob: probabilities
    """

    model_key = keyword.larva_survival

    prob: hint.bt_variable

    def __call__(self, mass:     float,
                       genotype: str,
                       bt:       str) -> bool:
        """
        Run the survival model

        Args:
            mass:     insect mass
            genotype: larva's genotype
            bt:       bt state of plant

        Returns:
            result of flipping a coin weighted by logistic function's resulting
            probability
        """

        prob = self.prob[bt][genotype]

        return rnd.random() <= prob


@dclass.dataclass
class Fixed(models.Model):
    """
    Class to describe a survival model with a fixed probability

    Variables:
        prob: probability of survival

    Methods:
        __call__: call the model
    """

    prob: float

    def __call__(self, mass: float, *args) -> bool:
        """
        Call the model to determine if the agent survives

        Args:
            mass:  mass of agent
            *args: genotype and bt (possibly)

        Returns:
            if egg survives
        """

        return rnd.random() <= self.prob


@dclass.dataclass
class Egg(Fixed):
    """
    Class to describe the survival model for single egg

    Variables:
        prob: probability of survival

    Methods:
        __call__: call the model
    """

    model_key = keyword.egg_survival


@dclass.dataclass
class Pupa(Fixed):
    """
    Class to describe the survival model for pupa

    Variables:
        prob: probability of survival

    Methods:
        __call__: call the model
    """

    model_key = keyword.pupa_survival


@dclass.dataclass
class Adult(Fixed):
    """
    Class to describe the survival model for adult

    Variables:
        prob: probability of survival

    Methods:
        __call__: call the model
    """

    model_key = keyword.adult_survival
