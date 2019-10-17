import source.development.models as models

import models.dominance as dom


def egg_dev(egg_mu_dev:  float,
            egg_sig_dev: float):
    """
    Create an egg development model

    Args:
        egg_mu_dev:  mean development time for eggs
        egg_sig_dev: std in development time for eggs

    Returns:
        a functional mathematical model for the simulation
    """

    return models.Egg(egg_mu_dev,
                      egg_sig_dev)


def pupa_dev(pupa_mu_dev:  float,
             pupa_sig_dev: float):
    """
    Create a pupa development model

    Args:
        pupa_mu_dev:  mean development time for pupae
        pupa_sig_dev: std in development time for pupae

    Returns:
    """

    return models.Pupa(pupa_mu_dev,
                       pupa_sig_dev)


def larva_dev(larva_mu_dev_ss:  float,
              larva_mu_dev_rr:  float,
              larva_sig_dev_ss: float,
              larva_sig_dev_rr: float,
              dominance:        float):
    """
    Create a larva development model

    Args:
        larva_mu_dev_ss:  mean development mass for larvae of genotype ss
        larva_mu_dev_rr:  mean development mass for larvae of genotype rr
        larva_sig_dev_ss: std in development mass for larvae of genotype ss
        larva_sig_dev_rr: std in development mass for larvae of genotype rr
        dominance:        degree of dominance

    Returns:
        a functional mathematical model for the simulation
    """

    mu  = dom.dom(larva_mu_dev_ss,
                  larva_mu_dev_rr,
                  dominance)
    sig = dom.dom(larva_sig_dev_ss,
                  larva_sig_dev_rr,
                  dominance)

    return models.Larva(mu, sig)
