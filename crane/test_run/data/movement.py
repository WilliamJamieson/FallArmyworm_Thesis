import source.movement.models as models


# Generate the input models
#       larva_movement
def larva(loc, scale, shape):
    """
    Create a larva movement model

    Args:
        loc:   location of mean
        scale: scale of distribution
        shape: shape of distribution

    Returns:
        larva movement model
    """

    return models.Larva(loc, scale, shape)


#      adult_movement
def adult(loc, scale, shape):
    """
    Create a adult movement model

    Args:
        loc:   location of mean
        scale: scale of distribution
        shape: shape of distribution

    Returns:
        adult movement model
    """

    return models.Adult(loc, scale, shape)
