# Included here are data points from a wide array of studies
print_data = True


# Whiteford et. al. 1988 (egg_mass data)
egg_mass_mean_number_eggs = [
    164.4,
    112.8,
    269.6,
    222.1,
    129.2,
    143.2,
    205.1,
    197.2,
    156.0,
    276.4,
    154.7,
    200.2
]
egg_mass_mean_mass = [
    10.4,
    14.3,
    12.8,
    14.9,
    14.7,
    10.8,
    12.0,
    11.3,
    11.2,
    14.4,
    10.3,
    13.7
]
ss_to_rr_mass_scale = 0.8

# Empirical Mature data
# TODO: Fill these in with proper data points
mu_0_mature_ss  = 100
sig_0_mature_ss = 10
mu_0_mature_rr  = 100
sig_0_mature_rr = 10


# Egg development Sparks 1979
mu_egg_dev  = 3.0
sig_egg_dev = 1.0

# Pitre and Hogg 1983 (Pupation duration)
pupa_duration_pitre_1983 = [
    9.0,
    10.8,
    9.6
]
# Adamczyk 2001 (Pupation duration)
pupa_duration_adamczyk_2001 = [
    8.43,
    7.88,
    8.25,
    7.29,
    8.05,
    7.20
]
pupa_duration = pupa_duration_pitre_1983 + pupa_duration_adamczyk_2001
