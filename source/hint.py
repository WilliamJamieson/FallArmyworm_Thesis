import typing

import pandas as pd

if typing.TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    import source.agents.agent    as main_agent
    # noinspection PyUnresolvedReferences
    import source.agents.adult    as main_adult
    # noinspection PyUnresolvedReferences
    import source.agents.egg      as main_egg
    # noinspection PyUnresolvedReferences
    import source.agents.egg_mass as main_egg_mass
    # noinspection PyUnresolvedReferences
    import source.agents.larva    as main_larva
    # noinspection PyUnresolvedReferences
    import source.agents.pupa     as main_pupa

    # noinspection PyUnresolvedReferences
    import source.biomass.gut  as main_gut
    # noinspection PyUnresolvedReferences
    import source.biomass.mass as main_mass

    # noinspection PyUnresolvedReferences
    import source.data.database as main_database
    # noinspection PyUnresolvedReferences
    import source.data.counter  as main_counter

    # noinspection PyUnresolvedReferences
    import source.development.egg   as main_egg_development
    # noinspection PyUnresolvedReferences
    import source.development.larva as main_larva_development
    # noinspection PyUnresolvedReferences
    import source.development.pupa  as main_pupa_development

    # noinspection PyUnresolvedReferences
    import source.forage.cannibalism as main_cannibalism
    # noinspection PyUnresolvedReferences
    import source.forage.egg         as main_egg_forage
    # noinspection PyUnresolvedReferences
    import source.forage.larva       as main_larva_forage
    # noinspection PyUnresolvedReferences
    import source.forage.plant       as main_plant_forage
    # noinspection PyUnresolvedReferences
    import source.forage.target      as main_target

    # noinspection PyUnresolvedReferences
    import source.migration.emigration  as main_emigration
    # noinspection PyUnresolvedReferences
    import source.migration.immigration as main_immigration

    # noinspection PyUnresolvedReferences
    import source.movement.adult as main_adult_movement
    # noinspection PyUnresolvedReferences
    import source.movement.larva as main_larva_movement

    # noinspection PyUnresolvedReferences
    import source.schedule.actions  as main_actions
    # noinspection PyUnresolvedReferences
    import source.schedule.schedule as main_schedule
    # noinspection PyUnresolvedReferences
    import source.schedule.step     as main_step

    # noinspection PyUnresolvedReferences
    import source.reproduction.lay  as main_lay
    # noinspection PyUnresolvedReferences
    import source.reproduction.mate as main_mate

    # noinspection PyUnresolvedReferences
    import source.simulation.behaviors  as main_behaviors
    # noinspection PyUnresolvedReferences
    import source.simulation.models     as main_models
    # noinspection PyUnresolvedReferences
    import source.simulation.simulation as main_simulation

    # noinspection PyUnresolvedReferences
    import source.space.agents      as main_agents
    # noinspection PyUnresolvedReferences
    import source.space.environment as main_environment
    # noinspection PyUnresolvedReferences
    import source.space.graph       as main_graph
    # noinspection PyUnresolvedReferences
    import source.space.location    as main_location
    # noinspection PyUnresolvedReferences
    import source.space.space       as main_space

    # noinspection PyUnresolvedReferences
    import source.survival.adult as main_adult_survival
    # noinspection PyUnresolvedReferences
    import source.survival.egg   as main_egg_survival
    # noinspection PyUnresolvedReferences
    import source.survival.larva as main_larva_survival
    # noinspection PyUnresolvedReferences
    import source.survival.pupa  as main_pupa_survival

# Agent hints
agent      = 'main_agent.Agent'
agent_list = typing.List[agent]
agent_dict = typing.Dict[str, agent]
#
# agent_dict = typing.Dict[int, agent]

egg      = 'main_egg.Egg'
egg_mass = 'main_egg_mass.EggMass'
larva    = 'main_larva.Larva'
pupa     = 'main_pupa.Pupa'
adult    = 'main_adult.Adult'

egg_mass_eggs = 'main_egg_mass.Eggs'
egg_masses    = typing.List[egg_mass]

genotypes = typing.List[str]
eggs      = typing.List[egg]

egg_dict = typing.Dict[str, egg]

alleles = typing.Tuple[int, int]


# Space hints
#       Location hints
sim_key       = typing.Tuple[int]
plant_key     = typing.Tuple[int, int]
leaf_key      = typing.Tuple[int, int, int]
location_key  = typing.Union[sim_key, plant_key, leaf_key]
location_keys = typing.List[location_key]
locations_key = typing.Dict[int, location_keys]

locs      = typing.List[int]
location  = 'main_location.Location'
locations = typing.List[location]

location_pairs = typing.Tuple[locations, location_keys]
location_data  = typing.Tuple[locations, locations_key]

#       Environment hints
init_plant  = typing.Callable[[str], float]
environment = 'main_environment.Environment'

environment_tuple = typing.Tuple[float, init_plant]

#       Agents hints
agent_keys  = typing.List[str]
agent_bin   = 'main_agents.AgentBin'
agent_bins  = typing.Dict[str, agent_bin]
agents_bin  = 'main_agents.AgentsBin'
agents_dict = typing.Dict[location_key, agents_bin]
agents      = 'main_agents.Agents'

#       Graph hints
vertex_neighborhood = 'main_graph.VertexNeighborhood'
vertex_distance     = 'main_graph.VertexDistance'

graph_neighborhood = 'main_graph.GraphNeighborhood'
graph_distance     = 'main_graph.GraphDistance'
graph_adjacency    = 'main_graph.Adjacency'
graph              = 'main_graph.Graph'

vertices      = typing.Set[int]
upper_lower   = typing.Tuple[float, float]
distance_pair = typing.Tuple[int, float]

neighborhood_dict = typing.Dict[float, vertices]
neighborhoods     = typing.Dict[int,   vertex_neighborhood]

distance_dict = typing.Dict[int, float]
distances     = typing.Dict[int, vertex_distance]

upper_grid = typing.List[typing.List[int]]
boundary   = typing.Tuple[typing.List[int],
                          typing.List[int],
                          typing.List[int],
                          typing.List[int]]

#       Space hints
graphs = typing.List[graph]

grid_regular_grid_generator  = typing.Tuple[str, int, int, bool]
grid_parallel_grid_generator = typing.Tuple[str, int, int, bool, bool]
grid_generator               = typing.Union[grid_regular_grid_generator,
                                            grid_parallel_grid_generator]
grid_gen                     = typing.Union[graph, grid_generator]
grid_generators              = typing.List[grid_gen]

space = 'main_space.Space'


# Data hints
#       Database Hints
database   = 'main_database.Database'
data_tuple_spacing = typing.Tuple[int]
data_tuple_name    = typing.Tuple[int, str, str]
data_tuple         = typing.Union[data_tuple_spacing, data_tuple_name]
#       Counter Hints
dataframe      = pd.DataFrame
dataframes     = typing.Dict[str, dataframe]
dataframe_list = typing.List[dataframe]

data_list        = typing.List[int]
data_column      = 'main_counter.DataColumn'
data_column_dict = typing.Dict[str, data_column]
data_columns     = 'main_counter.DataColumns'

counts_dict  = typing.Dict[str, any]
count_dict   = typing.Dict[str, int]
attr_values  = typing.List[str]
attrs        = typing.Dict[str, typing.Tuple[attr_values, bool]]
counter      = 'main_counter.Count'
count_filter = 'main_counter.CountFilter'
counting     = typing.Union[counter, count_filter]
counter_dict = typing.Dict[str, counting]
attr_other   = typing.Union[attrs, bool]
counts       = 'main_counter.Counts'

attr_filter = typing.Tuple[str, attr_values, attr_other]

attrs_dict  = typing.Dict[str, attr_filter]
attrs_depth = typing.Dict[int, attrs_dict]


# Schedule hints
#       Actions hints
action_keys = typing.List[str]
action      = 'main_actions.Action'
action_list = typing.List[action]

actions      = 'main_actions.Actions'
actions_list = typing.List[actions]
actions_dict = typing.Dict[str, action_keys]

#       Step hints
step  = 'main_step.Step'
steps = typing.List[step]

step_tuple_basic     = typing.Tuple[actions_dict]
step_tuple_repeat    = typing.Tuple[actions_dict, int]
step_tuple_shuffle_0 = typing.Tuple[actions_dict, int, bool]
step_tuple_shuffle_1 = typing.Tuple[actions_dict, int, bool, bool]
step_tuple_reg       = typing.Tuple[actions_dict, int, bool, bool, bool]
step_tuple_loc       = typing.Tuple[actions_dict, int, bool, bool, bool,
                                    bool, int]
step_tuple           = typing.Union[step_tuple_basic,
                                    step_tuple_repeat,
                                    step_tuple_shuffle_0,
                                    step_tuple_shuffle_1,
                                    step_tuple_reg,
                                    step_tuple_loc]
step_tuples           = typing.List[step_tuple]

#       Schedule hints
schedule = 'main_schedule.Schedule'


# Simulation Hints
simulation = 'main_simulation.Simulation'
model      = 'main_models.Model'
models     = 'main_models.Models'
behaviors  = 'main_behaviors.Behaviors'

init_pop  = typing.Tuple[int, int, int]
init_pops = typing.Tuple[init_pop, init_pop, init_pop, init_pop, init_pop]

variable    = typing.Dict[str, float]
bt_variable = typing.Dict[str, variable]


# Biomass Hints
#       Gut Hints
max_gut      = typing.Callable[[float], float]
amount_tuple = typing.Tuple[float, bool]
gut          = 'main_gut.Gut'
#       Mass Hints
growth = typing.Callable[[float, float, str], float]
mass   = 'main_mass.Mass'


# Survival Hints
survival_egg   = typing.Callable[[float, str, str], bool]
survival_larva = typing.Callable[[float, str, str], bool]
survival_pupa  = typing.Callable[[float, str], bool]
survival_adult = typing.Callable[[float, str], bool]

egg_survival   = 'main_egg_survival.Egg'
larva_survival = 'main_larva_survival.Larva'
pupa_survival  = 'main_pupa_survival.Pupa'
adult_survival = 'main_adult_survival.Adult'


# Development Hints
development_egg   = typing.Callable[[float, int, str], bool]
development_larva = typing.Callable[[float, int, str], bool]
development_pupa  = typing.Callable[[float, int, str], bool]

egg_development   = 'main_egg_development.Egg'
larva_development = 'main_larva_development.Larva'
pupa_development  = 'main_pupa_development.Pupa'


# Movement Hints
movement_larva = typing.Callable[[float, str], float]
movement_adult = typing.Callable[[float, str], float]

larva_movement = 'main_larva_movement.Larva'
adult_movement = 'main_adult_movement.Adult'


# Forage Hints
#       Foraging Hints
forage_plant = typing.Callable[[float, float, str, str], float]
forage_egg   = typing.Callable[[float, float, str],      float]
forage_larva = typing.Callable[[float, float, str],      float]
loss         = typing.Callable[[float, float, str, str], bool]

plant_forage = 'main_plant_forage.Plant'
egg_forage   = 'main_egg_forage.Egg'
larva_forage = 'main_larva_forage.Larva'
target_loss  = 'main_target.Target'

#       Cannibalism Hints
target    = typing.Union[egg_mass, larva]
targets   = typing.List[target]

fight     = typing.Callable[[float, float], bool]
encounter = typing.Callable[[int, float, str], bool]
radius    = typing.Callable[[float, str], bool]

cannibalism = 'main_cannibalism.Cannibalism'


# Reproduction Hints
#       Lay Hints
fecundity = typing.Callable[[float, int, str], int]
density   = typing.Callable[[int, float, str], bool]

egg_lay = typing.Tuple[egg_masses, int, bool]

lay = 'main_lay.Lay'

#       Mate Hints
mates = typing.List[adult]

mating      = typing.Callable[[int, float, str], bool]
mate_radius = typing.Callable[[float, str], bool]

adult_mate = typing.Union[str, None]

mate = 'main_mate.Mate'


# Migration Hints
emigration        = 'main_emigration.Emigration'
emigration_list   = typing.List[emigration]
emigrations       = 'main_emigration.Emigrations'
emigration_tuple  = typing.Tuple[float, float, agent_keys]
emigration_tuples = typing.List[emigration_tuple]

immigration        = 'main_immigration.Immigration'
immigration_list   = typing.List[immigration]
immigrations       = 'main_immigration.Immigrations'
immigration_tuple  = typing.Tuple[float, str, str]
immigration_tuples = typing.List[immigration_tuple]
