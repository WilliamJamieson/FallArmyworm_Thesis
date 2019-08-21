# Agent_keys
egg      = 'egg'
egg_mass = 'eggMass'
larva    = 'larva'
pupa     = 'pupa'
female   = 'female'
male     = 'male'
mated    = 'mated'

agent_keys = [egg, egg_mass, larva, pupa, female, male]

adult    = 'adult'
pregnant = 'pregnant'

# Initialization keys
init      = 'init'
immigrant = 'immigrant'

# upper_lower keys
upper = 'upper'
lower = 'lower'


# Genotype Keywords
homo_r = 'resistant'
hetero = 'heterozygous'
homo_s = 'susceptible'

genotype_keys = [homo_r, hetero, homo_s]

homo_r_value = 0
hetero_value = 1
homo_s_value = 2

homo_r_allele = 0
homo_s_allele = 1

homo_r_alleles = (homo_r_allele, homo_r_allele)
hetero_alleles = (homo_r_allele, homo_s_allele)
homo_s_alleles = (homo_s_allele, homo_s_allele)

# bt keys
bt     = 'Bt'
not_bt = 'not_Bt'
plant  = 'plant'

# level
egg_level      = 2
egg_mass_level = 2
larva_level    = 2
pupa_level     = 1
adult_level    = 1
bt_level       = 1
plant_level    = 1

# depth
egg_depth      = 3
egg_mass_depth = 3
larva_depth    = 3
pupa_depth     = 2
adult_depth    = 2
bt_depth       = 2
plant_depth    = 2

# grid_keys
hexagon  = 'hexagon'
square   = 'square'
moore    = 'moore'
triangle = 'triangle'

# death_keys
cannibalism = 'cannibalism'
emigrate    = 'emigrate'
survival    = 'survival'
starve      = 'starve'
alive       = 'alive'

# mathematical model keys
max_gut = 'max_gut'
growth  = 'growth'

init_num      = 'init_num'
init_mass     = 'init_mass'
init_juvenile = 'init_juvenile'
init_mature   = 'init_mature'
init_sex      = 'init_sex'
init_plant    = 'init_plant'

egg_development   = 'egg_development'
larva_development = 'larva_development'
pupa_development  = 'pupa_development'

egg_survival   = 'egg_survival'
larva_survival = 'larva_survival'
pupa_survival  = 'pupa_survival'
adult_survival = 'adult_survival'

larva_movement = 'larva_movement'
adult_movement = 'adult_movement'

egg_forage   = 'egg_forage'
larva_forage = 'larva_forage'
plant_forage = 'plant_forage'

fight     = 'fight'
encounter = 'encounter'
radius    = 'radius'

trials    = 'trials'
fecundity = 'fecundity'
density   = 'density'

mating      = 'mating'
mate_radius = 'mate_radius'

lifetime_male   = 'lifetime_male'
lifetime_female = 'lifetime_female'
limited         = 'limited'

required_inputs = [max_gut, growth, lifetime_male, lifetime_female, limited,
                   init_mass, init_mature, init_sex]

# Behavior_keys
survival_egg   = 'survival_egg'
survival_larva = 'survival_larva'
survival_pupa  = 'survival_pupa'
survival_adult = 'survival_adult'

movement_larva = 'movement_larva'
movement_adult = 'movement_adult'

forage_egg   = 'forage_egg'
forage_larva = 'forage_larva'
forage_plant = 'forage_plant'

cannibal = 'cannibal'

lay_eggs = 'lay_eggs'
mate     = 'mate'
