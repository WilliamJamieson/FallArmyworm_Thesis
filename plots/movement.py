import datetime
import dataclasses       as dclass
import numpy             as np
import matplotlib.pyplot as plt

import data.biomass       as input_biomass
import data.data_tracking as input_tracking
import data.graph         as input_graph
import data.movement      as input_move
import data.reproduction  as input_repro

import source.hint    as hint
import source.keyword as keyword

import source.simulation.simulation as main_simulation


# Plotting parameters
num_steps  = 15
num_larvae = 1
num_adults = 1
save_fig   = False


width  = 0.5
length = 0.5
colors = ['b', 'r', 'k']


sex_model = input_repro.init_sex
sex_model.prob = 1.0


@dclass.dataclass
class Simulator(object):
    """
    Class to setup and run a simulation of only biomass growth:

    Variables:
        nums:   initial population numbers
        forage: the plant forage model
    """

    # grid        = [(keyword.hexagon, 1, 1, True),
    #                (keyword.hexagon, 1, 1, True)]
    attrs       = {1: input_tracking.genotype_attrs,
                   2: input_tracking.genotype_attrs}
    data        = (np.inf,)
    steps       = [({keyword.larva:  [keyword.move],
                     keyword.female: [keyword.move]},)]
    emigration  = []
    immigration = []

    input_models = [input_biomass.max_gut,
                    input_biomass.growth,
                    input_biomass.init_num,
                    input_biomass.init_mass,
                    input_biomass.init_juvenile,
                    input_biomass.init_mature,
                    input_biomass.init_plant,
                    input_move.larva_movement,
                    input_move.adult_movement,
                    sex_model]
    input_variables = input_repro.values

    nums:       hint.init_pops
    grid:       hint.grid_generators
    bt_prop:    float
    simulation: hint.simulation = None

    def __post_init__(self):

        self.simulation = main_simulation.Simulation. \
            setup(self.nums,
                  self.grid,
                  self.attrs,
                  self.data,
                  self.bt_prop,
                  self.steps,
                  self.emigration,
                  self.immigration,
                  *self.input_models,
                  **self.input_variables)

    def collect(self) -> tuple:
        """
        Collect a list of locations

        Returns:
            tuple of locations
        """

        larvae = self.simulation.agents.agents(keyword.larva)
        adults = self.simulation.agents.agents(keyword.female)

        larvae_values = []
        for agent in larvae:
            larvae_values.append(agent.location.copy())

        adult_values = []
        for agent in adults:
            adult_values.append(agent.location.copy())

        return larvae_values, adult_values

    def run(self, times: list) -> tuple:
        """
        Run the simulation for each time

        Args:
            times: the times for the simulation

        Returns:
            biomass data
        """

        larva, adult = self.collect()
        larvae = [larva]
        adults = [adult]

        for time in times[1:]:
            print('     {} Running step: {}'.
                  format(datetime.datetime.now(), time))
            self.simulation.step()
            new_larva, new_adult = self.collect()
            larvae.append(new_larva)
            adults.append(new_adult)

        return larvae, adults


def convert_vertex(vertex: int,
                   side:   int) -> tuple:
    """
    Convert vertex in grid with side to ordered pair
    Args:
        vertex: vertex of grid
        side:   number of vertices on a side for grid

    Returns:
        (x, y) point
    """

    return vertex // side, vertex % side


def convert_location(location: hint.location,
                     side_p:   int,
                     side_l:   int) -> tuple:
    """
    Convert the location to a collection of ordered pairs
    Args:
        location: the location in question
        side_p:   grid side of plant grid
        side_l:   grid side of leaf  grid

    Returns:
        ordered pairs
    """

    plant_vertex = location[keyword.plant_level]
    plant_loc    = convert_vertex(plant_vertex, side_p)

    if location.depth > 2:
        leaf_vertex = location[keyword.leaf_level]
        leaf_loc    = convert_vertex(leaf_vertex, side_l)
    else:
        leaf_loc = ()

    return plant_loc, leaf_loc


def convert_xy_location(locations: hint.locations,
                        side_p:    int,
                        side_l:    int) -> tuple:
    """
    Convert a list of locations of locations to ordered pairs

    Args:
        locations: list of locations
        side_p:    grid side of plant grid
        side_l:    grid side of leaf  grid

    Returns:
        (plant_locs, leaf_locs)
    """

    plant_locs = []
    leaf_locs  = []

    for location in locations:
        plant_loc, leaf_loc = convert_location(location, side_p, side_l)
        plant_locs.append(plant_loc)
        leaf_locs.append(leaf_loc)

    return plant_locs, leaf_locs


def convert_xy_arrow(xy_data: list) -> list:
    """
    Convert a list of xy points to a list of arrow stuff
    Args:
        xy_data: list of xy points

    Returns:
        list of arrow tuples
    """

    arrows = []
    for index in range(len(xy_data) - 1):
        start = xy_data[index]
        end   = xy_data[index + 1]

        if len(start) < 2:
            break
        else:
            arrow = (start[0],
                     start[1],
                     end[0] - start[0],
                     end[1] - start[1])
            arrows.append(arrow)

    return arrows


def convert_arrow(locations: hint.locations,
                  side_p:    int,
                  side_l:    int) -> tuple:
    """
    Convert the locations to arrow data
    Args:
        locations: list of locations
        side_p:    grid side of plant grid
        side_l:    grid side of leaf  grid

    Returns:
        (plant_arrows, leaf_arrows)
    """

    plant_locations, leaf_locations = convert_xy_location(locations,
                                                          side_p,
                                                          side_l)
    plant_arrows = convert_xy_arrow(plant_locations)
    leaf_arrows  = convert_xy_arrow(leaf_locations)

    return plant_arrows, leaf_arrows


def invert_data(location_data: list,
                num_agents:    int) -> list:
    """
    Location data is List[List[loc data per agent] per step]
    Args:
        location_data: location data Lis
        num_agents:    number of agents in each step

    Returns:
        List[List[loc data per step] per agent]
    """

    data = []
    for index_agent in range(num_agents):
        data_agent = []
        for index_location in range(len(location_data)):
            data_agent.append(location_data[index_location][index_agent])
        data.append(data_agent)

    return data


def convert(location_data: list,
            num_agents:    int,
            side_p:        int,
            side_l:        int) -> tuple:
    """
    Convert location data into arrow data
    Args:
        location_data: location data List[List[locs for agents at step]]
        num_agents:    number of agents in each step
        side_p:        grid side of plant grid
        side_l:        grid side of leaf  grid

    Returns:
        List[plant_arrows by agent], List[leaf_arrows by agent
    """

    new_data = invert_data(location_data, num_agents)
    plant_arrows  = []
    leaf_arrows   = []
    for agent_data in new_data:
        plant_arrow, leaf_arrow = convert_arrow(agent_data, side_p, side_l)
        plant_arrows.append(plant_arrow)
        leaf_arrows.append(leaf_arrow)

    return plant_arrows, leaf_arrows


t            = list(range(num_steps))
initial_pops = ((0,          0,          0),
                (num_larvae, num_larvae, num_larvae),
                (0,          0,          0),
                (0,          0,          0),
                (0,          0,          0))
grid         = [(keyword.hexagon, 1, 1, True),
                input_graph.graph(25)]
simulator_larva_bt = Simulator(initial_pops, grid, 1)
larva_bt, adult_bt = simulator_larva_bt.run(t)

larva_plant, larva_leaf = convert(larva_bt, 3*num_larvae, 1, 25)
# Plot
plt.figure()
plt.xlim((-1, 25))
plt.ylim((-1, 25))
#   Plot Data
plot_arrows  = []
legend_names = []
for agent_index in range(3*num_larvae):
    points = larva_leaf[agent_index].copy()
    point  = points.pop(0)
    legend_name = 'Larva {}'.format(agent_index)
    plot_arrow = plt.arrow(point[0],
                           point[1],
                           point[2],
                           point[3],
                           head_width=width,
                           head_length=length,
                           length_includes_head=True,
                           color=colors[agent_index],
                           label=legend_name)
    plot_arrows.append(plot_arrow)
    legend_names.append(legend_name)
    for point in points:
        plt.arrow(point[0], point[1], point[2], point[3],
                               head_width=width,
                               head_length=length,
                               length_includes_head=True,
                               color=colors[agent_index])

plt.legend(plot_arrows, legend_names)
plt.xlabel('distance (cm)')
plt.ylabel('distance (cm)')
plt.title('Larva Movement on a Plant')
#   Show/save plot
if save_fig:
    plt.savefig('larva_movement.png')
plt.show()

initial_pops = ((0,          0,          0),
                (0,          0,          0),
                (0,          0,          0),
                (0,          0,          0),
                (num_adults, num_adults, num_adults))
grid         = [input_graph.graph(25),
                (keyword.hexagon, 1, 1, True)]
simulator_adult_bt = Simulator(initial_pops, grid, 1)
larva_bt, adult_bt = simulator_adult_bt.run(t)

adult_plant, adult_leaf = convert(adult_bt, 3*num_adults, 25, 1)
# Plot
plt.figure()
plt.xlim((-1, 25))
plt.ylim((-1, 25))
#   Plot Data
plot_arrows  = []
legend_names = []
for agent_index in range(3*num_adults):
    points = adult_plant[agent_index].copy()
    point  = points.pop(0)
    legend_name = 'Adult {}'.format(agent_index)
    plot_arrow = plt.arrow(point[0],
                           point[1],
                           point[2],
                           point[3],
                           head_width=width,
                           head_length=length,
                           length_includes_head=True,
                           color=colors[agent_index],
                           label=legend_name)
    plot_arrows.append(plot_arrow)
    legend_names.append(legend_name)
    for point in points:
        plt.arrow(point[0], point[1], point[2], point[3],
                  head_width=width,
                  head_length=length,
                  length_includes_head=True,
                  color=colors[agent_index])

plt.legend(plot_arrows, legend_names)
plt.xlabel('distance (m)')
plt.ylabel('distance (m)')
plt.title('Adult Movement on in a Field')
#   Show/save plot
if save_fig:
    plt.savefig('adult_movement.png')
plt.show()
