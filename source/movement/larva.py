import dataclasses  as dclass
import numpy.random as rnd

import source.hint    as hint
import source.keyword as keyword


@dclass.dataclass
class Larva(object):
    """
    Class to handle larva movement behavior

    Variables:
        movement: mathematical function for how far larva moves

    Methods:
        move: run the behavior

    Constructors:
        setup: setup class
    """

    movement: hint.movement_larva = None

    behavior: str = keyword.movement_larva

    @property
    def _use_movement(self) -> bool:
        """Determine if we use the move model"""

        return self.movement is not None

    def _distance(self, larva: hint.larva) -> float:
        """
        Get the distance the larva will move

        Args:
            larva: the larva in question

        Returns:
            the distance the larva can move
        """

        return self.movement(larva.mass, larva.genotype)

    def _vertex(self, larva: hint.larva) -> int:
        """
        Get the vertex for larva to move to

        Args:
            larva: the larva in question

        Returns:
            the vertex to move to
        """

        distance = self._distance(larva)
        kwargs = {keyword.upper: distance,
                  keyword.lower: distance}
        vertices = larva.vertices(**kwargs)

        return rnd.choice(list(vertices))

    def move(self, larva: hint.larva) -> None:
        """
        Move the larva

        Args:
            larva: the larva in question

        Effects:
            moves the larva in space
        """

        if self._use_movement:
            vertex = self._vertex(larva)
            larva.transfer(vertex, keyword.larva_level)

    @classmethod
    def setup(cls, **kwargs) -> 'Larva':
        """
        Setup the class

        Args:
            **kwargs: simulation input models

        Returns:
            setup class
        """

        if keyword.larva_movement in kwargs:
            return cls(kwargs[keyword.larva_movement])
        else:
            return cls()
