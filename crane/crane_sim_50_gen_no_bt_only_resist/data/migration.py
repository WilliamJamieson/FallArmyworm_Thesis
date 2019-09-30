import source.keyword as keyword


# Get the setup tuples
#       emigration_adult
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


#       emigration_larva
def emigration_larva(mean, sigma):
    """
    Create an emigration for larvae
    Args:
        mean:  mean number of larvae
        sigma: standard deviation

    Returns:
        larva immigration
    """

    emigration = (mean, sigma, [keyword.larva])

    return emigration


#       emigration_pupa
def emigration_pupa(mean, sigma):
    """
    Create an emigration for pupae
    Args:
        mean:  mean number of pupae
        sigma: standard deviation

    Returns:
        pupa immigration
    """

    emigration = (mean, sigma, [keyword.pupa])

    return emigration


#       emigration_egg
def emigration_egg(mean, sigma):
    """
    Create an emigration for egg_mass
    Args:
        mean:  mean number of egg_mass
        sigma: standard deviation

    Returns:
        egg immigration
    """

    emigration = (mean, sigma, [keyword.egg_mass])

    return emigration


#       immigration_pregnant
def immigration_pregnant_homo_r(lam):
    """
    immigration of pregnant homo_r producing adults
    Args:
        lam: mean number of immigrants

    Returns:
        immigration tuple
    """

    immigration = (lam, keyword.homo_r, keyword.pregnant)

    return immigration


def immigration_pregnant_hetero(lam):
    """
    immigration of pregnant hetero producing adults
    Args:
        lam: mean number of immigrants

    Returns:
        immigration tuple
    """

    immigration = (lam, keyword.hetero, keyword.pregnant)

    return immigration


def immigration_pregnant_homo_s(lam):
    """
    immigration of pregnant homo_s producing adults
    Args:
        lam: mean number of immigrants

    Returns:
        immigration tuple
    """

    immigration = (lam, keyword.homo_s, keyword.pregnant)

    return immigration


#       immigration_adult
def immigration_adult_homo_r(lam):
    """
    immigration of adult homo_r producing adults
    Args:
        lam: mean number of immigrants

    Returns:
        immigration tuple
    """

    immigration = (lam, keyword.homo_r, keyword.adult)

    return immigration


def immigration_adult_hetero(lam):
    """
    immigration of adult hetero producing adults
    Args:
        lam: mean number of immigrants

    Returns:
        immigration tuple
    """

    immigration = (lam, keyword.hetero, keyword.adult)

    return immigration


def immigration_adult_homo_s(lam):
    """
    immigration of adult homo_s producing adults
    Args:
        lam: mean number of immigrants

    Returns:
        immigration tuple
    """

    immigration = (lam, keyword.homo_s, keyword.adult)

    return immigration


#       immigration_larva
def immigration_larva_homo_r(lam):
    """
    immigration of larva homo_r producing larvae
    Args:
        lam: mean number of immigrants

    Returns:
        immigration tuple
    """

    immigration = (lam, keyword.homo_r, keyword.larva)

    return immigration


def immigration_larva_hetero(lam):
    """
    immigration of larva hetero producing larvae
    Args:
        lam: mean number of immigrants

    Returns:
        immigration tuple
    """

    immigration = (lam, keyword.hetero, keyword.larva)

    return immigration


def immigration_larva_homo_s(lam):
    """
    immigration of larva homo_s producing larvae
    Args:
        lam: mean number of immigrants

    Returns:
        immigration tuple
    """

    immigration = (lam, keyword.homo_s, keyword.larva)

    return immigration


#       immigration_pupa
def immigration_pupa_homo_r(lam):
    """
    immigration of pupa homo_r producing pupae
    Args:
        lam: mean number of immigrants

    Returns:
        immigration tuple
    """

    immigration = (lam, keyword.homo_r, keyword.pupa)

    return immigration


def immigration_pupa_hetero(lam):
    """
    immigration of pupa hetero producing pupae
    Args:
        lam: mean number of immigrants

    Returns:
        immigration tuple
    """

    immigration = (lam, keyword.hetero, keyword.pupa)

    return immigration


def immigration_pupa_homo_s(lam):
    """
    immigration of pupa homo_s producing pupae
    Args:
        lam: mean number of immigrants

    Returns:
        immigration tuple
    """

    immigration = (lam, keyword.homo_s, keyword.pupa)

    return immigration


#       immigration_egg
def immigration_egg_homo_r(lam):
    """
    immigration of egg homo_r producing egg_mass
    Args:
        lam: mean number of immigrants

    Returns:
        immigration tuple
    """

    immigration = (lam, keyword.homo_r, keyword.egg_mass)

    return immigration


def immigration_egg_hetero(lam):
    """
    immigration of egg hetero producing egg_mass
    Args:
        lam: mean number of immigrants

    Returns:
        immigration tuple
    """

    immigration = (lam, keyword.hetero, keyword.egg_mass)

    return immigration


def immigration_egg_homo_s(lam):
    """
    immigration of egg homo_s producing egg_mass
    Args:
        lam: mean number of immigrants

    Returns:
        immigration tuple
    """

    immigration = (lam, keyword.homo_s, keyword.egg_mass)

    return immigration
