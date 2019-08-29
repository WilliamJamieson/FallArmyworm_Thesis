import dataclasses as dclass

import source.hint    as hint
import source.keyword as keyword


@dclass.dataclass
class Target(object):
    """
    Class to handle target consumption

    Variables:
        loss: mathematical function for if we lose/keep the target

    Methods:
        consume: run the behavior

    Constructors:
        setup: setup class
    """

    loss: hint.loss = None

    @property
    def _use_loss(self) -> bool:
        """Determine if we use the loss model"""

        return self.loss is not None

    def _keep_target(self, larva:  hint.larva,
                           target: hint.target) -> bool:
        """
        Determine if we loose the target

        Args:
            larva:  the larva in question
            target: the larva's target

        Returns:
            if the larva moves away from the target
        """

        if self._use_loss:
            return self.loss(larva.mass, target.mass,
                             larva.genotype, target.agent_key)
        else:
            return False

    @staticmethod
    def _consume_target(larva:  hint.larva,
                        target: hint.target) -> None:
        """
        Consume the target

        Args:
            larva:  the larva in question
            target: the larva's target

        Effects:
            run consume behavior on target
        """

        if target.agent_key == keyword.egg_mass:
            larva.consume_egg(target)
        else:
            larva.consume_larva(target)

    def consume(self, larva: hint.larva) -> None:
        """
        Run a target consume behavior on the larva's target

        Args:
            larva: the larva in question

        Effects:
            run target consumption
        """

        target = larva.target

        if self._keep_target(larva, target):
            self._consume_target(larva, target)
        else:
            larva.target = None

    @classmethod
    def setup(cls, **kwargs) -> 'Target':
        """
        Setup the class

        Args:
            **kwargs: simulation input models

        Returns:
            setup class
        """

        if keyword.loss in kwargs:
            return cls(kwargs[keyword.loss])
        else:
            return cls()
