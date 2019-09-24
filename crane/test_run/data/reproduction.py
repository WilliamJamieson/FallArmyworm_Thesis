import source.reproduction.models as models


# Generate the input models
#       init_sex
def init_sex(prob):
    """
    Create an initial sex model
    Args:
        prob: probability of female

    Returns:
        an initial sex model
    """

    return models.InitSex(prob)


#       mating
def mating(factor):
    """
    Create a mating model
    Args:
        factor: encounter factor

    Returns:
        a mating model
    """

    return models.Mating(factor)


#       mate_radius
def radius(rad):
    """
    Create a mate radius model

    Args:
        rad: maximum radius

    Returns:
        a mate radius model
    """

    return models.Radius(rad)


#       fecundity
def fecundity(maximum, decay):
    """
    Create a fecundity model
    Args:
        maximum: maximum fecundity
        decay:   decay rate constant

    Returns:
        fecundity model
    """

    return models.Fecundity(maximum, decay)


#       density
def density(eta, gamma):
    """
    Create a density model
    Args:
        eta:   constant
        gamma: power

    Returns:
        density model
    """

    return models.Density(eta, gamma)
