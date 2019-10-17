import source.hint as hint

import source.biomass.models as bio
import source.forage.models  as models


def adlibitum(forage_steps: int):
    """
    Create a true adlibitum plant consume model

    Args:
        forage_steps: the number of steps that forage takes place over

    Returns:
        a functional mathematical model for the simulation
    """

    max_gut = bio.MaxGut()

    return models.PlantAdLibitum(forage_steps,
                                 max_gut)


def starvation(forage_steps: int,
               theta:        float,
               sig_starve:   float):
    """
    Create a starvation plat consume model

    Args:
        forage_steps: the number of steps that forage takes place over
        theta:        starvation factor
        sig_starve:   std in food amounts

    Returns:
        a functional mathematical model for the simulation
    """

    max_gut = bio.MaxGut()

    return models.PlantStarve(forage_steps,
                              theta,
                              sig_starve,
                              max_gut)


def egg(egg_factor: float):
    """
    Create an egg consume model

    Args:
        egg_factor: the factor for how much of egg can be eaten

    Returns:
        a functional mathematical model for the simulation
    """

    return models.Egg(egg_factor)


def larva(larva_factor: float):
    """
    Create an larva consume model

    Args:
        larva_factor: the factor for how much of larva can be eaten

    Returns:
        a functional mathematical model for the simulation
    """

    return models.Larva(larva_factor)


def fight(fight_slope: float):
    """
    Create a larva fight model

    Args:
        fight_slope: slope of transition

    Returns:
        a functional mathematical model for the simulation
    """

    return models.Fight(fight_slope)


def radius(cannibalism_radius: float):
    """
    Create a mathematical model for radius

    Args:
        cannibalism_radius: the radius for cannibalism

    Returns:
        a functional mathematical model for the simulation
    """

    return models.Radius(cannibalism_radius)


def encounter(cannibalism_encounter: float):
    """
    Create a mathematical model for encounters

    Args:
        cannibalism_encounter: the encounter rate constant

    Returns:
        a functional mathematical model for the simulation
    """

    return models.Encounter(cannibalism_encounter)


def loss(loss_slope:   float,
         mid:          hint.variable,
         egg_factor:   float,
         larva_factor: float):
    """
    Create a mathematical model for loss

    Args:
        loss_slope:   slope of transition
        mid:          equality probability factors
        egg_factor:   the factor for how much of egg can be eaten
        larva_factor: the factor for how much of larva can be eaten

    Returns:
        a functional mathematical model for the simulation
    """

    max_gut      = bio.MaxGut()
    forage_egg   = egg(  egg_factor)
    forage_larva = larva(larva_factor)

    return models.Loss(loss_slope,
                       mid,
                       max_gut,
                       forage_egg,
                       forage_larva)
