import source.keyword as keyword


def emigration_adult(mean, sigma):
    """
    Create an emigration for adults
    Args:
        mean:  mean number of adults
        sigma: standard deviation

    Returns:
        adult immigration
    """

    emigration = (mean, sigma, [keyword.female, keyword.male, keyword.mated])

    return emigration
