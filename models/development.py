import source.development.models as models

import models.dominance as dom


def egg_dev(mu_egg_dev:  float,
            sig_egg_dev: float):
    """
    Create an egg development model

    Args:
        mu_egg_dev:  mean development time for eggs
        sig_egg_dev: std in development time for eggs

    Returns:
        a functional mathematical model for the simulation
    """

    return models.Egg(mu_egg_dev,
                      sig_egg_dev)


def pupa_dev(mu_pupa_dev:  float,
             sig_pupa_dev: float):
    """
    Create a pupa development model

    Args:
        mu_pupa_dev:  mean development time for pupae
        sig_pupa_dev: std in development time for pupae

    Returns:
    """

    return models.Pupa(mu_pupa_dev,
                       sig_pupa_dev)


def larva_dev(mu_larva_dev_ss:  float,
              mu_larva_dev_rr:  float,
              sig_larva_dev_ss: float,
              sig_larva_dev_rr: float,
              dominance:        float):
    """
    Create a larva development model

    Args:
        mu_larva_dev_ss:  mean development mass for larvae of genotype ss
        mu_larva_dev_rr:  mean development mass for larvae of genotype rr
        sig_larva_dev_ss: std in development mass for larvae of genotype ss
        sig_larva_dev_rr: std in development mass for larvae of genotype rr
        dominance:        degree of dominance

    Returns:
        a functional mathematical model for the simulation
    """

    mu  = dom.dom(mu_larva_dev_ss,
                  mu_larva_dev_rr,
                  dominance)

    print('SS Mu: {}'.format(mu['susceptible']))
    print('RR Mu: {}'.format(mu['resistant']))

    sig = dom.dom(sig_larva_dev_ss,
                  sig_larva_dev_rr,
                  dominance)

    return models.Larva(mu, sig)
