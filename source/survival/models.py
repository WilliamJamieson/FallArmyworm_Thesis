# TODO: UPDATE THESE FOR NEW SYSTEMS

import numpy        as np
import numpy.random as rnd

import source.hints    as hints
import source.keywords as keywords

import source.models.model as model


class MassSurvive(model.Model):
    """
    Class to describe survival model which depends on mass
        - assumes probability is a general logistic:
            P(m) = L + (U-L)/(1 + exp(-k(m-m0)))

            L  = minimum probability
            U  = maximum probability
            m0 = inflection point
            k  = steepness


    Variables:
        _minimum:    minimum probability
        _maximum:    maximum probability
        _inflection: inflection point
        _steepness:  steepness of transition

    Methods:
        __call__: call the model

    Constructors:
        setup: setup the mathematical model
    """

    def __init__(self, minimum:    hints.variable,
                       maximum:    hints.variable,
                       inflection: hints.variable,
                       steepness:  hints.variable):
        self._minimum    = minimum
        self._maximum    = maximum
        self._inflection = inflection
        self._steepness  = steepness

    def _logistic(self, mass:      float,
                        phenotype: str) -> float:
        """
        Evaluate the generalized logistic function above

        Args:
            mass:      insect mass
            phenotype: insect phenotype

        Returns:
            value of generalized logistic function described
        """

        low = self._minimum(   phenotype)
        up  = self._maximum(   phenotype)
        m0  = self._inflection(phenotype)
        k   = self._steepness( phenotype)

        top = up - low
        bot = np.exp(-k*(mass - m0)) + 1

        return low + top/bot

    def __call__(self, mass:      float,
                       phenotype: str) -> bool:
        """
        Run the survival model
        Args:
            mass:      insect mass
            phenotype: insect phenotype

        Returns:
            result of flipping a coin weighted by logistic function's resulting
            probability
        """

        return rnd.random() <= self._logistic(mass, phenotype)

    @classmethod
    def setup(cls, *args, **kwargs) -> 'MassSurvive':
        """
        Correctly setup the class

        Args:
            *args: arg[0]=minimum, arg[1]=maximum, arg[2]=inflection,
                   arg[3]=steepness
            **kwargs: other args

        Returns:
            correctly initiated class
        """

        minimum    = cls.setup_variable(*args[0], **kwargs)
        maximum    = cls.setup_variable(*args[1], **kwargs)
        inflection = cls.setup_variable(*args[2], **kwargs)
        steepness  = cls.setup_variable(*args[3], **kwargs)

        return cls(minimum, maximum, inflection, steepness)


class LarvaSurvive(model.Model):
    """
    Class to describe survival model for larva, assumes on different types
        of plant with different models


    Variables:
        _wild: wild type plant model (mass dependent)
        _bt:   bt   type plant model (mass dependent)

    Methods:
        __call__: call the model

    Constructors:
        setup: setup the mathematical model
    """

    keyword = keywords.larva_survive

    def __init__(self, wild: MassSurvive,
                       bt:   MassSurvive):
        self._wild = wild
        self._bt   = bt

    def __call__(self, mass:      float,
                       phenotype: str,
                       bt:        str) -> bool:
        """
        Evaluate the model

        Args:
            mass:      insect mass
            phenotype: insect phenotype
            bt:        plant type

        Returns:
            result of survival test
        """

        if bt == keywords.wild:
            return self._wild(mass, phenotype)
        elif bt == keywords.bt:
            return self._bt(mass, phenotype)
        else:
            raise RuntimeError('Invalid plant type used')

    @classmethod
    def setup(cls, *args, **kwargs) -> 'LarvaSurvive':
        """
        Setup the class correctly

        Args:
            *args:    args[0]=wild tuple, args[1]=bt tuple
            **kwargs: other args

        Returns:
            correctly setup instance of model
        """

        wild = MassSurvive.setup(*args[0], **kwargs)
        bt   = MassSurvive.setup(*args[1], **kwargs)

        return cls(wild, bt)


class Egg(model.Model):
    """
    Class to describe the survival model for single egg

    Variables:
        _prob: probability of survival

    Methods:
        __call__: call the model

    Constructors:
        setup: setup the mathematical model
    """

    keyword = keywords.egg_survive

    def __init__(self, prob: hints.variable):
        self._prob = prob

    def __call__(self, mass:      float,
                       bt:        str,
                       phenotype: str) -> bool:
        """
        Call the model to determine if the egg survives

        Args:
            mass:      mass of of egg
            bt:        bt state of plant
            phenotype: phenotype of the egg

        Returns:
            if egg survives
        """

        return rnd.random() <= self._prob(phenotype)

    @classmethod
    def setup(cls, *args, **kwargs) -> 'Egg':
        """
        Correctly setup class

        Args:
            *args:    arg[0]=prob
            **kwargs: other arguments
        Returns:
            setup class
        """

        prob = cls.setup_variable(*args[0], **kwargs)

        return cls(prob)


class Pupa(model.Model):
    """
    Class to describe the survival model for pupa

    Variables:
        _prob: probability of survival

    Methods:
        __call__: call the model

    Constructors:
        setup: setup the mathematical model
    """

    keyword = keywords.pupa_survive

    def __init__(self, prob: hints.variable):
        self._prob = prob

    def __call__(self, mass:      float,
                       phenotype: str) -> bool:
        """
        Call the model to determine if the pupa survives

        Args:
            mass:      mass of of pupa
            phenotype: phenotype of pupa

        Returns:
            if pupa survives
        """

        return rnd.random() <= self._prob(phenotype)

    @classmethod
    def setup(cls, *args, **kwargs) -> 'Pupa':
        """
        Correctly setup class

        Args:
            *args:    arg[0]=prob
            **kwargs: other arguments
        Returns:
            setup class
        """

        prob = cls.setup_variable(*args[0], **kwargs)

        return cls(prob)


class Adult(model.Model):
    """
    Class to describe the survival model for adult

    Variables:
        _prob: probability of survival

    Methods:
        __call__: call the model

    Constructors:
        setup: setup the mathematical model
    """

    keyword = keywords.adult_survive

    def __init__(self, prob: hints.variable):
        self._prob = prob

    def __call__(self, mass:      float,
                       phenotype: str) -> bool:
        """
        Call the model to determine if the adult survives

        Args:
            mass:      mass of of adult
            phenotype: phenotype of adult

        Returns:
            if adult survives
        """

        return rnd.random() <= self._prob(phenotype)

    @classmethod
    def setup(cls, *args, **kwargs) -> 'Adult':
        """
        Correctly setup class

        Args:
            *args:    arg[0]=prob
            **kwargs: other arguments
        Returns:
            setup class
        """

        prob = cls.setup_variable(*args[0], **kwargs)

        return cls(prob)
