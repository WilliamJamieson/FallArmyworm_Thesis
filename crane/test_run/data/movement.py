import data.input_data as input_data

import source.movement.models as models


# Generate the input models
#       larva_movement
larva_loc   = input_data.larva_move_loc
larva_scale = input_data.larva_move_scale
larva_shape = input_data.larva_move_shape

larva_movement = models.Larva(larva_loc,
                              larva_scale,
                              larva_shape)
#      adult_movement
adult_loc   = input_data.adult_move_loc
adult_scale = input_data.adult_move_scale
adult_shape = input_data.adult_move_shape

adult_movement = models.Adult(adult_loc,
                              adult_scale,
                              adult_shape)
