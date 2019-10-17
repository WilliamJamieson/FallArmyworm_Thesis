import parameters.development  as dev
import parameters.growth       as growth
import parameters.init_biomass as init_bio


print_data = True

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
alpha_ss    = growth.alpha_ss
beta_ss     = growth.beta_ss
max_mass_ss = growth.max_mass_ss

alpha_rr    = growth.alpha_rr
beta_rr     = growth.beta_rr
max_mass_rr = growth.max_mass_rr

# List out development parameters
mu_egg_dev  = dev.mu_egg
sig_egg_dev = dev.sig_egg

mu_pupa_dev  = dev.mu_pupa
sig_pupa_dev = dev.sig_pupa

mu_larva_dev_ss  = dev.mu_larva_ss
sig_larva_dev_ss = dev.sig_larva_ss
mu_larva_dev_rr  = dev.mu_larva_rr
sig_larva_dev_rr = dev.sig_larva_rr


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
