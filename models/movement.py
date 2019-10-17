import source.movement.models as models


def larva(scale: float,
          shape: float):
    """
    Create a larva movement model

    Args:
        scale: scale parameter
        shape: shape parameter

    Returns:
        a functional mathematical model for the simulation
    """

    return models.Larva(scale, shape)


def adult(scale: float,
          shape: float):
    """
    Create a adult movement model

    Args:
        scale: scale parameter
        shape: shape parameter

    Returns:
        a functional mathematical model for the simulation
    """

    return models.Adult(scale, shape)
