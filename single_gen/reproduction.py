import datetime
import dataclasses as dclass
import numpy       as np

import bokeh.plotting as plt
import bokeh.layouts  as lay
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
dominance = 0
trials    = 2

num_steps_density = 5

line_width       = 3.5
point_size       = 6
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
save_file = 'reproduction_plots.html'


@dclass.dataclass
class Simulator(object):
    """
    Class to setup and run a simulation of only biomass growth:

    Variables:
        nums:    initial population numbers
        bt_prop: bt proportion
    """

    attrs       = {0: tracking.genotype_attrs}
    data        = (np.inf,)
    steps       = [({keyword.female: [keyword.move,
                                      keyword.reproduce],
                     keyword.male:   [keyword.move]}, param.forage_steps),
                   ({keyword.female: [keyword.advance_age,
                                      keyword.reset],
                     keyword.male:   [keyword.advance_age,
                                      keyword.reset]},)]
    emigration  = []
    immigration = []

    input_variables = param.repro_values

    nums:           hint.init_pops
    bt_prop:        float
    mate_encounter: float
    mate_radius:    float
    field_grid:     int
    plant_grid:     int
    simulation: hint.simulation = None

    def __post_init__(self):
        inputs = self.input_models(self.mate_encounter, self.mate_radius)
        inputs = tuple(inputs)

        grid = self.grid(self.field_grid,
                         self.plant_grid)

        self.simulation = main_simulation.Simulation. \
            setup(self.nums,
                  grid,
                  self.attrs,
                  self.data,
                  self.bt_prop,
                  self.steps,
                  self.emigration,
                  self.immigration,
                  *inputs,
                  **self.input_variables)

    @staticmethod
    def grid(field_grid: int,
             plant_grid: int):
        """
        Create the grids

        Args:
            field_grid: field grid parameters
            plant_grid: plant grid parameters

        Returns:
            grid setup
        """
        return [
            graph.graph(field_grid),
            graph.graph(plant_grid)
        ]

    @staticmethod
    def input_models(mate_encounter: float,
                     mate_radius: float):
        """
        Create all the input models

        Args:
            mate_encounter: mate encounter constant
            mate_radius:    mate radius

        Returns:
            input models
        """

        return [
            growth.max_gut(),
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
            move.adult(param.adult_scale,
                       param.adult_shape),
            repro.mating(mate_encounter),
            repro.radius(mate_radius),
            repro.fecundity(param.fecundity_maximum,
                            param.fecundity_decay),
            repro.density(param.eta,
                          param.gamma),
            repro.init_sex(param.female_prob)
        ]

    def collect(self) -> int:
        """
        Get the number of egg masses

        Returns:
            the number of egg masses
        """

        egg_masses = self.simulation.agents.agents(keyword.egg_mass)

        return len(egg_masses)

    def run(self, times: list) -> list:
        """
        Run the simulation for each time

        Args:
            times: the times for the simulation

        Returns:
            num egg_mass, densities
        """

        data = [self.collect()]
        for time in times[1:]:
            print('        {} Running step: {}'.
                  format(datetime.datetime.now(), time))
            self.simulation.step()
            data.append(self.collect())

        return data


t = list(range(num_steps_density))

grid_size  = [10,  25,  50]
adult_pops = [100, 500, 1000]

grid_data = []
for grid_value in grid_size:
    pop_data = []
    for num_adults in adult_pops:
        percent = 0.5
        rr_pop  = int(num_adults*percent)
        ss_pop  = int(num_adults*(1 - percent))
        initial_pops = ((0,      0, 0),
                        (0,      0, 0),
                        (0,      0, 0),
                        (rr_pop, 0, ss_pop),
                        (0,      0, 0))
        egg_data = []
        for num in range(trials):
            print('    {} Running Trial: {}'.format(datetime.datetime.now(),
                                                    num))
            simulator = Simulator(initial_pops, 1,
                                  param.mate_encounter,
                                  param.mate_radius,
                                  grid_value,
                                  1)
            egg_data.append(simulator.run(t))
        pop_data.append(np.mean(egg_data, axis=0))
    grid_data.append(pop_data)

grid_0_plot = plt.figure(plot_width=plot_width,
                         plot_height=plot_height)
grid_0_plot.title.text       = 'Reproduction, Grid Size: {}'.\
    format(grid_size[0])
grid_0_plot.yaxis.axis_label = 'egg_mass population'
grid_0_plot.xaxis.axis_label = 'time (days)'

grid_0_plot.line(t, grid_data[0][0],
                 color=colors[0], line_width=line_width,
                 legend='Adult Population: {}'.format(adult_pops[0]))

grid_0_plot.line(t, grid_data[0][1],
                 color=colors[1], line_width=line_width,
                 legend='Adult Population: {}'.format(adult_pops[1]))

grid_0_plot.line(t, grid_data[0][2],
                 color=colors[2], line_width=line_width,
                 legend='Adult Population: {}'.format(adult_pops[2]))

grid_0_plot.legend.location = 'top_right'

grid_0_plot.title.text_font_size = title_font_size
grid_0_plot.legend.label_text_font_size = legend_font_size
grid_0_plot.yaxis.axis_line_width = axis_line_width
grid_0_plot.xaxis.axis_line_width = axis_line_width
grid_0_plot.yaxis.axis_label_text_font_size = axis_font_size
grid_0_plot.xaxis.axis_label_text_font_size = axis_font_size
grid_0_plot.yaxis.major_label_text_font_size = axis_tick_font_size
grid_0_plot.xaxis.major_label_text_font_size = axis_tick_font_size
grid_0_plot.ygrid.grid_line_width = grid_line_width
grid_0_plot.xgrid.grid_line_width = grid_line_width

grid_1_plot = plt.figure(plot_width=plot_width,
                         plot_height=plot_height)
grid_1_plot.title.text       = 'Reproduction, Grid Size: {}'. \
    format(grid_size[1])
grid_1_plot.yaxis.axis_label = 'egg_mass population'
grid_1_plot.xaxis.axis_label = 'time (days)'

grid_1_plot.line(t, grid_data[1][0],
                 color=colors[0], line_width=line_width,
                 legend='Adult Population: {}'.format(adult_pops[0]))

grid_1_plot.line(t, grid_data[1][1],
                 color=colors[1], line_width=line_width,
                 legend='Adult Population: {}'.format(adult_pops[1]))

grid_1_plot.line(t, grid_data[1][2],
                 color=colors[2], line_width=line_width,
                 legend='Adult Population: {}'.format(adult_pops[2]))

grid_1_plot.legend.location = 'top_right'

grid_1_plot.title.text_font_size = title_font_size
grid_1_plot.legend.label_text_font_size = legend_font_size
grid_1_plot.yaxis.axis_line_width = axis_line_width
grid_1_plot.xaxis.axis_line_width = axis_line_width
grid_1_plot.yaxis.axis_label_text_font_size = axis_font_size
grid_1_plot.xaxis.axis_label_text_font_size = axis_font_size
grid_1_plot.yaxis.major_label_text_font_size = axis_tick_font_size
grid_1_plot.xaxis.major_label_text_font_size = axis_tick_font_size
grid_1_plot.ygrid.grid_line_width = grid_line_width
grid_1_plot.xgrid.grid_line_width = grid_line_width

grid_2_plot = plt.figure(plot_width=plot_width,
                         plot_height=plot_height)
grid_2_plot.title.text       = 'Reproduction, Grid Size: {}'. \
    format(grid_size[2])
grid_2_plot.yaxis.axis_label = 'egg_mass population'
grid_2_plot.xaxis.axis_label = 'time (days)'

grid_2_plot.line(t, grid_data[2][0],
                 color=colors[0], line_width=line_width,
                 legend='Adult Population: {}'.format(adult_pops[0]))

grid_2_plot.line(t, grid_data[2][1],
                 color=colors[1], line_width=line_width,
                 legend='Adult Population: {}'.format(adult_pops[1]))

grid_2_plot.line(t, grid_data[2][2],
                 color=colors[2], line_width=line_width,
                 legend='Adult Population: {}'.format(adult_pops[2]))

grid_2_plot.legend.location = 'top_right'

grid_2_plot.title.text_font_size = title_font_size
grid_2_plot.legend.label_text_font_size = legend_font_size
grid_2_plot.yaxis.axis_line_width = axis_line_width
grid_2_plot.xaxis.axis_line_width = axis_line_width
grid_2_plot.yaxis.axis_label_text_font_size = axis_font_size
grid_2_plot.xaxis.axis_label_text_font_size = axis_font_size
grid_2_plot.yaxis.major_label_text_font_size = axis_tick_font_size
grid_2_plot.xaxis.major_label_text_font_size = axis_tick_font_size
grid_2_plot.ygrid.grid_line_width = grid_line_width
grid_2_plot.xgrid.grid_line_width = grid_line_width

pop_0_plot = plt.figure(plot_width=plot_width,
                         plot_height=plot_height)
pop_0_plot.title.text       = 'Reproduction, Adult Population: {}'. \
    format(adult_pops[0])
pop_0_plot.yaxis.axis_label = 'egg_mass population'
pop_0_plot.xaxis.axis_label = 'time (days)'

pop_0_plot.line(t, grid_data[0][0],
                color=colors[0], line_width=line_width,
                legend='Grid Size: {}'.format(grid_size[0]))

pop_0_plot.line(t, grid_data[1][0],
                color=colors[1], line_width=line_width,
                legend='Grid Size: {}'.format(grid_size[1]))

pop_0_plot.line(t, grid_data[2][0],
                color=colors[2], line_width=line_width,
                legend='Grid Size: {}'.format(grid_size[2]))

pop_0_plot.legend.location = 'top_right'

pop_0_plot.title.text_font_size = title_font_size
pop_0_plot.legend.label_text_font_size = legend_font_size
pop_0_plot.yaxis.axis_line_width = axis_line_width
pop_0_plot.xaxis.axis_line_width = axis_line_width
pop_0_plot.yaxis.axis_label_text_font_size = axis_font_size
pop_0_plot.xaxis.axis_label_text_font_size = axis_font_size
pop_0_plot.yaxis.major_label_text_font_size = axis_tick_font_size
pop_0_plot.xaxis.major_label_text_font_size = axis_tick_font_size
pop_0_plot.ygrid.grid_line_width = grid_line_width
pop_0_plot.xgrid.grid_line_width = grid_line_width

pop_1_plot = plt.figure(plot_width=plot_width,
                        plot_height=plot_height)
pop_1_plot.title.text       = 'Reproduction, Adult Population: {}'. \
    format(adult_pops[1])
pop_1_plot.yaxis.axis_label = 'egg_mass population'
pop_1_plot.xaxis.axis_label = 'time (days)'

pop_1_plot.line(t, grid_data[0][1],
                color=colors[0], line_width=line_width,
                legend='Grid Size: {}'.format(grid_size[0]))

pop_1_plot.line(t, grid_data[1][1],
                color=colors[1], line_width=line_width,
                legend='Grid Size: {}'.format(grid_size[1]))

pop_1_plot.line(t, grid_data[2][1],
                color=colors[2], line_width=line_width,
                legend='Grid Size: {}'.format(grid_size[2]))

pop_1_plot.legend.location = 'top_right'

pop_1_plot.title.text_font_size = title_font_size
pop_1_plot.legend.label_text_font_size = legend_font_size
pop_1_plot.yaxis.axis_line_width = axis_line_width
pop_1_plot.xaxis.axis_line_width = axis_line_width
pop_1_plot.yaxis.axis_label_text_font_size = axis_font_size
pop_1_plot.xaxis.axis_label_text_font_size = axis_font_size
pop_1_plot.yaxis.major_label_text_font_size = axis_tick_font_size
pop_1_plot.xaxis.major_label_text_font_size = axis_tick_font_size
pop_1_plot.ygrid.grid_line_width = grid_line_width
pop_1_plot.xgrid.grid_line_width = grid_line_width

pop_2_plot = plt.figure(plot_width=plot_width,
                        plot_height=plot_height)
pop_2_plot.title.text       = 'Reproduction, Adult Population: {}'. \
    format(adult_pops[2])
pop_2_plot.yaxis.axis_label = 'egg_mass population'
pop_2_plot.xaxis.axis_label = 'time (days)'

pop_2_plot.line(t, grid_data[0][2],
                color=colors[0], line_width=line_width,
                legend='Grid Size: {}'.format(grid_size[0]))

pop_2_plot.line(t, grid_data[1][2],
                color=colors[1], line_width=line_width,
                legend='Grid Size: {}'.format(grid_size[1]))

pop_2_plot.line(t, grid_data[2][2],
                color=colors[2], line_width=line_width,
                legend='Grid Size: {}'.format(grid_size[2]))

pop_2_plot.legend.location = 'top_right'

pop_2_plot.title.text_font_size = title_font_size
pop_2_plot.legend.label_text_font_size = legend_font_size
pop_2_plot.yaxis.axis_line_width = axis_line_width
pop_2_plot.xaxis.axis_line_width = axis_line_width
pop_2_plot.yaxis.axis_label_text_font_size = axis_font_size
pop_2_plot.xaxis.axis_label_text_font_size = axis_font_size
pop_2_plot.yaxis.major_label_text_font_size = axis_tick_font_size
pop_2_plot.xaxis.major_label_text_font_size = axis_tick_font_size
pop_2_plot.ygrid.grid_line_width = grid_line_width
pop_2_plot.xgrid.grid_line_width = grid_line_width

layout = lay.column(grid_0_plot, grid_1_plot, grid_2_plot,
                    pop_0_plot,  pop_1_plot,  pop_2_plot)
plt.show(layout)
