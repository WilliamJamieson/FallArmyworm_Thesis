import source.keyword as keyword


dominance = 0


def hetero(homo_s: float,
           homo_r: float) -> float:
    """
    Calculate the heterozyous parameter using degree of dominance
        SR = (SS + RR)/2 + D*(SS - RR)/2

        SR = heterozyous
        SS = susceptible
        RR = resistant
        D  = degree of dominance

    Args:
        homo_s: susceptible parameter
        homo_r: resistant   parameter

    Returns:
        heterozygous parameter
    """

    avg = (homo_s + homo_r)/2
    sub = (homo_s - homo_r)/2

    return avg + (dominance * sub)


# save name
save_name = 'parallel_sim_10_gen_no_bt_only_sus'

# steps
num_steps = 2


# initial data
egg_masses_homo_r = 0
egg_masses_hetero = 0
egg_masses_homo_s = 0

larvae_homo_r = 0
larvae_hetero = 0
larvae_homo_s = 0

pupae_homo_r = 0
pupae_hetero = 0
pupae_homo_s = 0

adults_homo_r = 0
adults_hetero = 0
adults_homo_s = 0

pregnant_homo_r = 0
pregnant_hetero = 0
pregnant_homo_s = 100


# bt
bt_prob = 0


# Larva Mass Measurements
mass_final_s  = 161.1
time_final_s  = 15.4
mass_middle_s = 58.1
time_middle_s = 8

mass_final_r  = 151.3
time_final_r  = 23.9
mass_middle_r = 41
time_middle_r = 10

mass_sigma = 0.1

# Egg_mass measurements
egg_mass_samples = [10.4,
                    14.2,
                    12.8,
                    14.9,
                    14.7,
                    10.8,
                    12.0,
                    11.3,
                    11.2,
                    14.4,
                    10.3,
                    13.7]
egg_mass_number = [164.5,
                   112.8,
                   269.6,
                   222.1,
                   129.2,
                   143.3,
                   205.1,
                   197.2,
                   156.0,
                   276.4,
                   154.7,
                   200.2]
homo_r_mass_factor = 0.8

# Leaf mass
leaf_mass_mu    = 1000
leaf_mass_sigma = 0.001
leaf_mass_max   = 10000

# Leaf recovery
leaf_alpha = 1
leaf_beta  = 1

# Movement measures
larva_move_loc   = 0
larva_move_scale = 1
larva_move_shape = 1

adult_move_loc   = 0
adult_move_scale = 1
adult_move_shape = 1

# Survival measurements
larva_wild_lower_homo_s = 0.9
larva_wild_lower_homo_r = 0.9
larva_wild_lower_hetero = hetero(larva_wild_lower_homo_s,
                                 larva_wild_lower_homo_r)
larva_wild_lower        = {keyword.homo_s: larva_wild_lower_homo_s,
                           keyword.homo_r: larva_wild_lower_homo_r,
                           keyword.hetero: larva_wild_lower_hetero}

larva_wild_upper_homo_s = 0.95
larva_wild_upper_homo_r = 0.95
larva_wild_upper_hetero = hetero(larva_wild_upper_homo_s,
                                 larva_wild_upper_homo_r)
larva_wild_upper        = {keyword.homo_s: larva_wild_upper_homo_s,
                           keyword.homo_r: larva_wild_upper_homo_r,
                           keyword.hetero: larva_wild_upper_hetero}

larva_bt_lower_homo_s = 0.4
larva_bt_lower_homo_r = 0.9
larva_bt_lower_hetero = hetero(larva_bt_lower_homo_s,
                                 larva_bt_lower_homo_r)
larva_bt_lower        = {keyword.homo_s: larva_bt_lower_homo_s,
                         keyword.homo_r: larva_bt_lower_homo_r,
                         keyword.hetero: larva_bt_lower_hetero}

larva_bt_upper_homo_s = 0.8
larva_bt_upper_homo_r = 0.95
larva_bt_upper_hetero = hetero(larva_bt_upper_homo_s,
                               larva_bt_upper_homo_r)
larva_bt_upper        = {keyword.homo_s: larva_bt_upper_homo_s,
                         keyword.homo_r: larva_bt_upper_homo_r,
                         keyword.hetero: larva_bt_upper_hetero}

larva_lower = {keyword.not_bt: larva_wild_lower,
               keyword.bt:     larva_bt_lower}
larva_upper = {keyword.not_bt: larva_wild_upper,
               keyword.bt:     larva_bt_upper}

larva_inflection_homo_s = time_final_s/2
larva_inflection_homo_r = time_final_r/2
larva_inflection_hetero = hetero(larva_inflection_homo_s,
                                 larva_inflection_homo_r)
larva_inflection        = {keyword.homo_s: larva_inflection_homo_s,
                           keyword.homo_r: larva_inflection_homo_r,
                           keyword.hetero: larva_inflection_hetero}

larva_sur_steep_homo_s = 4
larva_sur_steep_homo_r = 4
larva_sur_steep_hetero = hetero(larva_sur_steep_homo_s,
                                larva_sur_steep_homo_r)
larva_sur_steep        = {keyword.homo_s: larva_sur_steep_homo_s,
                          keyword.homo_r: larva_sur_steep_homo_r,
                          keyword.hetero: larva_sur_steep_hetero}

egg_survive_prob = 0.95
egg_lifetime     = 3

pupa_survive_prob = 0.95
pupa_lifetime     = 10

adult_survive_prob = 0.95
adult_lifetime     = 10

# Development measurements
larva_mu_homo_s      = mass_final_s
larva_sigma_homo_s   = 25
larva_minimum_homo_s = time_final_s

larva_mu_homo_r      = mass_final_r
larva_sigma_homo_r   = 25
larva_minimum_homo_r = time_final_r

larva_mu_hetero      = hetero(larva_mu_homo_s, larva_mu_homo_r)
larva_sigma_hetero   = hetero(larva_sigma_homo_s, larva_sigma_homo_r)
larva_minimum_hetero = hetero(larva_minimum_homo_s, larva_minimum_homo_r)

larva_mu      = {keyword.homo_s:  larva_mu_homo_s,
                 keyword.homo_r:  larva_mu_homo_r,
                 keyword.hetero:  larva_mu_hetero}
larva_sigma   = {keyword.homo_s:  larva_sigma_homo_s,
                 keyword.homo_r:  larva_sigma_homo_r,
                 keyword.hetero:  larva_sigma_hetero}
larva_minimum = {keyword.homo_s:  larva_minimum_homo_s,
                 keyword.homo_r:  larva_minimum_homo_r,
                 keyword.hetero:  larva_minimum_hetero}

egg_mu      = 3
egg_sigma   = 1
egg_minimum = 2

pupa_mu      = 10
pupa_sigma   = 3
pupa_minimum = 8

# Starvation factor
starvation_mu    = 0.8
starvation_sigma = 0.05

# Foraging measurements
egg_factor            = 1
larva_factor          = 1


def mid(point):
    return (1 - point) / point


egg_slope      = 4
larva_slope    = 4
egg_mid_prob   = 0.9
egg_mid        = mid(egg_mid_prob)
larva_mid_prob = 0.25
larva_mid      = mid(larva_mid_prob)

loss_slope = {keyword.egg_mass: egg_slope,
              keyword.larva:    larva_slope}
loss_mid   = {keyword.egg_mass: egg_mid,
              keyword.larva:    larva_mid}

# Cannibalism measurements
fight_steepness       = 4
cannibalism_encounter = 1
cannibalism_radius    = 0

# Reproduction measurements
female_prob    = 0.5
mate_encounter = 10
mate_radius    = 2

trials            = 5
fecundity_maximum = 10
fecundity_decay   = 0.01

density_eta   = 0.45
density_gamma = 4

lifetime_female = True
lifetime_male   = False
limited         = True

# Migration
#   emigration
mean_adult  = 300
sigma_adult = 10
mean_larva  = 300
sigma_larva = 10
mean_pupa   = 300
sigma_pupa  = 10
mean_egg    = 300
sigma_egg   = 10
#   immigration
lambda_pregnant = 3
lambda_adult    = 3
lambda_larva    = 3
lambda_pupa     = 3
lambda_egg      = 3
