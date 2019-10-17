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


# Pass through the egg development parameters
mu_egg_dev  = data.mu_egg_dev
sig_egg_dev = data.sig_egg_dev

# Generate the pupa development parameters
mu_pupa_dev, sig_pupa_dev = normal_pupa(data.pupa_duration)
