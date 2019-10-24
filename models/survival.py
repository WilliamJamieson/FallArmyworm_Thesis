import source.keyword as keyword

import source.survival.models as models

import models.dominance as dom


def egg_sur(egg_prob: float):
    """
    Create an egg survival model

    Args:
        egg_prob: daily survival probability

    Returns:
        a functional mathematical model for the simulation
    """

    return models.Egg(egg_prob)


def pupa_sur(pupa_prob: float):
    """
    Create a pupa survival model

    Args:
        pupa_prob: daily survival probability

    Returns:
        a functional mathematical model for the simulation
    """

    return models.Pupa(pupa_prob)


def adult_sur(adult_prob: float):
    """
    Create an adult survival model

    Args:
        adult_prob: daily survival probability

    Returns:
        a functional mathematical model for the simulation
    """

    return models.Adult(adult_prob)


def larva_sur(larva_prob_non_bt_rr: float,
              larva_prob_non_bt_ss: float,
              larva_prob_bt_rr:     float,
              larva_prob_bt_ss:     float,
              dominance:            float):
    """
    Create a larva survival model

    Args:
        larva_prob_non_bt_rr: non-Bt RR prob
        larva_prob_non_bt_ss: non-Bt SS prob
        larva_prob_bt_rr:     Bt     RR prob
        larva_prob_bt_ss:     Bt     SS prob
        dominance:            degree of dominance

    Returns:
        a functional mathematical model for the simulation
    """

    prob_non_bt = dom.dom(larva_prob_non_bt_ss,
                          larva_prob_non_bt_rr,
                          dominance)
    prob_bt     = dom.dom(larva_prob_bt_ss,
                          larva_prob_bt_rr,
                          dominance)

    prob = {
        keyword.bt:     prob_bt,
        keyword.not_bt: prob_non_bt
    }

    return models.LarvaFixed(prob)
