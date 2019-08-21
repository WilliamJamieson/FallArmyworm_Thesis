# TODO: UPDATE THESE FOR NEW SYSTEMS

import numpy        as np
import numpy.random as rnd
import scipy.stats  as stats

import source.hints    as hints
import source.keywords as keywords

import source.models.model as model


class Sex(model.Model):
    """
    Class to contain a model for the adult sex:
        P is the probability of being female

    Variables:
        _prob: the probability of being female

    Methods:
        __call__: call the model

    Constructors:
        setup: setup the mathematical model
    """

    keyword = keywords.sex

    def __init__(self, prob: hints.variable):
        self._prob = prob

    def __call__(self) -> bool:
        """
        Call model to determine if female

        Returns:
            if this is female
        """

        return rnd.random() <= self._prob()

    @classmethod
    def setup(cls, *args, **kwargs) -> 'Sex':
        """
        Setup the model

        Args:
            *args:    args[0]=prob
            **kwargs: place holder

        Returns:
            the setup model
        """

        prob = cls.setup_variable(*args[0])

        return cls(prob)


class Mating(model.Model):
    """
    Class to contain encounter model for mating

        Probability for an encounter is given via:
            p(n) = 1 - exp(-k*n)
        where n is the number of other individuals and k is the scale factor

    Variables:
        _factor: scale factor for encounters

    Methods:
        __call__: call the model

    Constructors:
        setup: setup the mathematical model
    """

    keyword = keywords.mating

    def __init__(self, factor: hints.variable):
        self._factor = factor

    def _prob(self, number:    int,
              phenotype: str) -> float:
        """
        Get the probability for an encounter

        Args:
            number:    number of other individuals
            phenotype: phenotype of consumer

        Returns:
            probability of an encounter
        """

        exp = -self._factor(phenotype)*number

        return 1 - np.exp(exp)

    def __call__(self, number:    int,
                 mass:      float,
                 phenotype: str) -> bool:
        """
        Make an encounter decision

        Args:
            number:    number of other individuals
            mass:      mass of consumer
            phenotype: phenotype of consumer

        Returns:
            if an encounter occurs
        """

        return rnd.random() <= self._prob(number, phenotype)

    @classmethod
    def setup(cls, *args, **kwargs) -> 'Mating':
        """
        Correctly setup class

        Args:
            *args:    arg[0]=factor
            **kwargs: other arguments
        Returns:
            setup class
        """

        factor = cls.setup_variable(*args[0], **kwargs)

        return cls(factor)


class Fecundity(model.Model):
    """
    Class to contain fecundity model for adults
        Mean (mu(t)) is given by
            mu(t) = 2*m/(1 + exp(r*t))
        where
            m = maximum
            r = decay rate

        Sample value from Poisson distribution with mu(t) as mean

    Variables:
        _maximum: maximum probability
        _decay:   decay rate after maximum

    Methods:
        __call__: call the model

    Constructors:
        setup: setup the mathematical model
    """

    keyword = keywords.fecundity

    def __init__(self, maximum: hints.variable,
                       decay:   hints.variable):
        self._maximum = maximum
        self._decay   = decay

    def _mu(self, time:      int,
                  phenotype: str) -> float:
        """
        Get the mean for the distribution

        Args:
            time:      time as adult
            phenotype: phenotype of adult

        Returns:
            mean of Poisson distribution
        """

        m = self._maximum(phenotype)
        r = self._decay(  phenotype)

        return (m * 2)/(np.exp(r*time) + 1)

    def __call__(self, time:      int,
                       mass:      float,
                       phenotype: str) -> int:
        """
        Get the number of egg masses which can be laid

        Args:
            time:      time as adult
            mass:      mass of adult
            phenotype: phenotype of adult

        Returns:
            Number of egg_masses
        """

        mu = self._mu(time, phenotype)

        return int(stats.poisson.rvs(mu))

    @classmethod
    def setup(cls, *args, **kwargs) -> 'Fecundity':
        """
        Correctly setup class

        Args:
            *args:    arg[0]=maximum
                      arg[1]=decay
            **kwargs: other arguments
        Returns:
            setup class
        """

        maximum = cls.setup_variable(*args[0], **kwargs)
        decay   = cls.setup_variable(*args[1], **kwargs)

        return cls(maximum, decay)


class Density(model.Model):
    """
    Class to density model for laying eggs:
        Probability that density is low enough:
            P(n) = exp(-(n/a)^b)
        where
            n = number of eggs and larvae
            a = eta
            b = gamma

    Variables:
        _eta:   density scale parameter
        _gamma: density exponent

    Methods:
        __call__: call the model

    Constructors:
        setup: setup the mathematical model
    """

    keyword = keywords.density

    def __init__(self, eta:   hints.variable,
                       gamma: hints.variable):
        self._eta   = eta
        self._gamma = gamma

    def _prob(self, number:    int,
                   phenotype: str) -> float:
        """
        Get the probability

        Args:
            number:    number of eggs/larvae
            phenotype: phenotype of adult

        Returns:
            the probability
        """

        a = self._eta(  phenotype)
        b = self._gamma(phenotype)

        return np.exp(-((number/a)**b))

    def __call__(self, number:    int,
                       mass:      float,
                       phenotype: str) -> bool:
        """
        Determine if density is low enough

        Args:
            number:    number of eggs and larvae
            mass:      mass of the adult
            phenotype: phenotype of adult

        Returns:
            if the density is low enough
        """

        return rnd.random() <= self._prob(number, phenotype)

    @classmethod
    def setup(cls, *args, **kwargs) -> 'Density':
        """
        Correctly setup class

        Args:
            *args:    arg[0]=eta
                      arg[1]=gamma
            **kwargs: other arguments
        Returns:
            setup class
        """

        eta   = cls.setup_variable(*args[0], **kwargs)
        gamma = cls.setup_variable(*args[1], **kwargs)

        return cls(eta, gamma)


class Radius(model.Model):
    """
    Class to contain mate radius model

    Variables:
        _radius: the radius for mates

    Methods:
        __call__: call the model

    Constructors:
        setup: setup the mathematical model
    """

    keyword = keywords.mate_radius

    def __init__(self, radius: hints.variable):
        self._radius = radius

    def __call__(self, mass:      float,
                       phenotype: str) -> int:
        """
        Call the model to get the encounter radius
        Args:
            mass:      mass of larva
            phenotype: phenotype of larva

        Returns:
            the radius of encounters
        """

        return self._radius(phenotype)

    @classmethod
    def setup(cls, *args, **kwargs) -> 'Radius':
        """
        Correctly setup class

        Args:
            *args:    arg[0]=radius
            **kwargs: other arguments
        Returns:
            setup class
        """

        radius = cls.setup_variable(*args[0], **kwargs)

        return cls(radius)
