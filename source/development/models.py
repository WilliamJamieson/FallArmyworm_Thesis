# TODO: UPDATE THESE FOR NEW SYSTEMS

import numpy.random as rnd
import scipy.stats  as stats

import source.hints    as hints
import source.keywords as keywords

import source.models.model as model


class Egg(model.Model):
    """
    Class to contain development model for egg
        USES CDF for Normal Distribution for probability
        Checks if minimum time has been achieved

    Variables:
        _mu:      mean time for development
        _sigma:   standard deviation in mean time
        _minimum: minimum time to wait (optional)
    """

    keyword = keywords.egg_develop

    def __init__(self, mu:      hints.variable,
                       sigma:   hints.variable,
                       minimum: hints.variable):
        self._mu      = mu
        self._sigma   = sigma
        self._minimum = minimum

    @property
    def _use_minimum(self) -> bool:
        """Determine if we use the minimum"""

        return self._minimum is not None

    def _min(self, time:      int,
                   phenotype: str) -> bool:
        """
        Determine if min time has been achieved

        Args:
            time:      time egg has existed
            phenotype: phenotype of the egg

        Returns:
            if min time has been achieved
        """

        if self._use_minimum:
            return self._minimum(phenotype) <= time
        else:
            return True

    def _cdf(self, time:      int,
                   phenotype: str) -> float:
        """
        Evaluate the CDF for the normal distribution at current time

        Args:
            time:      time egg has existed
            phenotype: phenotype of the egg

        Returns:
            a probability from normal
        """

        loc   = self._mu(phenotype)
        scale = self._sigma(phenotype)

        return stats.norm.cdf(time, loc=loc, scale=scale)

    def _prob(self, time:      int,
                    phenotype: str) -> float:
        """
        Get a probability to test against

        Args:
            time:      time egg has existed
            phenotype: phenotype of the egg

        Returns:
            a probability of development
        """

        if self._min(time, phenotype):
            return self._cdf(time, phenotype)
        else:
            return 0

    def __call__(self, mass:      float,
                       time:      int,
                       phenotype: str) -> bool:
        """
        Determine if an egg develops

        Args:
            mass:      mass of egg
            time:      time egg has existed
            phenotype: phenotype of the egg

        Returns:
            if egg develops or not
        """

        return rnd.random() <= self._prob(time, phenotype)

    @classmethod
    def setup(cls, *args, **kwargs) -> 'Egg':
        """
        Setup the model

        Args:
            *args:    args[0]=mu tuple, args[1]=sigma tuple,
                      args[3]=minimum tuple (optional)
            **kwargs: other args

        Returns:
            setup class
        """

        mu    = cls.setup_variable(*args[0], **kwargs)
        sigma = cls.setup_variable(*args[1], **kwargs)

        if len(args) > 2:
            minimum = cls.setup_variable(*args[2], **kwargs)
        else:
            minimum = None

        return cls(mu, sigma, minimum)


class Larva(model.Model):
    """
    Class to contain development model for larva
        USES CDF for Normal Distribution for probability
        Checks if minimum time has been achieved

    Variables:
        _mu:      mean mass for development
        _sigma:   standard deviation in mean mass
        _minimum: minimum time to wait (optional)
    """

    keyword = keywords.larva_develop

    def __init__(self, mu:      hints.variable,
                       sigma:   hints.variable,
                       minimum: hints.variable):
        self._mu      = mu
        self._sigma   = sigma
        self._minimum = minimum

    @property
    def _use_minimum(self) -> bool:
        """Determine if we use the minimum"""

        return self._minimum is not None

    def _min(self, time:      int,
                   phenotype: str) -> bool:
        """
        Determine if min time has been achieved

        Args:
            time:      time larva has existed
            phenotype: phenotype of larva

        Returns:
            if min time has been achieved
        """

        if self._use_minimum:
            return self._minimum(phenotype) <= time
        else:
            return True

    def _cdf(self, mass:      float,
                   phenotype: str) -> float:
        """
        Evaluate the CDF for the normal distribution at current mas

        Args:
            mass:      mass of larva
            phenotype: phenotype of larva

        Returns:
            a probability from normal
        """

        loc   = self._mu(   phenotype)
        scale = self._sigma(phenotype)

        return stats.norm.cdf(mass, loc=loc, scale=scale)

    def _prob(self, mass:      float,
                    time:      int,
                    phenotype: str) -> float:
        """
        Get a probability to test against

        Args:
            mass:      mass of larva
            time:      time larva has existed
            phenotype: phenotype of larva

        Returns:
            a probability of development
        """

        if self._min(time, phenotype):
            return self._cdf(mass, phenotype)
        else:
            return 0

    def __call__(self, mass:      float,
                       time:      int,
                       phenotype: str) -> bool:
        """
        Determine if an larva develops

        Args:
            mass:      mass of larva
            time:      time larva has existed
            phenotype: phenotype of larva

        Returns:
            if larva develops or not
        """

        return rnd.random() <= self._prob(mass, time, phenotype)

    @classmethod
    def setup(cls, *args, **kwargs) -> 'Larva':
        """
        Setup the model

        Args:
            *args:    args[0]=mu tuple, args[1]=sigma tuple,
                      args[3]=minimum tuple (optional)
            **kwargs: other args

        Returns:
            setup class
        """

        mu    = cls.setup_variable(*args[0], **kwargs)
        sigma = cls.setup_variable(*args[1], **kwargs)

        if len(args) > 2:
            minimum = cls.setup_variable(*args[2], **kwargs)
        else:
            minimum = None

        return cls(mu, sigma, minimum)


class Pupa(model.Model):
    """
    Class to contain development model for pupa
        USES CDF for Normal Distribution for probability
        Checks if minimum time has been achieved

    Variables:
        _mu:      mean mass for development
        _sigma:   standard deviation in mean mass
        _minimum: minimum time to wait (optional)
    """

    keyword = keywords.pupa_develop

    def __init__(self, mu:      hints.variable,
                       sigma:   hints.variable,
                       minimum: hints.variable):
        self._mu      = mu
        self._sigma   = sigma
        self._minimum = minimum

    @property
    def _use_minimum(self) -> bool:
        """Determine if we use the minimum"""

        return self._minimum is not None

    def _min(self, time:      int,
             phenotype: str) -> bool:
        """
        Determine if min time has been achieved

        Args:
            time:      time pupa has existed
            phenotype: phenotype of pupa

        Returns:
            if min time has been achieved
        """

        if self._use_minimum:
            return self._minimum(phenotype) <= time
        else:
            return True

    def _cdf(self, time:      float,
                   phenotype: str) -> float:
        """
        Evaluate the CDF for the normal distribution at current mas

        Args:
            time:      time pupa has existed
            phenotype: phenotype of pupa

        Returns:
            a probability from normal
        """

        loc   = self._mu(   phenotype)
        scale = self._sigma(phenotype)

        return stats.norm.cdf(time, loc=loc, scale=scale)

    def _prob(self, time:      int,
                    phenotype: str) -> float:
        """
        Get a probability to test against

        Args:
            time:      time pupa has existed
            phenotype: phenotype of pupa

        Returns:
            a probability of development
        """

        if self._min(time, phenotype):
            return self._cdf(time, phenotype)
        else:
            return 0

    def __call__(self, mass:      float,
                       time:      int,
                       phenotype: str) -> bool:
        """
        Determine if an pupa develops

        Args:
            mass:      mass of pupa
            time:      time pupa has existed
            phenotype: phenotype of pupa

        Returns:
            if pupa develops or not
        """

        return rnd.random() <= self._prob(time, phenotype)

    @classmethod
    def setup(cls, *args, **kwargs) -> 'Pupa':
        """
        Setup the model

        Args:
            *args:    args[0]=mu tuple, args[1]=sigma tuple,
                      args[3]=minimum tuple (optional)
            **kwargs: other args

        Returns:
            setup class
        """

        mu    = cls.setup_variable(*args[0], **kwargs)
        sigma = cls.setup_variable(*args[1], **kwargs)

        if len(args) > 2:
            minimum = cls.setup_variable(*args[2], **kwargs)
        else:
            minimum = None

        return cls(mu, sigma, minimum)
