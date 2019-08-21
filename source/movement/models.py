# TODO: UPDATE THESE FOR NEW SYSTEMS

import scipy.stats as stats

import source.hints    as hints
import source.keywords as keywords

import source.models.model as model


class Levy(model.Model):
    """
    Class to contain a model to select a travel distance for Levy flight

    Variables:
        _loc:   location of mean
        _scale: scale factor
        _shape: distribution shape constant

    Methods:
        __call__: call the model

    Constructors:
        setup: setup the model
    """

    def __init__(self, loc:   hints.variable,
                       scale: hints.variable,
                       shape: hints.variable):
        self._loc   = loc
        self._scale = scale
        self._shape = shape

    def __call__(self, mass:      float,
                       phenotype: str) -> float:
        """
        Call the model to get the distance to travel

        Args:
            mass:      mass of larva
            phenotype: phenotype of larva

        Returns:
            the distance to travel
        """

        loc   = self._loc(  phenotype)
        scale = self._scale(phenotype)
        shape = self._shape(phenotype)

        return stats.pareto.rvs(shape, loc=loc, scale=scale)

    @classmethod
    def setup(cls, *args, **kwargs) -> 'Levy':
        """
        Correctly setup class

        Args:
            *args:    arg[0]=loc
                      arg[1]=scale
                      arg[2]=shape
            **kwargs: other arguments
        Returns:
            setup class
        """

        loc   = cls.setup_variable(*args[0], **kwargs)
        scale = cls.setup_variable(*args[1], **kwargs)
        shape = cls.setup_variable(*args[2], **kwargs)

        return cls(loc, scale, shape)


class Larva(Levy):
    """
    Class containing distance model for larva movement

    Variables:
        _loc:   location of mean
        _scale: scale factor
        _shape: distribution shape constant

    Methods:
        __call__: call the model

    Constructors:
        setup: setup the model
    """

    keyword = keywords.larva_move


class Adult(Levy):
    """
    Class containing distance model for adult movement

    Variables:
        _loc:   location of mean
        _scale: scale factor
        _shape: distribution shape constant

    Methods:
        __call__: call the model

    Constructors:
        setup: setup the model
    """

    keyword = keywords.adult_move
