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


# Generate the egg survival probability
egg_prob = probability_egg(data.mu_egg_dev,
                           data.egg_survivals)

# Generate the pupa survival probability
pupa_prob = probability_pupa(data.pupa_duration,
                             data.pupa_survivals)

# Generate the adult survival probability
adult_prob = probability_adult(data.adult_duration)
