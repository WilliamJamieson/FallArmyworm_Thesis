import importlib
import sys

import source.keyword as keyword

simulation   = vars(sys.modules[__name__])['__package__']
biomass      = importlib.import_module('.data.biomass',      package=simulation)
data         = importlib.import_module('.data.input_data',   package=simulation)
development  = importlib.import_module('.data.development',  package=simulation)
forage       = importlib.import_module('.data.forage',       package=simulation)
graph        = importlib.import_module('.data.graph',        package=simulation)
migration    = importlib.import_module('.data.migration',    package=simulation)
movement     = importlib.import_module('.data.movement',     package=simulation)
reproduction = importlib.import_module('.data.reproduction', package=simulation)
survival     = importlib.import_module('.data.survival',     package=simulation)
tracking     = importlib.import_module('.data.tracking',     package=simulation)

print('Simulation package {}'.format(simulation))

grid = [graph.graph(25),
        graph.graph(10)]

attrs = {0: tracking.genotype_death_filters_attrs}

emigration  = [migration.emigration_adult(data.mean_adult,
                                          data.sigma_adult)]
immigration = []
# immigration = [migration.immigration_pregnant_homo_r(data.lambda_pregnant),
#                migration.immigration_pregnant_homo_s(data.lambda_pregnant),
#                migration.immigration_pregnant_hetero(data.lambda_pregnant)]

steps = [({keyword.female: [keyword.move,
                            keyword.reproduce],
           keyword.male: [keyword.move],
           keyword.mated: [keyword.move],
           keyword.larva: [keyword.move,
                           keyword.consume]}, 24, True),
         ({keyword.female: [keyword.survive,
                            keyword.advance_age,
                            keyword.reset],
           keyword.male: [keyword.survive,
                          keyword.advance_age,
                          keyword.reset],
           keyword.mated: [keyword.survive,
                           keyword.advance_age,
                           keyword.reset],
           keyword.larva: [keyword.grow,
                           keyword.survive,
                           keyword.develop,
                           keyword.advance_age,
                           keyword.reset],
           keyword.pupa: [keyword.survive,
                          keyword.develop,
                          keyword.advance_age],
           keyword.egg: [keyword.survive,
                         keyword.develop,
                         keyword.advance_age],
           keyword.egg_mass: [keyword.reset]},)]

max_gut, growth, init_num, init_mass, init_juvenile, init_mature = \
    biomass.biomass_models(data.egg_mass_number,
                           data.egg_mass_samples,
                           data.homo_r_mass_factor,
                           data.dominance,
                           data.mass_middle_s,
                           data.time_middle_s,
                           data.mass_middle_r,
                           data.time_middle_r,
                           data.mass_final_s,
                           data.time_final_s,
                           data.mass_final_r,
                           data.time_final_r,
                           data.mass_sigma)
forage_egg   = forage.egg(data.egg_factor)
forage_larva = forage.larva(data.larva_factor)

models = [max_gut,
          growth,
          init_num,
          init_mass,
          init_juvenile,
          init_mature,
          biomass.init_plant(data.leaf_mass_mu,
                             data.leaf_mass_sigma,
                             data.leaf_mass_max),
          development.egg(data.egg_mu,
                          data.egg_sigma,
                          data.egg_minimum),
          development.larva(data.larva_mu,
                            data.larva_sigma,
                            data.larva_minimum),
          development.pupa(data.pupa_mu,
                           data.pupa_sigma,
                           data.pupa_minimum),
          forage.ad_libitum(max_gut),
          forage_egg,
          forage_larva,
          forage.loss(data.loss_slope,
                      data.loss_mid,
                      max_gut,
                      forage_egg,
                      forage_larva),
          forage.fight(data.fight_steepness),
          forage.encounter(data.cannibalism_encounter),
          forage.radius(data.cannibalism_radius),
          movement.adult(data.adult_move_loc,
                         data.adult_move_scale,
                         data.adult_move_shape),
          movement.larva(data.larva_move_loc,
                         data.larva_move_scale,
                         data.larva_move_shape),
          reproduction.mating(data.mate_encounter),
          reproduction.radius(data.mate_radius),
          reproduction.fecundity(data.fecundity_maximum,
                                 data.fecundity_decay),
          reproduction.density(data.density_eta,
                               data.density_gamma),
          reproduction.init_sex(data.female_prob),
          survival.egg(data.egg_lifetime,
                       data.egg_survive_prob),
          survival.larva(data.larva_lower,
                         data.larva_upper,
                         data.larva_inflection,
                         data.larva_sur_steep),
          survival.pupa(data.pupa_lifetime,
                        data.pupa_survive_prob),
          survival.adult(data.adult_lifetime,
                         data.adult_survive_prob)]
variables = {keyword.trials:          data.trials,
             keyword.limited:         data.limited,
             keyword.lifetime_male:   data.lifetime_male,
             keyword.lifetime_female: data.lifetime_female}

nums = (
    (data.egg_masses_homo_r, data.egg_masses_hetero, data.egg_masses_homo_s),
    (data.larvae_homo_r,     data.larvae_hetero,     data.larvae_homo_s),
    (data.pupae_homo_r,      data.pupae_hetero,      data.pupae_homo_s),
    (data.adults_homo_r,     data.adults_hetero,     data.adults_homo_s),
    (data.pregnant_homo_r,   data.pregnant_hetero,   data.pregnant_homo_s),
)

bt_prop   = data.bt_prob
timesteps = data.num_steps
path_save = data.save_path
base_save = data.save_name
