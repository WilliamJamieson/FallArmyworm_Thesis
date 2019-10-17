import source.biomass.models as models

import models.dominance as dom


def max_gut():
    """
    Create the max_gut model

    Returns:
        a functional mathematical model for the simulation
    """

    return models.MaxGut()


def growth(alpha_ss:  float,
           alpha_rr:  float,
           beta_ss:   float,
           beta_rr:   float,
           dominance: float):
    """
    Create a growth model for larvae

    Args:
        alpha_ss:  growth rate for ss genotype
        alpha_rr:  growth rate for rr genotype
        beta_ss:   maintenance cost for ss genotype
        beta_rr:   maintenance cost for rr genotype
        dominance: degree of dominance

    Returns:
        a functional mathematical model for the simulation
    """

    alpha = dom.dom(alpha_ss,
                    alpha_rr,
                    dominance)
    beta  = dom.dom(beta_ss,
                    beta_rr,
                    dominance)

    return models.Growth(alpha, beta)
