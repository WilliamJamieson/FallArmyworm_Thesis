import source.biomass.models as models

import models.dominance as dom


def init_num(lam_0_egg: float):
    """
    Create an init_num model for egg_mass

    Args:
        lam_0_egg: the mean number of eggs in egg_mass

    Returns:
        a functional mathematical model for the simulation
    """

    return models.InitNum(lam_0_egg)


def init_mass(mu_0_egg_ss:  float,
              mu_0_egg_rr:  float,
              sig_0_egg_ss: float,
              sig_0_egg_rr: float,
              dominance:    float):
    """
    Create an init_mass model for egg_mass

    Args:
        mu_0_egg_ss:  the mean mass of egg_mass for ss genotype
        mu_0_egg_rr:  the mean mass of egg_mass for rr genotype
        sig_0_egg_ss: the std in mass of egg_mass for ss genotype
        sig_0_egg_rr: the std in mass of egg_mass for rr genotype
        dominance:    the degree of dominance

    Returns:
        a functional mathematical model for the simulation
    """

    mu_0_egg  = dom.dom(mu_0_egg_ss,
                        mu_0_egg_rr,
                        dominance)
    sig_0_egg = dom.dom(sig_0_egg_ss,
                        sig_0_egg_rr,
                        dominance)

    return models.InitMass(mu_0_egg,
                           sig_0_egg)


def init_juvenile(mu_0_larva_ss:  float,
                  mu_0_larva_rr:  float,
                  sig_0_larva_ss: float,
                  sig_0_larva_rr: float,
                  dominance:      float):
    """
    Create an init_mass model for larva

    Args:
        mu_0_larva_ss:  the mean mass of larva for ss genotype
        mu_0_larva_rr:  the mean mass of larva for rr genotype
        sig_0_larva_ss: the std in mass of larva for ss genotype
        sig_0_larva_rr: the std in mass of larva for rr genotype
        dominance:      the degree of dominance

    Returns:
        a functional mathematical model for the simulation
    """

    mu_0_larva  = dom.dom(mu_0_larva_ss,
                          mu_0_larva_rr,
                          dominance)
    sig_0_larva = dom.dom(sig_0_larva_ss,
                          sig_0_larva_rr,
                          dominance)

    return models.InitJuvenile(mu_0_larva,
                               sig_0_larva)


def init_mature(mu_0_mature_ss:  float,
                mu_0_mature_rr:  float,
                sig_0_mature_ss: float,
                sig_0_mature_rr: float,
                dominance:       float):
    """
    Create an init_mass model for mature agents

    Args:
        mu_0_mature_ss:  the mean mass of mature for ss genotype
        mu_0_mature_rr:  the mean mass of mature for rr genotype
        sig_0_mature_ss: the std in mass of mature for ss genotype
        sig_0_mature_rr: the std in mass of mature for rr genotype
        dominance:       the degree of dominance

    Returns:
        a functional mathematical model for the simulation
    """

    mu_0_mature  = dom.dom(mu_0_mature_ss,
                           mu_0_mature_rr,
                           dominance)
    sig_0_mature = dom.dom(sig_0_mature_ss,
                           sig_0_mature_rr,
                           dominance)

    return models.InitMature(mu_0_mature,
                             sig_0_mature)


def init_plant(mu_leaf:  float,
               sig_leaf: float):
    """
    Create an init_plant model for plant biomass
    Args:
        mu_leaf:  the mean mass of a leaf
        sig_leaf: the std in mass of a leaf

    Returns:
        a functional mathematical model for the simulation
    """

    return models.InitPlant(mu_leaf,
                            sig_leaf)
