import numpy as np

import parameters.basic_data as data


def poisson_egg_mass(number_data: list) -> float:
    """
    Find the value of the mean for the Poisson distribution of number of eggs
        in egg_mass from the data

    Args:
        number_data: list of number of eggs in egg_mass data points

    Returns:
        lambda
    """

    return float(np.mean(number_data))


def normal_egg_mass(mass_data: list) -> tuple:
    """
    Find the values for the normal distribution of egg_mass masses from the
        given data

    Args:
        mass_data: list of egg_mass mass data points

    Returns:
        mean, standard deviation
    """

    mu    = float(np.mean(mass_data))
    sigma = float(np.std(mass_data))

    return mu, sigma


def normal_scaling(mu:    float,
                   sigma: float,
                   scale: float) -> tuple:
    """
    Scale the parameters of a normal distribution correctly

    Args:
        mu:    mean of distribution
        sigma: std of distribution
        scale: scale factor

    Returns:
        scaled mu, scaled sigma
    """

    s_mu    = mu*scale
    s_sigma = sigma*(scale**2)

    return s_mu, s_sigma


def normal_larva(mu:    float,
                 sigma: float,
                 lam:   float) -> tuple:
    """
    Get the parameters of a normal distribution for the mass of a new larva

    Args:
        mu:    mean egg_mass mass
        sigma: std  egg_mass mass
        lam:   mean egg_mass num eggs

    Returns:
        larva mu, larva_sigma
    """

    scale = 1/lam

    return normal_scaling(mu, sigma, scale)


# Generate the init_egg parameters
lam_0_egg                 = poisson_egg_mass(data.egg_mass_mean_number_eggs)
mu_0_egg_ss, sig_0_egg_ss = normal_egg_mass(data.egg_mass_mean_mass)
mu_0_egg_rr, sig_0_egg_rr = normal_scaling(mu_0_egg_ss, sig_0_egg_ss,
                                           data.ss_to_rr_mass_scale)

# Generate the init_larva parameters
mu_0_larva_ss, sig_0_larva_ss = normal_larva(mu_0_egg_ss, sig_0_egg_ss,
                                             lam_0_egg)
mu_0_larva_rr, sig_0_larva_rr = normal_larva(mu_0_egg_rr, sig_0_egg_rr,
                                             lam_0_egg)

# Pass through the init_mature parameters
mu_0_mature_ss  = data.mu_0_mature_ss
sig_0_mature_ss = data.sig_0_mature_ss
mu_0_mature_rr  = data.mu_0_mature_rr
sig_0_mature_rr = data.sig_0_mature_rr


# Print data points
if data.print_data:
    print('Init_egg_mass data')
    print('    lam_0_egg: {}'.format(lam_0_egg))
    print('    mu_0_egg_ss: {}, sig_0_egg_ss: {}'.
          format(mu_0_egg_ss, sig_0_egg_ss))
    print('    mu_0_egg_rr: {}, sig_0_egg_rr: {}'.
          format(mu_0_egg_rr, sig_0_egg_rr))
    print('Init_larva data')
    print('    mu_0_larva_ss: {}, sig_0_larva_ss: {}'.
          format(mu_0_larva_ss, sig_0_larva_ss))
    print('    mu_0_larva_rr: {}, sig_0_larva_rr: {}'.
          format(mu_0_larva_rr, sig_0_larva_rr))
    print('Init_mature data')
    print('    mu_0_mature_ss: {}, sig_0_mature_ss: {}'.
          format(mu_0_mature_ss, sig_0_mature_ss))
    print('    mu_0_mature_rr: {}, sig_0_mature_rr: {}'.
          format(mu_0_mature_rr, sig_0_mature_rr))
