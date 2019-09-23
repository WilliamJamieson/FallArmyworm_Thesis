import data.input_data as input_data

import source.keyword as keyword


# Get the setup tuples
#       emigration_adult
emigration_adult = (input_data.mean_adult, input_data.sigma_adult,
                    [keyword.female, keyword.male, keyword.mated])
#       emigration_larva
emigration_larva = (input_data.mean_larva, input_data.sigma_larva,
                    [keyword.larva])
#       emigration_pupa
emigration_pupa  = (input_data.mean_pupa, input_data.sigma_pupa,
                    [keyword.pupa])
#       emigration_egg
emigration_egg   = (input_data.mean_egg, input_data.sigma_egg,
                    [keyword.egg_mass])

#       immigration_adult
immigration_adult_homo_r = (input_data.lambda_adult, keyword.homo_r,
                            keyword.pregnant)
immigration_adult_hetero = (input_data.lambda_adult, keyword.hetero,
                            keyword.pregnant)
immigration_adult_homo_s = (input_data.lambda_adult, keyword.homo_s,
                            keyword.pregnant)
#       immigration_larva
immigration_larva_homo_r = (input_data.lambda_larva, keyword.homo_r,
                            keyword.larva)
immigration_larva_hetero = (input_data.lambda_larva, keyword.hetero,
                            keyword.larva)
immigration_larva_homo_s = (input_data.lambda_larva, keyword.homo_s,
                            keyword.larva)
#       immigration_pupa
immigration_pupa_homo_r = (input_data.lambda_pupa, keyword.homo_r,
                            keyword.pupa)
immigration_pupa_hetero = (input_data.lambda_pupa, keyword.hetero,
                            keyword.pupa)
immigration_pupa_homo_s = (input_data.lambda_pupa, keyword.homo_s,
                            keyword.pupa)
#       immigration_egg
immigration_egg_homo_r = (input_data.lambda_egg, keyword.homo_r,
                            keyword.egg_mass)
immigration_egg_hetero = (input_data.lambda_egg, keyword.hetero,
                            keyword.egg_mass)
immigration_egg_homo_s = (input_data.lambda_egg, keyword.homo_s,
                            keyword.egg_mass)
