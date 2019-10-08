import source.survival.models as models


class DailyProb(object):
    """
    Class to calculate the daily survival probabilities:
        Daily = P^(time - 1)

    Variables:
        _time: number of days for the lifetime
        _prob: the total survival probability

    Methods:
        daily: calculate the daily probability
    """

    def __init__(self, time: int,
                 prob: float):
        self._time = time
        self._prob = prob

    def daily(self) -> float:
        """
        Calculate the daily probability from the equation above

        Returns:
            the daily prob
        """

        exp = 1 / (self._time - 1)

        return self._prob**exp


def daily(time: int,
          prob: float) -> float:
    """
    Calculate the daily probability

    Args:
        time: daily survival lifetime
        prob: average lifetime probability

    Returns:
        the daily lifetime probability
    """

    return DailyProb(time, prob).daily()


# Generate the input models
#       egg_survival
def egg(lifetime, prob):
    """
    Create an egg survival model

    Args:
        lifetime: average lifetime
        prob:     average survival over lifetime

    Returns:
        survival model
    """

    survival_prob = daily(lifetime, prob)

    return models.Egg(survival_prob)


#       pupa_survival
def pupa(lifetime, prob):
    """
    Create an pupa survival model

    Args:
        lifetime: average lifetime
        prob:     average survival over lifetime

    Returns:
        survival model
    """

    survival_prob = daily(lifetime, prob)

    return models.Pupa(survival_prob)


#       adult_survival
def adult(lifetime, prob):
    """
    Create an adult survival model

    Args:
        lifetime: average lifetime
        prob:     average survival over lifetime

    Returns:
        survival model
    """

    survival_prob = daily(lifetime, prob)

    return models.Adult(survival_prob)


#       larva_survival
def larva(minimum, maximum, inflection, steepness):
    """
    Create a larval survival model
    Args:
        minimum:    minimum probability
        maximum:    maximum probability
        inflection: inflection point of transition
        steepness:  steepness of transition

    Returns:

    """

    return models.Larva(minimum, maximum, inflection, steepness)
