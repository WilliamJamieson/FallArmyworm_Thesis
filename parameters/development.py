import numpy as np

import parameters.basic_data as data


def normal_pupa(duration_data: list) -> tuple:
    """
    Calculate the normal distribution pupal stage duration

    Args:
        duration_data: data points on pupa durations

    Returns:
        mu, sigma for duration
    """

    mu    = float(np.mean(duration_data))
    sigma = float(np.std(duration_data))

    return mu, sigma


def normal_larva(mass:     list,
                 mass_sem: list,
                 samples:  int) -> tuple:
    """
    Get a normal distribution for the mass of larva pupating
    Args:
        mass:     mass sample point data
        mass_sem: mass sem data
        samples:  number of total samples for each point

    Returns:
        mu, sigma for pupation mass
    """

    mu = mass[-1]

    sem   = mass_sem[-1]
    sigma = sem*np.sqrt(samples)

    return mu, sigma


# Pass through the egg development parameters
mu_egg  = data.mu_egg_dev
sig_egg = data.sig_egg_dev

# Generate the pupa development parameters
mu_pupa, sig_pupa = normal_pupa(data.pupa_duration)

# Generate the larva development parameters
mu_larva_ss, sig_larva_ss = normal_larva(data.growth_mass_ss,
                                         data.growth_mass_sem_ss,
                                         data.growth_samples_ss)
mu_larva_rr, sig_larva_rr = normal_larva(data.growth_mass_rr,
                                         data.growth_mass_sem_rr,
                                         data.growth_samples_rr)
