import data.input_data as input_data

import source.keyword as keyword

import source.survival.models as models


class DailyProb(object):
    """
    Class to calculate the daily survival probabilities:
        Daily = P^(time - 1)

    Variables:
        _time: number of days for the lifetime
        _prob: the total survival probability

    Methods:
        daily: calculate the daily probability
    """

    def __init__(self, time: int,
                 prob: float):
        self._time = time
        self._prob = prob

    def daily(self) -> float:
        """
        Calculate the daily probability from the equation above

        Returns:
            the daily prob
        """

        exp = 1 / (self._time - 1)

        return self._prob**exp


def daily(time: int,
          prob: float) -> float:
    """
    Calculate the daily probability

    Args:
        time: daily survival lifetime
        prob: average lifetime probability

    Returns:
        the daily lifetime probability
    """

    return DailyProb(time, prob).daily()


# Find the fit data
egg_survival_prob   = daily(input_data.egg_lifetime,
                            input_data.egg_survive_prob)
pupa_survival_prob  = daily(input_data.pupa_lifetime,
                            input_data.pupa_survive_prob)
adult_survival_prob = daily(input_data.adult_lifetime,
                            input_data.adult_survive_prob)


# Generate the input models
#       egg_survival
egg_survival = models.Egg(egg_survival_prob)
#       pupa_survival
pupa_survival = models.Pupa(pupa_survival_prob)
#       adult_survival
adult_survival = models.Adult(adult_survival_prob)
#       larva_survival
larva_minimum_not_bt_homo_s = input_data.larva_wild_lower_s
larva_minimum_not_bt_homo_r = input_data.larva_wild_lower_r
larva_minimum_not_bt_hetero = input_data.hetero(larva_minimum_not_bt_homo_s,
                                                larva_minimum_not_bt_homo_r)
larva_minimum_not_bt        = {keyword.homo_s:  larva_minimum_not_bt_homo_s,
                               keyword.homo_r:  larva_minimum_not_bt_homo_r,
                               keyword.hetero:  larva_minimum_not_bt_hetero}
larva_minimum_bt_homo_s     = input_data.larva_bt_lower_s
larva_minimum_bt_homo_r     = input_data.larva_bt_lower_r
larva_minimum_bt_hetero     = input_data.hetero(larva_minimum_bt_homo_s,
                                                larva_minimum_bt_homo_r)
larva_minimum_bt            = {keyword.homo_s:  larva_minimum_bt_homo_s,
                               keyword.homo_r:  larva_minimum_bt_homo_r,
                               keyword.hetero:  larva_minimum_bt_hetero}
larva_minimum               = {keyword.not_bt:  larva_minimum_not_bt,
                               keyword.bt:      larva_minimum_bt}
larva_maximum_not_bt_homo_s = input_data.larva_wild_upper_s
larva_maximum_not_bt_homo_r = input_data.larva_wild_upper_r
larva_maximum_not_bt_hetero = input_data.hetero(larva_maximum_not_bt_homo_s,
                                                larva_maximum_not_bt_homo_r)
larva_maximum_not_bt        = {keyword.homo_s:  larva_maximum_not_bt_homo_s,
                               keyword.homo_r:  larva_maximum_not_bt_homo_r,
                               keyword.hetero:  larva_maximum_not_bt_hetero}
larva_maximum_bt_homo_s     = input_data.larva_bt_upper_s
larva_maximum_bt_homo_r     = input_data.larva_bt_upper_r
larva_maximum_bt_hetero     = input_data.hetero(larva_maximum_bt_homo_s,
                                                larva_maximum_bt_homo_r)
larva_maximum_bt            = {keyword.homo_s:  larva_maximum_bt_homo_s,
                               keyword.homo_r:  larva_maximum_bt_homo_r,
                               keyword.hetero:  larva_maximum_bt_hetero}
larva_maximum               = {keyword.not_bt:  larva_maximum_not_bt,
                               keyword.bt:      larva_maximum_bt}
larva_inflection_homo_s     = input_data.time_final_s/2
larva_inflection_homo_r     = input_data.time_final_r/2
larva_inflection_hetero     = input_data.hetero(larva_inflection_homo_s,
                                                larva_inflection_homo_r)
larva_inflection            = {keyword.homo_s:  larva_inflection_homo_s,
                               keyword.homo_r:  larva_inflection_homo_r,
                               keyword.hetero:  larva_inflection_hetero}
larva_steepness_homo_s      = input_data.larva_sur_steep_s
larva_steepness_homo_r      = input_data.larva_sur_steep_r
larva_steepness_hetero      = input_data.hetero(larva_steepness_homo_s,
                                                larva_steepness_homo_r)
larva_steepness             = {keyword.homo_s:  larva_steepness_homo_s,
                               keyword.homo_r:  larva_steepness_homo_r,
                               keyword.hetero:  larva_steepness_hetero}

larva_survival = models.Larva(larva_minimum,
                              larva_maximum,
                              larva_inflection,
                              larva_steepness)
