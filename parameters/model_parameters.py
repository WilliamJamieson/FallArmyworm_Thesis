import parameters.development  as dev
import parameters.forage       as forage
import parameters.growth       as growth
import parameters.init_biomass as init_bio
import parameters.movement     as move
import parameters.reproduction as repro
import parameters.survival     as sur


print_data = True

field_grid = 50
plant_grid = 10

timesteps = 4200

mean_adult  = 300
sigma_adult = 10

dominance_0 = 0
dominance_1 = 0.11
dominance_2 = 0.29

start_preg_ss = 200
start_preg_rr = 200

mix_preg_rr = 50
mix_preg_ss = 200

bt_prop_0 = 0.0
bt_prop_7 = 0.7
bt_prop_8 = 0.8
bt_prop_9 = 0.9
bt_prop_1 = 1.0

# List out init biomass parameters
lam_0_egg    = init_bio.lam_0_egg
mu_0_egg_ss  = init_bio.mu_0_egg_ss
sig_0_egg_ss = init_bio.sig_0_egg_ss
mu_0_egg_rr  = init_bio.mu_0_egg_rr
sig_0_egg_rr = init_bio.sig_0_egg_rr

mu_0_larva_ss  = init_bio.mu_0_larva_ss
sig_0_larva_ss = init_bio.sig_0_larva_ss
mu_0_larva_rr  = init_bio.mu_0_larva_rr
sig_0_larva_rr = init_bio.sig_0_larva_rr

mu_0_mature_ss  = init_bio.mu_0_mature_ss
sig_0_mature_ss = init_bio.sig_0_mature_ss
mu_0_mature_rr  = init_bio.mu_0_mature_rr
sig_0_mature_rr = init_bio.sig_0_mature_rr

mu_leaf  = init_bio.mu_leaf
sig_leaf = init_bio.sig_leaf

# List out the growth parameters
alpha_ss      = growth.alpha_ss
beta_ss       = growth.beta_ss
max_mass_ss   = growth.max_mass_ss
mass_const_ss = growth.mass_const_ss

alpha_rr      = growth.alpha_rr
beta_rr       = growth.beta_rr
max_mass_rr   = growth.max_mass_rr
mass_const_rr = growth.mass_const_rr

# List out the forage parameters
forage_steps    = forage.forage_steps
theta_adlibitum = forage.theta_adlibitum
theta_scarce    = forage.theta_scarce
sig_scarce      = forage.sig_scarce

fight_slope           = forage.fight_slope
cannibalism_radius    = forage.cannibalism_radius
cannibalism_encounter = forage.cannibalism_encounter

cannib_0 = cannibalism_encounter
cannib_1 = 0.15
cannib_2 = 0.38
cannib_3 = 0.5
cannib_4 = 1.0

egg_factor   = forage.egg_factor
larva_factor = forage.larva_factor

loss_slope = forage.loss_slope
mid        = forage.mid

# List out development parameters
mu_egg_dev  = dev.mu_egg
sig_egg_dev = dev.sig_egg

mu_pupa_dev  = dev.mu_pupa
sig_pupa_dev = dev.sig_pupa

mu_larva_dev_ss  = dev.mu_larva_ss
sig_larva_dev_ss = dev.sig_larva_ss
mu_larva_dev_rr  = dev.mu_larva_rr
sig_larva_dev_rr = dev.sig_larva_rr

# List out reproduction parameters
female_prob = repro.female_prob

mate_encounter = repro.encounter
mate_radius    = repro.radius

fecundity_maximum = repro.maximum
fecundity_decay   = repro.decay

eta   = repro.eta
gamma = repro.gamma

repro_values = repro.values

# List out movement parameters
larva_scale = move.larva_scale
larva_shape = move.larva_shape
adult_scale = move.adult_scale
adult_shape = move.adult_shape

# List out survival parameters
egg_prob   = sur.egg_prob
pupa_prob  = sur.pupa_prob
adult_prob = sur.adult_prob

larva_prob_non_bt_rr  = sur.larva_non_bt_rr
larva_prob_non_bt_ss  = sur.larva_non_bt_ss
larva_prob_bt_rr      = sur.larva_bt_rr
larva_prob_bt_low_ss  = sur.larva_bt_low_ss
larva_prob_bt_mid_ss  = sur.larva_bt_mid_ss
larva_prob_bt_high_ss = sur.larva_bt_high_ss


# Print data to console
if print_data:
    # Print the init_biomass
    print('Init_egg_mass parameters')
    print('    lam_0_egg: {}'.format(lam_0_egg))
    print('    mu_0_egg_ss: {}, sig_0_egg_ss: {}'.
          format(mu_0_egg_ss, sig_0_egg_ss))
    print('    mu_0_egg_rr: {}, sig_0_egg_rr: {}'.
          format(mu_0_egg_rr, sig_0_egg_rr))
    print('Init_larva parameters')
    print('    mu_0_larva_ss: {}, sig_0_larva_ss: {}'.
          format(mu_0_larva_ss, sig_0_larva_ss))
    print('    mu_0_larva_rr: {}, sig_0_larva_rr: {}'.
          format(mu_0_larva_rr, sig_0_larva_rr))
    print('Init_mature parameters')
    print('    mu_0_mature_ss: {}, sig_0_mature_ss: {}'.
          format(mu_0_mature_ss, sig_0_mature_ss))
    print('    mu_0_mature_rr: {}, sig_0_mature_rr: {}'.
          format(mu_0_mature_rr, sig_0_mature_rr))
    print('    mu_leaf: {}, sig_leaf: {}'.
          format(mu_leaf, sig_leaf))

    # Print the growth
    print('Growth parameters')
    print('    alpha_ss: {}, beta_ss: {}, max_mass_ss: {}'.
          format(alpha_ss, beta_ss, max_mass_ss))
    print('    alpha_rr: {}, beta_rr: {}, max_mass_rr: {}'.
          format(alpha_rr, beta_rr, max_mass_rr))

    # Print the development
    print('Development parameters')
    print('    mu_egg_dev: {}, sig_egg_dev: {}'.
          format(mu_egg_dev, sig_egg_dev))
    print('    mu_pupa_dev: {}, sig_pupa_dev: {}'.
          format(mu_pupa_dev, sig_pupa_dev))
    print('    mu_larva_dev_ss: {}, sig_larva_dev_ss: {}'.
          format(mu_larva_dev_ss, sig_larva_dev_ss))
    print('    mu_larva_dev_rr: {}, sig_larva_dev_rr: {}'.
          format(mu_larva_dev_rr, sig_larva_dev_rr))

    # Print the movement
    print('Movement parameters')
    print('    larva_scale: {}, larva_shape: {}'.
          format(larva_scale, larva_shape))
    print('    adult_scale: {}, adult_shape: {}'.
          format(adult_scale, adult_shape))
