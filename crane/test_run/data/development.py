import data.input_data as input_data

import source.keyword as keyword

import source.development.models as models


# Generate the input models
#       egg_development
egg_mu      = input_data.egg_mu
egg_sigma   = input_data.egg_sigma
egg_minimum = input_data.egg_minimum

egg_development = models.Egg(egg_mu,
                             egg_sigma,
                             egg_minimum)

#       pupa_development
pupa_mu      = input_data.pupa_mu
pupa_sigma   = input_data.pupa_sigma
pupa_minimum = input_data.pupa_minimum

pupa_development = models.Pupa(pupa_mu,
                               pupa_sigma,
                               pupa_minimum)

#       larva_development
larva_mu_homo_s = input_data.larva_mu_s
larva_mu_homo_r = input_data.larva_mu_r
larva_mu_hetero = input_data.hetero(larva_mu_homo_s,
                                    larva_mu_homo_r)
larva_mu        = {keyword.homo_s:  larva_mu_homo_s,
                   keyword.homo_r:  larva_mu_homo_r,
                   keyword.hetero:  larva_mu_hetero}

larva_sigma_homo_s = input_data.larva_sigma_s
larva_sigma_homo_r = input_data.larva_sigma_r
larva_sigma_hetero = input_data.hetero(larva_sigma_homo_s,
                                       larva_sigma_homo_r)
larva_sigma        = {keyword.homo_s:  larva_sigma_homo_s,
                      keyword.homo_r:  larva_sigma_homo_r,
                      keyword.hetero:  larva_sigma_hetero}

larva_minimum_homo_s = input_data.larva_minimum_s
larva_minimum_homo_r = input_data.larva_minimum_r
larva_minimum_hetero = input_data.hetero(larva_minimum_homo_s,
                                         larva_minimum_homo_r)
larva_minimum        = {keyword.homo_s:  larva_minimum_homo_s,
                        keyword.homo_r:  larva_minimum_homo_r,
                        keyword.hetero:  larva_minimum_hetero}

larva_development = models.Larva(larva_mu,
                                 larva_sigma,
                                 larva_minimum)
