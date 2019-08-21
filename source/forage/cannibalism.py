import dataclasses  as dclass
import numpy.random as rnd

import source.hint    as hint
import source.keyword as keyword


@dclass.dataclass
class Cannibalism(object):
    """
    Class to handle cannibalism behavior:

    Variables:
        fight:     mathematical function for determining fight winner
        encounter: mathematical function for determining if cannibalism occurs
        radius:    mathematical function for determining how far encounters
                                                                        reach

    Methods:
        cannibalism: run the behavior

    Constructors:
        setup: setup class
    """

    fight:     hint.fight     = None
    encounter: hint.encounter = None
    radius:    hint.radius    = None

    @property
    def _use_fight(self) -> bool:
        """Determine if we use the fight model"""

        return self.fight is not None

    def _winner(self, larva:  hint.larva,
                      target: hint.larva) -> bool:
        """
        Determine if this larva is winner of fight with target

        Args:
            larva: the larva starting fight
            target: the larva's target

        Returns:
            if the larva running system is winner
        """

        return self.fight(larva.mass, target.mass)

    def _fight(self, larva:  hint.larva,
                     target: hint.larva) -> None:
        """
        Run one fight

        Args:
            larva: the larva starting fight
            target: the larva's target

        Effects:
            runs full fight
        """

        if self._winner(larva, target):
            larva.consume_larva(target)
        else:
            target.consume_larva(larva)

    def _contest(self, larva:  hint.larva,
                       target: hint.larva) -> None:
        """
        Run fight/consume when possible on target larva

        Args:
            larva: the larva starting fight
            target: the larva's target

        Effects:
            consumes part of the larva
        """

        if self._use_fight:
            self._fight(larva, target)

    @property
    def _use_radius(self) -> bool:
        """Determine if we use the radius model"""

        return self.radius is not None

    def _bounds(self, larva: hint.larva) -> dict:
        """
        Get the bounds on the radius for finding encounters

        Args:
            larva: the larva in question

        Returns:
            dict:
                {upper: radius
                 lower: 0}
        """

        if self._use_radius:
            radius = self.radius(larva.mass, larva.genotype)
        else:
            radius = 0

        return {keyword.upper: radius,
                keyword.lower: 0}

    def _targets(self, larva: hint.larva) -> hint.targets:
        """
        Get a list of targets for cannibalism

        Args:
            larva: the larva in question

        Returns:
            list of targets
        """

        return larva.targets(**self._bounds(larva))

    @staticmethod
    def _get_target(targets: hint.targets) -> hint.target:
        """
        Get insect to encounter

        Args:
            targets: get list of potential targets

        Returns:
            target to encounter

        Effects:
            remove target from list
        """

        target = rnd.choice(targets)
        targets.remove(target)

        return target

    def _can_encounter(self, larva: hint.larva) -> bool:
        """
        Determine if larva can encounter

        Args:
            larva: the larva in question

        Returns:
            if larva can perform an encounter
        """

        return (self.encounter is not None) and larva.alive and (not larva.full)

    def _encounter(self, larva: hint.larva,
                         targets: hint.targets) -> bool:
        """
        Determine if an encounter occurs

        Args:
            larva:   the larva in question
            targets: get list of potential targets

        Returns:
            if an encounter occurs
        """

        if self._can_encounter(larva):
            return self.encounter(len(targets), larva.mass, larva.genotype)
        else:
            return False

    def _cannibalize(self, larva:   hint.larva,
                           targets: hint.targets) -> None:
        """
        Perform cannibalism on target

        Args:
            larva:   the larva in question
            targets: get list of potential targets

        Effects:
            run cannibalism on target
        """

        target = self._get_target(targets)

        if target.agent_key == keyword.egg_mass:
            larva.consume_egg(target)
        else:
            self._contest(larva, target)

    def _cannibalism(self, larva:    hint.larva,
                           targets: hint.targets) -> bool:
        """
        Run single cannibalism step:

        Args:
            larva:   the larva in question
            targets: get list of potential targets

        Returns:
            if their was an encounter
        """

        if self._encounter(larva, targets):
            self._cannibalize(larva, targets)

            return True
        else:
            return False

    def _run_cannibalism(self, larva: hint.larva) -> None:
        """
        Run cannibalism system

        Args:
            larva: the larva in question

        Effects:
            Run all the cannibalism a larva
        """

        targets = self._targets(larva)

        cannibalism = True
        while cannibalism:
            cannibalism = self._cannibalism(larva, targets)

    def cannibalism(self, larva: hint.larva) -> None:
        """
        Run full cannibalism encounter

        Args:
            larva: the larva in question

        Effects:
            Runs single cannibalism instance
        """

        if self._can_encounter(larva):
            self._run_cannibalism(larva)

    @classmethod
    def setup(cls, **kwargs) -> 'Cannibalism':
        """
        Setup the class

        Args:
            **kwargs: simulation input models

        Returns:
            setup class
        """

        if keyword.fight in kwargs:
            fight = kwargs[keyword.fight]
        else:
            fight = None

        if keyword.encounter in kwargs:
            encounter = kwargs[keyword.encounter]
        else:
            encounter = None

        if keyword.radius in kwargs:
            radius = kwargs[keyword.radius]
        else:
            radius = None

        return cls(fight, encounter, radius)
