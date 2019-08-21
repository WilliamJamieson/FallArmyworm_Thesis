import dataclasses as dclass
import scipy.stats as stats

import source.keyword as keyword

import source.simulation.models as models


@dclass.dataclass
class Levy(models.Model):
    """
    Class to contain a model to select a travel distance for Levy flight

    Variables:
        loc:   location of mean
        scale: scale factor
        shape: distribution shape constant

    Methods:
        __call__: call the model

    Constructors:
        setup: setup the model
    """

    loc:   float
    scale: float
    shape: float

    def __call__(self, mass:   float,
                       genotype: str) -> float:
        """
        Call the model to get the distance to travel

        Args:
            mass:     mass of agent
            genotype: genotype of agent

        Returns:
            the distance to travel
        """

        return float(stats.pareto.rvs(self.shape,
                                      loc=self.loc, scale=self.scale))


@dclass.dataclass
class Larva(Levy):
    """
    Class containing distance model for larva movement

    Variables:
        loc:   location of mean
        scale: scale factor
        shape: distribution shape constant

    Methods:
        __call__: call the model
    """

    model_key = keyword.larva_movement


@dclass.dataclass
class Adult(Levy):
    """
    Class containing distance model for adult movement

    Variables:
        loc:   location of mean
        scale: scale factor
        shape: distribution shape constant

    Methods:
        __call__: call the model
    """

    model_key = keyword.adult_movement
