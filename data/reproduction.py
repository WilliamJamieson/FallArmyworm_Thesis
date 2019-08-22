import data.input_data as input_data

import source.keyword as keyword

import source.reproduction.models as models


# Generate the input models
#       init_sex
sex_prob = input_data.female_prob

init_sex = models.InitSex(sex_prob)
#       mating
mating_factor = input_data.mate_encounter

mating = models.Mating(mating_factor)

#       mate_radius
radius = input_data.mate_radius

mate_radius = models.Radius(radius)

#       fecundity
maximum = input_data.fecundity_maximum
decay   = input_data.fecundity_decay

fecundity = models.Fecundity(maximum,
                             decay)

#       density
eta   = input_data.density_eta
gamma = input_data.density_gamma

density = models.Density(eta,
                         gamma)

#      fixed value inputs
values = {keyword.trials:          input_data.trials,
          keyword.lifetime_male:   input_data.lifetime_male,
          keyword.lifetime_female: input_data.lifetime_female}
