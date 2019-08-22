import data.input_data as input_data
import data.biomass    as biomass

import source.forage.models as models


# Generate the input models
#       plant_ad_libitum
ad_libitum = models.PlantAdLibitum(biomass.max_gut)
#       plant_starve
starve_mu    = input_data.starvation_mu
starve_sigma = input_data.starvation_sigma

starve = models.PlantStarve(starve_mu,
                            starve_sigma)
#       egg_forage
egg_factor = input_data.egg_factor

egg_forage = models.Egg(egg_factor)
#       larva_forage
larva_factor = input_data.larva_factor

larva_forage = models.Larva(larva_factor)

#       fight
fight_slope = input_data.fight_steepness

fight = models.Fight(fight_slope)

#       encounter
encounter_factor = input_data.cannibalism_encounter

encounter = models.Encounter(encounter_factor)

#       radius
rad = input_data.cannibalism_radius

radius = models.Radius(rad)
