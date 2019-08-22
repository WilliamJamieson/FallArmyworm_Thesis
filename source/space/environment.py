import dataclasses as dclass

import source.hint as hint


@dclass.dataclass
class Environment(object):
    """
    Class to handle local environmental conditions:

    Variables:
        bt:    bt state of local environment
        plant: mass available to each individual to consume

    Constructors:
        read the data
    """

    bt:    str   = None
    plant: float = None

    @classmethod
    def setup(cls, bt:         str,
                   init_plant: hint.init_plant) -> 'Environment':
        """
        Setup the environment

        Args:
            bt:         bt state of the local environment
            init_plant: plant mass model

        Returns:
            setup environment
        """

        plant = init_plant(bt)

        return cls(bt, plant)
