import dataclasses  as dclass
import numpy.random as rnd

import source.hint    as hint
import source.keyword as keyword


@dclass.dataclass
class Adult(object):
    """
    Class to handle adult movement behavior

    Variables:
        movement: mathematical function for how far adult moves

    Methods:
        move: run the behavior

    Constructors:
        setup: setup class
    """

    movement: hint.movement_adult = None

    behavior: str = keyword.movement_adult

    @property
    def _use_movement(self) -> bool:
        """Determine if we use the move model"""

        return self.movement is not None

    def _distance(self, adult: hint.adult) -> float:
        """
        Get the distance the adult will move

        Args:
            adult: the adult in question

        Returns:
            the distance the adult can move
        """

        return self.movement(adult.mass, adult.genotype)

    def _vertex(self, adult: hint.adult) -> int:
        """
        Get the vertex for adult to move to

        Args:
            adult: the adult in question

        Returns:
            the vertex to move to
        """

        distance = self._distance(adult)
        kwargs = {keyword.upper: distance,
                  keyword.lower: distance}
        vertices = adult.vertices(**kwargs)

        return rnd.choice(list(vertices))

    def move(self, adult: hint.adult) -> None:
        """
        Move the adult

        Args:
            adult: the adult in question

        Effects:
            moves the adult in space
        """

        if self._use_movement:
            vertex = self._vertex(adult)
            adult.transfer(vertex, keyword.adult_level)

    @classmethod
    def setup(cls, **kwargs) -> 'Adult':
        """
        Setup the class

        Args:
            **kwargs: simulation input models

        Returns:
            setup class
        """

        if keyword.adult_movement in kwargs:
            return cls(kwargs[keyword.adult_movement])
        else:
            return cls()
