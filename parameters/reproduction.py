import source.keyword as keyword

import parameters.basic_data as data


# Pass through the sex probability
female_prob = data.female_prob

# Pass through the reproductive encounter factors
encounter = data.mate_encounter
radius    = data.mate_radius

# Pass through the fecundity factors
maximum = data.fecundity_maximum
decay   = data.fecundity_decay

# Pass through the density factors
eta   = data.eta
gamma = data.gamma

# Pass through fixed values
values = {keyword.trials:          data.trials,
          keyword.limited:         data.limited,
          keyword.lifetime_male:   data.lifetime_male,
          keyword.lifetime_female: data.lifetime_female}
