import datetime
import dataclasses as dclass
import numpy       as np
import pandas      as pd

import bokeh.plotting as plt
import bokeh.layouts  as lay
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
dominance = 0
trials    = 10

age_max        = 12
num_steps_mate = 10

num_eggs   = 10
num_larvae = 1000
num_adults = 200
save_fig   = True

field_grid = 25
plant_grid = 1

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
save_file = 'mate_plots.html'


@dclass.dataclass
class Simulator(object):
    """
    Class to setup and run a simulation of only biomass growth:

    Variables:
        nums:    initial population numbers
        bt_prop: bt proportion
    """

    grid        = [graph.graph(field_grid),
                   graph.graph(plant_grid)]
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
    simulation: hint.simulation = None

    def __post_init__(self):
        inputs = self.input_models(self.mate_encounter, self.mate_radius)
        inputs = tuple(inputs)

        self.simulation = main_simulation.Simulation. \
            setup(self.nums,
                  self.grid,
                  self.attrs,
                  self.data,
                  self.bt_prop,
                  self.steps,
                  self.emigration,
                  self.immigration,
                  *inputs,
                  **self.input_variables)

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

    @staticmethod
    def percent(dataframe: hint.dataframe) -> None:
        """
        Add percent resist column

        Args:
            dataframe: dataframe to process

        Effects:
            add percent column
        """

        def resist(row) -> float:
            """
            Percent resistant of row value

            Args:
                row: row of dataframe

            Returns:
                percent resistant
            """

            ss = row['genotype_susceptible']
            sr = row['genotype_heterozygous']
            rr = row['genotype_resistant']

            total = 2*(ss + sr + rr)

            if total == 0:
                return np.nan
            else:
                r = 2*rr + sr

                return r / total

        dataframe['percent'] = dataframe.apply(lambda row: resist(row), axis=1)

    @staticmethod
    def ratios(dataframe: hint.dataframe) -> None:
        """
        Add ratio of genotype columns

        Args:
            dataframe: dataframe to process

        Effects:
            add ratio columns
        """

        def resist(row) -> float:
            """
            Percent resistant of row value

            Args:
                row: row of dataframe

            Returns:
                percent resistant
            """

            ss = row['genotype_susceptible']
            sr = row['genotype_heterozygous']
            rr = row['genotype_resistant']

            total = ss + sr + rr

            if total == 0:
                return 0
            else:
                return rr / total

        def suscept(row) -> float:
            """
            Percent susceptible of row value

            Args:
                row: row of dataframe

            Returns:
                percent resistant
            """

            ss = row['genotype_susceptible']
            sr = row['genotype_heterozygous']
            rr = row['genotype_resistant']

            total = ss + sr + rr

            if total == 0:
                return 0
            else:
                return ss / total

        def hetero(row) -> float:
            """
            Percent hetero of row value

            Args:
                row: row of dataframe

            Returns:
                percent resistant
            """

            ss = row['genotype_susceptible']
            sr = row['genotype_heterozygous']
            rr = row['genotype_resistant']

            total = ss + sr + rr

            if total == 0:
                return 0
            else:
                return sr / total

        dataframe['percent_resist'] = \
            dataframe.apply(lambda row: resist(row), axis=1)

        dataframe['percent_suscept'] = \
            dataframe.apply(lambda row: suscept(row), axis=1)

        dataframe['percent_hetero'] = \
            dataframe.apply(lambda row: hetero(row), axis=1)

    def run(self, times: list) -> hint.dataframe:
        """
        Run the simulation for each time

        Args:
            times: the times for the simulation

        Returns:
            num egg_mass, densities
        """

        for time in times[1:]:
            print('        {} Running step: {}'.
                  format(datetime.datetime.now(), time))
            self.simulation.step()

        print('        {} Getting data'.format(datetime.datetime.now()))
        dataframes = self.simulation.agents.dataframes()
        dataframe  = dataframes['(0,)_egg']
        print('        {} Calculating Percent'.format(datetime.datetime.now()))
        self.percent(dataframe)
        self.ratios(dataframe)

        return dataframe


t          = list(range(num_steps_mate))

resist_percent = [0.1, 0.5, 0.9]
mean_data = []
for percent in resist_percent:
    print('{} Running Mating simulations with {} resist'.
          format(datetime.datetime.now(), percent))
    rho     = param.mate_encounter
    rad     = param.mate_radius
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
                              rho,
                              rad)
        egg_data.append(simulator.run(t))
    mean_data.append(pd.concat(egg_data).groupby(level=0).mean())

resist_0_source = mdl.ColumnDataSource(mean_data[0])
resist_1_source = mdl.ColumnDataSource(mean_data[1])
resist_2_source = mdl.ColumnDataSource(mean_data[2])

pop_plot = plt.figure(plot_width=plot_width,
                      plot_height=plot_height)
pop_plot.title.text       = 'Resistant Allele Frequency'
pop_plot.yaxis.axis_label = '% resistant'
pop_plot.xaxis.axis_label = 'time (days)'

pop_plot.line(x='index', y='percent',
              source=resist_0_source,
              color=colors[0], line_width=line_width,
              legend='Parental: {}'.format(resist_percent[0]))

pop_plot.line(x='index', y='percent',
              source=resist_1_source,
              color=colors[1], line_width=line_width,
              legend='Parental: {}'.format(resist_percent[1]))

pop_plot.line(x='index', y='percent',
              source=resist_2_source,
              color=colors[2], line_width=line_width,
              legend='Parental: {}'.format(resist_percent[2]))

pop_plot.legend.location = "top_left"

pop_plot.title.text_font_size = title_font_size
pop_plot.legend.label_text_font_size = legend_font_size
pop_plot.yaxis.axis_line_width = axis_line_width
pop_plot.xaxis.axis_line_width = axis_line_width
pop_plot.yaxis.axis_label_text_font_size = axis_font_size
pop_plot.xaxis.axis_label_text_font_size = axis_font_size
pop_plot.yaxis.major_label_text_font_size = axis_tick_font_size
pop_plot.xaxis.major_label_text_font_size = axis_tick_font_size
pop_plot.ygrid.grid_line_width = grid_line_width
pop_plot.xgrid.grid_line_width = grid_line_width

layout = lay.column(pop_plot)
plt.show(layout)

# rho_values = np.linspace(0.1, 1, 10)
# rad_values = np.linspace(0, 10, 11)
# resist_percent = [0.1, 0.5, 0.9]
# mean_percent_rho = []
# mean_percent_rad = []
# for percent in resist_percent:
#     print('{} Running Mating simulations with {} resist'.
#           format(datetime.datetime.now(), percent))
#     rr_pop = int(num_adults*percent)
#     ss_pop = int(num_adults*(1-percent))
#     initial_pops = ((0,      0, 0),
#                     (0,      0, 0),
#                     (0,      0, 0),
#                     (rr_pop, 0, ss_pop),
#                     (0,      0, 0))
#
#     mean_data_rho = []
#     for rho in rho_values:
#         print('{} Running Rho: {}'.
#               format(datetime.datetime.now(), rho))
#         egg_data   = []
#         for num in range(trials):
#             print('    {} Running Trial: {}'.format(datetime.datetime.now(),
#                                                     num))
#             simulator = Simulator(initial_pops, 1,
#                                   rho,
#                                   param.mate_radius)
#             data = simulator.run(t)
#             egg_data.append(data['percent'].mean())
#         mean_data_rho.append(np.mean(egg_data))
#     mean_percent_rho.append(mean_data_rho)
#
#     mean_data_rad = []
#     for rad in rad_values:
#         print('{} Running Rad: {}'.
#               format(datetime.datetime.now(), rad))
#         egg_data   = []
#         for num in range(trials):
#             print('    {} Running Trial: {}'.format(datetime.datetime.now(),
#                                                     num))
#             simulator = Simulator(initial_pops, 1,
#                                   param.mate_encounter,
#                                   rad)
#             data = simulator.run(t)
#             egg_data.append(data['percent'].mean())
#         mean_data_rad.append(np.mean(egg_data))
#     mean_percent_rad.append(mean_data_rad)
#
# encount_plot = plt.figure(plot_width=plot_width,
#                           plot_height=plot_height)
# encount_plot.title.text       = 'Resistant Allele Frequency, Radius={}'.\
#     format(param.mate_radius)
# encount_plot.yaxis.axis_label = '% resistant'
# encount_plot.xaxis.axis_label = 'encounter constant'
#
# encount_plot.line(rho_values, mean_percent_rho[0],
#                   color=colors[0], line_width=line_width,
#                   legend='Parental Resistance: {}'.format(resist_percent[0]))
#
# encount_plot.line(rho_values, mean_percent_rho[1],
#                   color=colors[1], line_width=line_width,
#                   legend='Parental Resistance: {}'.format(resist_percent[1]))
#
# encount_plot.line(rho_values, mean_percent_rho[2],
#                   color=colors[2], line_width=line_width,
#                   legend='Parental Resistance: {}'.format(resist_percent[2]))
#
# encount_plot.legend.location = "top_left"
#
# encount_plot.title.text_font_size = title_font_size
# encount_plot.legend.label_text_font_size = legend_font_size
# encount_plot.yaxis.axis_line_width = axis_line_width
# encount_plot.xaxis.axis_line_width = axis_line_width
# encount_plot.yaxis.axis_label_text_font_size = axis_font_size
# encount_plot.xaxis.axis_label_text_font_size = axis_font_size
# encount_plot.yaxis.major_label_text_font_size = axis_tick_font_size
# encount_plot.xaxis.major_label_text_font_size = axis_tick_font_size
# encount_plot.ygrid.grid_line_width = grid_line_width
# encount_plot.xgrid.grid_line_width = grid_line_width
#
# radius_plot = plt.figure(plot_width=plot_width,
#                          plot_height=plot_height)
# radius_plot.title.text       = 'Resistant Allele Frequency, Encounter={}'. \
#     format(param.mate_encounter)
# radius_plot.yaxis.axis_label = '% resistant'
# radius_plot.xaxis.axis_label = 'radius'
#
# radius_plot.line(rad_values, mean_percent_rad[0],
#                  color=colors[0], line_width=line_width,
#                  legend='Parental Resistance: {}'.format(resist_percent[0]))
#
# radius_plot.line(rad_values, mean_percent_rad[1],
#                  color=colors[1], line_width=line_width,
#                  legend='Parental Resistance: {}'.format(resist_percent[1]))
#
# radius_plot.line(rad_values, mean_percent_rad[2],
#                  color=colors[2], line_width=line_width,
#                  legend='Parental Resistance: {}'.format(resist_percent[2]))
#
# radius_plot.legend.location = "top_left"
#
# radius_plot.title.text_font_size = title_font_size
# radius_plot.legend.label_text_font_size = legend_font_size
# radius_plot.yaxis.axis_line_width = axis_line_width
# radius_plot.xaxis.axis_line_width = axis_line_width
# radius_plot.yaxis.axis_label_text_font_size = axis_font_size
# radius_plot.xaxis.axis_label_text_font_size = axis_font_size
# radius_plot.yaxis.major_label_text_font_size = axis_tick_font_size
# radius_plot.xaxis.major_label_text_font_size = axis_tick_font_size
# radius_plot.ygrid.grid_line_width = grid_line_width
# radius_plot.xgrid.grid_line_width = grid_line_width
#
# layout = lay.column(encount_plot,
#                     radius_plot)
# plt.show(layout)
