import source.keyword as keyword

import parameters.basic_data as data


# Get the consumption steps
forage_steps = data.hourly_steps

# Pass through the theta values
theta_adlibitum = data.theta_adlibitum
theta_scarce    = data.theta_scarce
sig_scarce      = data.sig_scarce

# Pass through the cannibalism factors
fight_slope           = data.fight_slope
cannibalism_radius    = data.cannibalism_radius
cannibalism_encounter = data.cannibalism_encounter


def mid(prob: float) -> float:
    """
    Calculate the actual value of mid point constant

    Args:
        prob: loss probability

    Returns:
        the mid factor
    """

    return (1 - prob) / prob


loss_slope = data.loss_slope
mid = {
    keyword.egg_mass: mid(data.egg_loss),
    keyword.larva:    mid(data.larva_loss)
}

# Pass through the forage factors

egg_factor   = data.egg_factor
larva_factor = data.larva_factor
