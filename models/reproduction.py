import source.reproduction.models as models


def init_sex(female_prob: float):
    """
    Create an initial sex model

    Args:
        female_prob: probability of being female

    Returns:
        a functional mathematical model for the simulation
    """

    return models.InitSex(female_prob)


def mating(mate_encounter: float):
    """
    Create a mate encounter model

    Args:
        mate_encounter: encounter constant for mating

    Returns:
        a functional mathematical model for the simulation
    """

    return models.Mating(mate_encounter)


def radius(mate_radius: float):
    """
    Create a mate radius model

    Args:
        mate_radius: radius of mating

    Returns:
        a functional mathematical model for the simulation
    """

    return models.Radius(mate_radius)


def fecundity(fecundity_maximum: float,
              fecundity_decay:   float):
    """
    Create a fecundity model

    Args:
        fecundity_maximum: maximum fecundity
        fecundity_decay:   decay rate of fecundity

    Returns:
        a functional mathematical model for the simulation
    """

    return models.Fecundity(fecundity_maximum,
                            fecundity_decay)


def density(eta:   float,
            gamma: float):
    """
    Create a density model

    Args:
        eta:   constant of proportionality
        gamma: shape

    Returns:
        a functional mathematical model for the simulation
    """

    return models.Density(eta,
                          gamma)
