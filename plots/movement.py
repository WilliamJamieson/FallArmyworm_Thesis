import datetime
import dataclasses       as dclass
import numpy             as np

import bokeh.plotting as plt
import bokeh.models   as mdl
import bokeh.palettes as palettes

import parameters.data_tracking    as tracking
import parameters.model_parameters as param

import models.graph        as graph
import models.growth       as growth
import models.init_biomass as init_bio
import models.movement     as move
import models.reproduction as repro

import source.hint    as hint
import source.keyword as keyword

import source.simulation.simulation as main_simulation


# Plotting parameters
larva_grid = 25
adult_grid = 50

dominance  = 0
num_steps  = param.forage_steps
num_larvae = 2
num_adults = 2
save_fig   = True


line_width       = 2
point_size       = 10
point_size_stoch = 8

axis_line_width     = 2
grid_line_width     = 2
title_font_size     = '16pt'
legend_font_size    = '12pt'
axis_font_size      = '12pt'
axis_tick_font_size = '10pt'

plot_width  = 800
plot_height = 500

colors    = palettes.Colorblind[8]
save_file = 'move_plots.html'


sex_model = repro.init_sex(1)


@dclass.dataclass
class Simulator(object):
    """
    Class to setup and run a simulation of only biomass growth:

    Variables:
        nums:   initial population numbers
        forage: the plant forage model
    """

    attrs       = {1: tracking.genotype_attrs,
                   2: tracking.genotype_attrs}
    data        = (np.inf,)
    steps       = [({keyword.larva:  [keyword.move],
                     keyword.female: [keyword.move]},)]
    emigration  = []
    immigration = []

    input_models = [growth.max_gut(),
                    growth.growth(param.alpha_ss,
                                  param.alpha_rr,
                                  param.beta_ss,
                                  param.beta_rr,
                                  dominance),
                    init_bio.init_num(param.lam_0_egg),
                    init_bio.init_mass(param.mu_0_egg_ss,
                                       param.mu_0_egg_rr,
                                       param.sig_0_egg_ss,
                                       param.sig_0_egg_rr,
                                       dominance),
                    init_bio.init_juvenile(param.mu_0_larva_ss,
                                           param.mu_0_larva_rr,
                                           param.sig_0_larva_ss,
                                           param.sig_0_larva_rr,
                                           dominance),
                    init_bio.init_mature(param.mu_0_mature_ss,
                                         param.mu_0_mature_rr,
                                         param.sig_0_mature_ss,
                                         param.sig_0_mature_rr,
                                         dominance),
                    init_bio.init_plant(param.mu_leaf,
                                        param.sig_leaf),
                    sex_model,
                    move.larva(param.larva_scale,
                               param.larva_shape),
                    move.adult(param.adult_scale,
                               param.adult_shape)]
    input_variables = param.repro_values

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
        plant_arrow, leaf_arrow = convert_xy_location(agent_data, side_p, side_l)
        plant_arrows.append(plant_arrow)
        leaf_arrows.append(leaf_arrow)

    return plant_arrows, leaf_arrows


t            = list(range(num_steps))
print('Running Larva')
initial_pops = ((0,          0,          0),
                (num_larvae, num_larvae, num_larvae),
                (0,          0,          0),
                (0,          0,          0),
                (0,          0,          0))
grid         = [(keyword.hexagon, 1, 1, True),
                graph.graph(larva_grid)]
simulator_larva = Simulator(initial_pops, grid, 1)
larva_larva, adult_larva = simulator_larva.run(t)

larva_plant, larva_leaf = convert(larva_larva, 3*num_larvae, 1, larva_grid)


plt.output_file('larva_' + save_file)
larva_plot = plt.figure(plot_width=plot_width,
                        plot_height=plot_height,
                        x_range=(0, larva_grid),
                        y_range=(0, larva_grid))
larva_plot.title.text = 'Larva Movement, ' \
                        '(x_m={}, a={})'.format(param.larva_scale,
                                                param.larva_shape)
larva_plot.yaxis.axis_label = 'distance (~cm)'
larva_plot.xaxis.axis_label = 'distance (~cm)'

larva_legend_items = []
for agent_index in range(3*num_larvae):
    points = larva_leaf[agent_index].copy()

    start_point = points.pop(0)
    larva_circle = larva_plot.circle([[start_point[0]]], [[start_point[1]]],
                                     color=colors[agent_index], size=10)
    larva_legend_items.append(('Larva {}'.format(agent_index), [larva_circle]))

    for end_point in points:
        larva_arrow = mdl.Arrow(end=mdl.VeeHead(fill_color=colors[agent_index],
                                                line_color=colors[agent_index],
                                                size=10),
                                line_color=colors[agent_index],
                                line_width=line_width,
                                x_start=start_point[0], y_start=start_point[1],
                                x_end=end_point[0], y_end=end_point[1])
        larva_plot.add_layout(larva_arrow)

        start_point = end_point

larva_legend = mdl.Legend(items=larva_legend_items, location='top_right')
larva_plot.add_layout(larva_legend, 'right')

larva_plot.title.text_font_size = title_font_size
larva_plot.legend.label_text_font_size = legend_font_size
larva_plot.yaxis.axis_line_width = axis_line_width
larva_plot.xaxis.axis_line_width = axis_line_width
larva_plot.yaxis.axis_label_text_font_size = axis_font_size
larva_plot.xaxis.axis_label_text_font_size = axis_font_size
larva_plot.yaxis.major_label_text_font_size = axis_tick_font_size
larva_plot.xaxis.major_label_text_font_size = axis_tick_font_size
larva_plot.ygrid.grid_line_width = grid_line_width
larva_plot.xgrid.grid_line_width = grid_line_width


plt.show(larva_plot)


plt.output_file('adult_' + save_file)
print('Running Adult')
initial_pops = ((0,          0,          0),
                (0,          0,          0),
                (0,          0,          0),
                (0,          0,          0),
                (num_adults, num_adults, num_adults))
grid         = [graph.graph(adult_grid),
                (keyword.hexagon, 1, 1, True)]
simulator_adult = Simulator(initial_pops, grid, 1)
larva_adult, adult_adult = simulator_adult.run(t)

adult_plant, adult_leaf = convert(adult_adult, 3*num_adults, adult_grid, 1)


adult_plot = plt.figure(plot_width=plot_width,
                        plot_height=plot_height,
                        x_range=(0, adult_grid),
                        y_range=(0, adult_grid))
adult_plot.title.text = 'Adult Movement, ' \
                        '(x_m={}, a={})'.format(param.adult_shape,
                                                param.adult_scale)
adult_plot.yaxis.axis_label = 'distance (~m)'
adult_plot.xaxis.axis_label = 'distance (~m)'

adult_legend_items = []
for agent_index in range(3*num_adults):
    points = adult_plant[agent_index].copy()

    start_point = points.pop(0)
    adult_circle = adult_plot.circle([[start_point[0]]], [[start_point[1]]],
                                     color=colors[agent_index], size=10)
    adult_legend_items.append(('Adult {}'.format(agent_index), [adult_circle]))

    for end_point in points:
        adult_arrow = mdl.Arrow(end=mdl.VeeHead(fill_color=colors[agent_index],
                                                line_color=colors[agent_index],
                                                size=10),
                                line_color=colors[agent_index],
                                line_width=line_width,
                                x_start=start_point[0], y_start=start_point[1],
                                x_end=end_point[0], y_end=end_point[1])
        adult_plot.add_layout(adult_arrow)

        start_point = end_point

adult_legend = mdl.Legend(items=adult_legend_items, location='top_right')
adult_plot.add_layout(adult_legend, 'right')

adult_plot.title.text_font_size = title_font_size
adult_plot.legend.label_text_font_size = legend_font_size
adult_plot.yaxis.axis_line_width = axis_line_width
adult_plot.xaxis.axis_line_width = axis_line_width
adult_plot.yaxis.axis_label_text_font_size = axis_font_size
adult_plot.xaxis.axis_label_text_font_size = axis_font_size
adult_plot.yaxis.major_label_text_font_size = axis_tick_font_size
adult_plot.xaxis.major_label_text_font_size = axis_tick_font_size
adult_plot.ygrid.grid_line_width = grid_line_width
adult_plot.xgrid.grid_line_width = grid_line_width


plt.show(adult_plot)
