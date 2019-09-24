import source.keyword as keyword

import source.development.models as models


# Generate the input models
#       egg_development
def egg(mu, sigma, minimum):
    """
    Create the egg development model

    Args:
        mu:      mean
        sigma:   standard deviation
        minimum: min development time

    Returns:
        mathematical model
    """

    return models.Egg(mu, sigma, minimum)


#       pupa_development
def pupa(mu, sigma, minimum):
    """
    Create the pupa development model

    Args:
        mu:      mean
        sigma:   standard deviation
        minimum: min development time

    Returns:
        mathematical model
    """

    return models.Pupa(mu, sigma, minimum)


#       larva_development
def larva(mu, sigma, minimum):
    """
    Create the larva development model

    Args:
        mu:      mean
        sigma:   standard deviation
        minimum: min development time

    Returns:
        mathematical model
    """

    return models.Larva(mu, sigma, minimum)
