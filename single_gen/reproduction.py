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
trials    = 5000

age_max           = 12
num_steps_density = 5

num_eggs   = 10
num_larvae = 1000
num_adults = 500
save_fig   = True

field_grid = 25


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
class Fecundity(object):
    """
    Class to setup and run a simulation of the female fecundity

    Variables:
        fecundity: the fecundity model
    """

    init_num  = init_bio.init_num(param.lam_0_egg)
    fecundity = repro.fecundity(param.fecundity_maximum,
                                param.fecundity_decay)

    def run(self, ages: list) -> list:
        """
        Run the model for each age

        Args:
            ages: list of ages

        Returns:
            list of number of eggs
        """

        numbers = []
        for age in ages:
            number_egg_mass = self.fecundity(age, 0, 'none')
            number_eggs     = self.init_num('none')

            numbers.append(number_egg_mass*number_eggs)

        return numbers

    @classmethod
    def run_sim(cls, ages: list) -> list:
        """
        Setup and rum the sim

        Args:
            ages: ages to simulate

        Returns:
            number of eggs produced
        """

        new = cls()

        return new.run(ages)


@dclass.dataclass
class Simulator(object):
    """
    Class to setup and run a simulation of only biomass growth:

    Variables:
        nums:    initial population numbers
        bt_prop: bt proportion
    """

    grid        = [graph.graph(field_grid),
                   (keyword.hexagon, 1, 1, True)]
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
                    move.adult(param.adult_scale,
                               param.adult_shape),
                    repro.mating(param.mate_encounter),
                    repro.radius(param.mate_radius),
                    repro.fecundity(param.fecundity_maximum,
                                    param.fecundity_decay),
                    repro.density(param.eta,
                                  param.gamma),
                    repro.init_sex(param.female_prob)]
    input_variables = param.repro_values

    nums:       hint.init_pops
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

    def collect(self) -> int:
        """
        Collect the number of egg_masses

        Returns:
            number of egg_masses
        """

        egg_masses = self.simulation.agents.agents(keyword.egg_mass)

        return len(egg_masses)

    def run(self, times: list) -> tuple:
        """
        Run the simulation for each time

        Args:
            times: the times for the simulation

        Returns:
            num egg_mass, densities
        """
        #
        # females = self.simulation.agents[(0,)]['female'].agents
        # for agent in females:
        #     print('Agent: {}, Num_eggs: {}'.format(agent.unique_id,
        #                                            agent.num_eggs))

        data = [self.collect()]
        for time in times[1:]:
            print('        {} Running step: {}'.
                  format(datetime.datetime.now(), time))
            self.simulation.step()
            data.append(self.collect())

            # females = self.simulation.agents[(0,)]['female'].agents
            # for agent in females:
            #     print('Agent: {}, Num_eggs: {}'.format(agent.unique_id,
            #                                            agent.num_eggs))

        density = []
        for number in data:
            density.append(number/(field_grid**2))

        return data, density


a = list(range(age_max))
print('{} Running Fecundity simulations'.
      format(datetime.datetime.now()))
fecundity_data = []
for num in range(trials):
    print('    {} Running Trial: {}'.format(datetime.datetime.now(), num))
    fecundity_data.append(Fecundity.run_sim(a))

fecundity_mean  = np.mean(fecundity_data, axis=0)
fecundity_lower = np.percentile(fecundity_data, 2.5, axis=0)
fecundity_upper = np.percentile(fecundity_data, 97.5, axis=0)

fecundity_plot = plt.figure(plot_width=plot_width,
                            plot_height=plot_height)
fecundity_plot.title.text       = 'Number of Eggs, ' \
                                  'Number of Trials: {}'.format(trials)
fecundity_plot.yaxis.axis_label = 'population'
fecundity_plot.xaxis.axis_label = 'time (days)'

fecundity_plot.line(a, fecundity_mean,
                    color=colors[0],
                    line_width=line_width,
                    legend='number of eggs')
fecundity_plot.circle(a, fecundity_mean,
                      color=colors[0],
                      size=point_size,
                      legend='number of eggs')
# fecundity_plot.segment(x0=a, y0=fecundity_lower,
#                        x1=a, y1=fecundity_upper,
#                        line_color=colors[0], line_width=line_width / 2,
#                        line_cap='square')

fecundity_plot.legend.location = 'top_right'
fecundity_plot.title.text_font_size = title_font_size
fecundity_plot.legend.label_text_font_size = legend_font_size
fecundity_plot.yaxis.axis_line_width = axis_line_width
fecundity_plot.xaxis.axis_line_width = axis_line_width
fecundity_plot.yaxis.axis_label_text_font_size = axis_font_size
fecundity_plot.xaxis.axis_label_text_font_size = axis_font_size
fecundity_plot.yaxis.major_label_text_font_size = axis_tick_font_size
fecundity_plot.xaxis.major_label_text_font_size = axis_tick_font_size
fecundity_plot.ygrid.grid_line_width = grid_line_width
fecundity_plot.xgrid.grid_line_width = grid_line_width

plt.show(fecundity_plot)


# t            = list(range(num_steps_density))
# initial_pops = ((0,          0,          0),
#                 (0,          0,          0),
#                 (0,          0,          0),
#                 (0,          0,          0),
#                 (num_adults, num_adults, num_adults))
# print('{} Running Reproduction simulations'.
#       format(datetime.datetime.now()))
# eggs_mass          = []
# egg_mass_densities = []
# eggs               = []
# for num in range(trials):
#     print('    {} Running Trial: {}'.format(datetime.datetime.now(), num))
#     simulator = Simulator(initial_pops, 1)
#     egg_mass, egg_mass_density = simulator.run(t)
#     dataframes = simulator.simulation.agents.dataframes()
#     egg = dataframes['(0,)_egg']
#
#     eggs_mass.append(egg_mass)
#     egg_mass_densities.append(egg_mass_density)
#     eggs.append(egg)
#
# egg_mass_mean  = np.mean(eggs_mass, axis=0)
# egg_mass_lower = np.percentile(eggs_mass, 2.5, axis=0)
# egg_mass_upper = np.percentile(eggs_mass, 97.5, axis=0)
#
# egg_mass_density_mean  = np.mean(egg_mass_densities, axis=0)
# egg_mass_density_lower = np.percentile(egg_mass_densities, 2.5, axis=0)
# egg_mass_density_upper = np.percentile(egg_mass_densities, 97.5, axis=0)
#
# egg_mass_plot = plt.figure(plot_width=plot_width,
#                            plot_height=plot_height)
# egg_mass_plot.title.text       = 'Number of Juveniles, ' \
#                                  'Number of Trials: {}'.format(trials)
# egg_mass_plot.yaxis.axis_label = 'population'
# egg_mass_plot.xaxis.axis_label = 'time (days)'
#
# egg_mass_plot.line(t, egg_mass_mean,
#                    color=colors[0],
#                    line_width=line_width,
#                    legend='number of agents')
# egg_mass_plot.circle(t, egg_mass_mean,
#                      color=colors[0],
#                      size=point_size,
#                      legend='number of agents')
# egg_mass_plot.segment(x0=t, y0=egg_mass_lower,
#                       x1=t, y1=egg_mass_upper,
#                       line_color=colors[0], line_width=line_width/2,
#                       line_cap='square')
#
# egg_mass_plot.legend.location = 'top_left'
#
# egg_mass_plot.title.text_font_size = title_font_size
# egg_mass_plot.legend.label_text_font_size = legend_font_size
# egg_mass_plot.yaxis.axis_line_width = axis_line_width
# egg_mass_plot.xaxis.axis_line_width = axis_line_width
# egg_mass_plot.yaxis.axis_label_text_font_size = axis_font_size
# egg_mass_plot.xaxis.axis_label_text_font_size = axis_font_size
# egg_mass_plot.yaxis.major_label_text_font_size = axis_tick_font_size
# egg_mass_plot.xaxis.major_label_text_font_size = axis_tick_font_size
# egg_mass_plot.ygrid.grid_line_width = grid_line_width
# egg_mass_plot.xgrid.grid_line_width = grid_line_width
#
# # plt.show(egg_mass_plot)
#
#
# egg_mass_density_plot = plt.figure(plot_width=plot_width,
#                                    plot_height=plot_height)
# egg_mass_density_plot.title.text       = 'Density of Juveniles, ' \
#                                          'Number of Trials: {}'.format(trials)
# egg_mass_density_plot.yaxis.axis_label = 'population per plant'
# egg_mass_density_plot.xaxis.axis_label = 'time (days)'
#
# egg_mass_density_plot.line(t, egg_mass_density_mean,
#                            color=colors[0],
#                            line_width=line_width,
#                            legend='density of agents')
# egg_mass_density_plot.circle(t, egg_mass_density_mean,
#                              color=colors[0],
#                              size=point_size,
#                              legend='density of agents')
# egg_mass_density_plot.segment(x0=t, y0=egg_mass_density_lower,
#                               x1=t, y1=egg_mass_density_upper,
#                               line_color=colors[0], line_width=line_width/2,
#                               line_cap='square')
#
# egg_mass_density_plot.legend.location = 'top_left'
#
# egg_mass_density_plot.title.text_font_size = title_font_size
# egg_mass_density_plot.legend.label_text_font_size = legend_font_size
# egg_mass_density_plot.yaxis.axis_line_width = axis_line_width
# egg_mass_density_plot.xaxis.axis_line_width = axis_line_width
# egg_mass_density_plot.yaxis.axis_label_text_font_size = axis_font_size
# egg_mass_density_plot.xaxis.axis_label_text_font_size = axis_font_size
# egg_mass_density_plot.yaxis.major_label_text_font_size = axis_tick_font_size
# egg_mass_density_plot.xaxis.major_label_text_font_size = axis_tick_font_size
# egg_mass_density_plot.ygrid.grid_line_width = grid_line_width
# egg_mass_density_plot.xgrid.grid_line_width = grid_line_width
#
# layout = lay.column(egg_mass_plot, egg_mass_density_plot,
#                     fecundity_plot)
# plt.show(layout)
