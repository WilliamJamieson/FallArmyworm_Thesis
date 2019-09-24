import source.forage.models as models


# Generate the input models
#       plant_ad_libitum
def ad_libitum(max_gut):
    """
    Create an ad libitum model
    Args:
        max_gut: max gut model

    Returns:
        forage model
    """

    return models.PlantAdLibitum(max_gut)


#       plant_starve
def starve(mu, sigma, max_gut):
    """
    Create a starvation model
    Args:
        mu:      mean in starvation factor
        sigma:   standard deviation in factor
        max_gut: max gut model

    Returns:
        forage model
    """

    return models.PlantStarve(mu, sigma, max_gut)


#       egg_forage
def egg(factor):
    """
    Create a egg forage model

    Args:
        factor: weight factor

    Returns:
        an egg forage model
    """

    return models.Egg(factor)


#       larva_forage
def larva(factor):
    """
    Create a larva forage model

    Args:
        factor: weight factor

    Returns:
        an larva forage model
    """

    return models.Larva(factor)


#       loss
def loss(slope, mid, max_gut, egg_forage, larva_forage):
    """
    Calculate the loss of target model
    Args:
        slope:        loss slope
        mid:          midpoint prob
        max_gut:      max_gut model
        egg_forage:   egg forage
        larva_forage: larva forage

    Returns:
        a target loss model
    """

    return models.Loss(slope, mid, max_gut, egg_forage, larva_forage)


#       fight
def fight(slope):
    """
    Create a fight model
    Args:
        slope: slope of transition

    Returns:
        fight model
    """

    return models.Fight(slope)


#       encounter
def encounter(factor):
    """
    Create an encounter model
    Args:
        factor: encounter control factor

    Returns:
        encounter model
    """

    return models.Encounter(factor)


#       radius
def radius(rad):
    """
    Create an encounter radius model
    Args:
        rad: max radius

    Returns:
        radius model
    """

    return models.Radius(rad)
