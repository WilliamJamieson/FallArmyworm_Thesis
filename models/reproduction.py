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
