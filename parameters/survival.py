import numpy as np

import parameters.basic_data as data


def probability_egg(duration:       float,
                    total_survival: list) -> float:
    """
    Calculate the daily survival probability for eggs:

    Args:
        duration:       average duration of stage
        total_survival: data points on total survival

    Returns:
        the average daily survival probability for eggs
    """

    total = np.mean(total_survival)

    power = 1 / (duration - 1)

    daily = total**power

    print('Egg Survival')
    print('   Egg total survival: {}'. format(total))
    print('   Egg total duration: {}'. format(duration))
    print('   Egg daily survival: {}'. format(daily))

    return daily


def probability_pupa(duration:       list,
                     total_survival: list) -> float:
    """
    Calculate the daily survival probability for pupae

    Args:
        duration:       average duration data
        total_survival: data points on total survival

    Returns:
        the average daily survival probability for pupae
    """

    t     = np.mean(duration)
    total = np.mean(total_survival)

    power = 1 / (t - 1)

    daily = total**power

    print('Pupa Survival')
    print('   Pupa total survival: {}'. format(total))
    print('   Pupa total duration: {}'. format(t))
    print('   Pupa daily survival: {}'. format(daily))

    return daily


def probability_adult(duration: list) -> float:
    """
    Calculate the daily survival probability for adults

    Args:
        duration: average duration for an adult

    Returns:
        the average daily survival probability for adults
    """

    t = np.mean(duration)

    daily = (t - 1) / t

    print('Adult Survival')
    print('   Adult total duration: {}'. format(t))
    print('   Adult daily survival: {}'. format(daily))

    return daily


def probability_larva(duration_rr: float,
                      duration_ss: float,
                      total_survival_non_bt: list,
                      total_survival_bt_rr:  list) -> tuple:
    """
    Calculate the daily survival probabilities for larvae
    Args:
        duration_rr:           duration of rr
        duration_ss:           duration of ss
        total_survival_non_bt: data on total survival on non Bt
        total_survival_bt_rr:  data on total survival on Bt for rr

    Returns:
        the daily survival for non Bt rr,
        the daily survival for non Bt ss,
        the daily survival for Bt rr,
        the daily survival for Bt ss
    """

    t = np.mean([duration_rr, duration_ss])

    power     = 1 / (t - 1)
    # power_rr  = 1 / (duration_rr - 1)

    total_survival = total_survival_non_bt + total_survival_bt_rr
    total          = np.mean(total_survival)
    # total_non_bt = np.mean(total_survival_non_bt)
    # total_bt_rr  = np.mean(total_survival_bt_rr)

    daily = total**power
    # daily_non_bt_rr = total_non_bt**power
    # daily_non_bt_ss = total_non_bt**power
    # daily_bt_rr     = total_bt_rr**power_rr

    print('Larva non-Bt RR')
    print('   Larva non-Bt RR total survival: {}'. format(total))
    print('   Larva non-Bt RR total duration: {}'. format(t))
    print('   Larva non-Bt RR daily survival: {}'. format(daily))

    print('Larva non-Bt SS')
    print('   Larva non-Bt SS total survival: {}'. format(total))
    print('   Larva non-Bt SS total duration: {}'. format(t))
    print('   Larva non-Bt SS daily survival: {}'. format(daily))

    print('Larva Bt RR')
    print('   Larva RR total survival: {}'. format(total))
    print('   Larva RR total duration: {}'. format(t))
    print('   Larva RR daily survival: {}'. format(daily))

    return daily, daily, daily


def probability_larva_low(duration: float,
                          total_survival: list) -> float:
    """
    Calculate the low ss survival probability
    Args:
        duration:       duration ss
        total_survival: low total survival ss

    Returns:
        daily survival for ss (low)
    """

    power = 1 / (duration - 1)
    total = np.mean(total_survival)
    daily = total**power

    print('Larva Bt SS')
    print('   Larva SS low total survival: {}'. format(total))
    print('   Larva SS low total duration: {}'. format(duration))
    print('   Larva SS low daily survival: {}'. format(daily))

    return daily


def probability_larva_mid(duration: float,
                          total_survival: list) -> float:
    """
    Calculate the mid ss survival probability
    Args:
        duration:       duration ss
        total_survival: mid total survival ss

    Returns:
        daily survival for ss (low)
    """

    power = 1 / (duration - 1)
    total = np.mean(total_survival)
    daily = total ** power

    print('Larva Bt SS')
    print('   Larva SS mid total survival: {}'.format(total))
    print('   Larva SS mid total duration: {}'.format(duration))
    print('   Larva SS mid daily survival: {}'.format(daily))

    return daily


def probability_larva_high(duration: float,
                           total_survival: list) -> float:
    """
    Calculate the high ss survival probability
    Args:
        duration:       duration ss
        total_survival: high total survival ss

    Returns:
        daily survival for ss (low)
    """

    power = 1 / (duration - 1)
    total = np.mean(total_survival)
    daily = total ** power

    print('Larva Bt SS')
    print('   Larva SS high total survival: {}'.format(total))
    print('   Larva SS high total duration: {}'.format(duration))
    print('   Larva SS high daily survival: {}'.format(daily))

    return daily


# Generate the egg survival probability
egg_prob = probability_egg(data.mu_egg_dev,
                           data.egg_survivals)

# Generate the pupa survival probability
pupa_prob = probability_pupa(data.pupa_duration,
                             data.pupa_survivals)

# Generate the adult survival probability
adult_prob = probability_adult(data.adult_duration)

# Generate the larva survival probabilities
larva_non_bt_rr, larva_non_bt_ss, larva_bt_rr = \
    probability_larva(data.growth_times_rr[-1],
                      data.growth_times_ss[-1],
                      data.larva_non_bt_survivals,
                      data.larva_bt_survivals_rr)
larva_bt_low_ss  = probability_larva_low(data.growth_times_ss[-1],
                                         data.larva_bt_low_survivals_ss)
larva_bt_mid_ss  = probability_larva_mid(data.growth_times_ss[-1],
                                         data.larva_bt_mid_survivals_ss)
larva_bt_high_ss = probability_larva_high(data.growth_times_ss[-1],
                                          data.larva_bt_high_survivals_ss)
