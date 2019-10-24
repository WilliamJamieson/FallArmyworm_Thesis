import source.survival.models as models


def egg_sur(egg_prob: float):
    """
    Create an egg survival model

    Args:
        egg_prob: daily survival probability

    Returns:
        a functional mathematical model for the simulation
    """

    return models.Egg(egg_prob)


def pupa_sur(pupa_prob: float):
    """
    Create a pupa survival model

    Args:
        pupa_prob: daily survival probability

    Returns:
        a functional mathematical model for the simulation
    """

    return models.Pupa(pupa_prob)


def adult_sur(adult_prob: float):
    """
    Create an adult survival model

    Args:
        adult_prob: daily survival probability

    Returns:
        a functional mathematical model for the simulation
    """

    return models.Adult(adult_prob)
