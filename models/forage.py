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
