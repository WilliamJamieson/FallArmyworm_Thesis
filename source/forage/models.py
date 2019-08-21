# TODO: UPDATE THESE FOR NEW SYSTEMS

import scipy.stats   as stats
import scipy.special as spcl
import numpy         as np
import numpy.random  as rnd

import source.hints    as hints
import source.keywords as keywords

import source.models.model as model


class LeafBase(model.Model):
    """
    Base class for leaf forage models

    Methods:
        __call__: call the model
    """

    keyword = keywords.leaf_forage

    def __call__(self, mass:      float,
                       leaf:      float,
                       bt:        str,
                       phenotype: str) -> float:
        """
        Call the model

        Args:
            mass:      mass of larva
            leaf:      mass of leaf
            bt:        plant type
            phenotype: larva phenotype

        Returns:
            biomass which can be foraged
        """

        pass


class LeafAdLibitum(LeafBase):
    """
    Class for larvae consuming leaf ad libitum:
        - ignores leaf mass present
        - assumes leaf mass does not change (no recovery model)

        Outputs 5 time maximum amount of food which can be consumed

    Variables:
        _max_gut: the maximum gut model

    Methods:
        __call__: call the model

    Constructors:
        setup: setup the mathematical model
    """

    def __init__(self, max_gut: hints.max_gut):
        self._max_gut = max_gut

    def __call__(self, mass:      float,
                       leaf:      float,
                       bt:        str,
                       phenotype: str) -> float:
        """
        Call the model

        Args:
            mass:      mass of larva
            leaf:      mass of leaf
            bt:        plant type
            phenotype: larva phenotype

        Returns:
            biomass which can be foraged
        """

        return self._max_gut(mass)*5

    @classmethod
    def setup(cls, *args, **kwargs) -> 'LeafAdLibitum':
        """
        Correctly setup class

        Args:
            *args:    arg[0]=max_gut model
            **kwargs: place holder
        Returns:
            setup class
        """

        max_gut = kwargs[keywords.max_gut]

        return cls(max_gut)
    

class LeafGutStarve(LeafAdLibitum):
    """
    Class for larvae consuming leaf with a normal distribution describing
        starvation
        - ignores leaf mass present
        - assumes leaf mass does not change (no recovery model)

        takes maximum amount of consumed food and multiplies it by a factor
        drawn from a normal distribution

    Variables:
        _max_gut: the maximum gut model
        _mu:      mean
        _sigma:   standard deviation

    Methods:
        __call__: call the model

    Constructors:
        setup: setup the mathematical model
    """

    def __init__(self, max_gut: hints.max_gut,
                       mu:      hints.variable,
                       sigma:   hints.variable):
        super().__init__(max_gut)

        self._mu    = mu
        self._sigma = sigma

    def _lower(self, phenotype: str) -> float:
        """
        Get lower bound on distribution

        Args:
            phenotype: larva phenotype

        Returns:
            lower bound on distribution
        """

        mu    = self._mu(   phenotype)
        sigma = self._sigma(phenotype)

        return (0 - mu)/sigma

    def _upper(self, phenotype: str) -> float:
        """
        Get upper bound on distribution

        Args:
            phenotype: larva phenotype

        Returns:
            upper bound on distribution
        """

        mu    = self._mu(   phenotype)
        sigma = self._sigma(phenotype)

        return (1 - mu)/sigma

    def _sample(self, phenotype: str) -> float:
        """
        Sample from the distribution

        Args:
            phenotype: larva phenotype

        Returns:
            sample from the distribution
        """

        a = self._lower(phenotype)
        b = self._upper(phenotype)

        mu    = self._mu(   phenotype)
        sigma = self._sigma(phenotype)

        return stats.truncnorm.rvs(a, b, loc=mu, scale=sigma)

    def __call__(self, mass:      float,
                       leaf:      float,
                       bt:        str,
                       phenotype: str) -> float:
        """
        Call the model

        Args:
            mass:      mass of larva
            leaf:      mass of leaf
            bt:        plant type
            phenotype: larva phenotype

        Returns:
            biomass which can be foraged
        """

        return self._sample(phenotype)*self._max_gut(mass)

    @classmethod
    def setup(cls, *args, **kwargs) -> 'LeafGutStarve':
        """
        Correctly setup class

        Args:
            *args:    arg[0]=mu, arg[1]=sigma
            **kwargs: other arguments
        Returns:
            setup class
        """

        max_gut = kwargs[keywords.max_gut]
        mu      = cls.setup_variable(*args[0], **kwargs)
        sigma   = cls.setup_variable(*args[1], **kwargs)

        return cls(max_gut, mu, sigma)


class Egg(model.Model):
    """
    Class for describing the amount of food a larva can eat from an egg_mass

        amount = factor*mass

    Variables:
        _factor: the scale factor

    Methods:
        __call__: call the model

    Constructors:
        setup: setup the mathematical model
    """

    keyword = keywords.egg_forage

    def __init__(self, factor: hints.variable):
        self._factor = factor

    def __call__(self, mass:      float,
                       phenotype: str) -> float:
        """
        Call the model

        Args:
            mass:      mass of larva to eat
            phenotype: phenotype of consumer

        Returns:
            amount of larva to eat
        """

        return self._factor(phenotype)*mass

    @classmethod
    def setup(cls, *args, **kwargs) -> 'Egg':
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


class Larva(model.Model):
    """
    Class for describing the amount of food a larva can eat from another larva

        amount = factor*mass

    Variables:
        _factor: the scale factor

    Methods:
        __call__: call the model

    Constructors:
        setup: setup the mathematical model
    """

    keyword = keywords.larva_forage

    def __init__(self, factor: hints.variable):
        self._factor = factor

    def __call__(self, mass:      float,
                       phenotype: str) -> float:
        """
        Call the model

        Args:
            mass:      mass of larva to eat
            phenotype: phenotype of consumer

        Returns:
            amount of larva to eat
        """

        return self._factor(phenotype)*mass

    @classmethod
    def setup(cls, *args, **kwargs) -> 'Larva':
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


class Fight(model.Model):
    """
    Class for describing results of a larva cannibalistic fight

        Win probability given by the function
            P(d) = 1/(1 + exp(-k*d))
        where d is the mass difference and k is the slope:
            d = m0 - m1
        so if m0 >> m1, p(d)->1
              m0 << m1, p(d)->0

    Variables:
        _slope: the steepness of the model's transition

    Methods:
        __call__: call the model

    Constructors:
        setup: setup the mathematical model
    """

    keyword = keywords.fight

    def __init__(self, slope: hints.variable):
        self._slope = slope

    @staticmethod
    def _diff(mass0: float,
              mass1: float) -> float:
        """
        Find the mass difference between mass0 and mass1 from mass0:
            mass0 - mass1

        Args:
            mass0: mass of larva running fight
            mass1: mass of target larva

        Returns:
            mass difference
        """

        return mass0 - mass1

    def _prob(self, mass0: float, mass1: float) -> float:
        """
        Evaluate the logistic model for probability

        Args:
            mass0: mass of larva running fight
            mass1: mass of target larva

        Returns:
            result of logistic evaluation
        """

        slope = self._slope()
        value = self._diff(mass0, mass1)

        x = slope*value

        return float(spcl.expit(x))

    def __call__(self, mass0: float, mass1: float) -> bool:
        """
        Call the mathematical model to make decision

        Args:
            mass0: mass of larva running fight
            mass1: mass of target larva

        Returns:
            if mass0 larva wins
        """

        return rnd.random() <= self._prob(mass0, mass1)

    @classmethod
    def setup(cls, *args, **kwargs) -> 'Fight':
        """
        Setup the model

        Args:
            *args:    arg[0]= value of slope
            **kwargs: other args

        Returns:
            the setup model
        """

        slope = cls.setup_variable(*args[0])

        return cls(slope)


class Encounter(model.Model):
    """
    Class to contain encounter model for cannibalism

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

    keyword = keywords.encounter

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
    def setup(cls, *args, **kwargs) -> 'Encounter':
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


class Radius(model.Model):
    """
    Class to contain encounter radius model for cannibalism

    Variables:
        _radius: the radius for encounters

    Methods:
        __call__: call the model

    Constructors:
        setup: setup the mathematical model
    """

    keyword = keywords.encounter_radius

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
