import datetime
import dataclasses as dclass
import numpy       as np
import pandas      as pd

import bokeh.plotting as plt
import bokeh.layouts  as lay
import bokeh.palettes as palettes

import parameters.data_tracking    as tracking
import parameters.model_parameters as param

import models.development  as dev
import models.forage       as forage
import models.graph        as graph
import models.growth       as growth
import models.init_biomass as init_bio
import models.reproduction as repro
import models.survival     as sur

import source.hint    as hint
import source.keyword as keyword

import source.simulation.simulation as main_simulation


# Plotting parameters
trials     = 100
dominance  = 0
num_steps  = 20

num_steps_eggs = 10
num_eggs       = 10

num_steps_larvae = 20
num_larvae       = 1000
hist_density     = False
mass_bins        = 30
digits           = 3

num_steps_pupae = 15
num_pupae       = 1000

use_hetero = False

line_width       = 3.5
point_size       = 10
point_size_stoch = 8

alpha               = 0.8
axis_line_width     = 2
grid_line_width     = 2
title_font_size     = '16pt'
legend_font_size    = '12pt'
axis_font_size      = '12pt'
axis_tick_font_size = '10pt'

plot_width  = 800
plot_height = 500

colors    = palettes.Colorblind[6]
save_file = 'develop_plots.html'

plt.output_file(save_file)


sex_model = repro.init_sex(1)


@dclass.dataclass
class Simulator(object):
    """
    Class to setup and run a simulation of only biomass growth:

    Variables:
        nums:   initial population numbers
        forage: the plant forage model
    """

    grid        = [graph.graph(10),
                   (keyword.hexagon, 1, 1, True)]
    attrs       = {0: tracking.genotype_attrs}
    data        = (np.inf,)
    step        = [({keyword.larva: [keyword.consume,
                                     keyword.grow,
                                     keyword.survive,
                                     keyword.advance_age,
                                     keyword.reset]},)]
    emigration  = []
    immigration = []
    input_variables = param.repro_values

    nums:             hint.init_pops
    bt_prop:          float
    larva_prob_bt_ss: float
    simulation:       hint.simulation = None

    def __post_init__(self):

        input_models = self.input_models(self.larva_prob_bt_ss)
        input_models = tuple(input_models)

        self.simulation = main_simulation.Simulation. \
            setup(self.nums,
                  self.grid,
                  self.attrs,
                  self.data,
                  self.bt_prop,
                  self.step,
                  self.emigration,
                  self.immigration,
                  *input_models,
                  **self.input_variables)

    @staticmethod
    def input_models(larva_prob_bt_ss: float) -> list:
        """
        Create a list of input models
        Args:
            larva_prob_bt_ss: ss prob in bt

        Returns:

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
            forage.adlibitum(1),
            sex_model,
            dev.egg_dev(param.mu_egg_dev,
                        param.sig_egg_dev),
            dev.larva_dev(param.mu_larva_dev_ss,
                          param.mu_larva_dev_rr,
                          param.sig_larva_dev_ss,
                          param.sig_larva_dev_rr,
                          dominance),
            dev.pupa_dev(param.mu_pupa_dev,
                         param.sig_pupa_dev),
            sur.egg_sur(param.egg_prob),
            sur.pupa_sur(param.pupa_prob),
            sur.adult_sur(param.adult_prob),
            sur.larva_sur(param.larva_prob_non_bt_rr,
                          param.larva_prob_non_bt_ss,
                          param.larva_prob_bt_rr,
                          larva_prob_bt_ss,
                          dominance)
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

    def run(self, times: list) -> hint.dataframe:
        """
        Run the simulation for each time

        Args:
            times: the times for the simulation

        Returns:
            biomass data
        """

        for this in times[1:]:
            self.simulation.step()
            print('           {}: Running step {}'.
                  format(datetime.datetime.now(), this))

        dataframes = self.simulation.agents.dataframes()
        dataframe  = dataframes['(0,)_larva']
        self.percent(dataframe)

        return dataframe


t = list(range(num_steps))
initial_pops = ((0,          0, 0),
                (num_larvae, 0, num_larvae),
                (0,          0, 0),
                (0,          0, 0),
                (0,          0, 0))

bt_levels = np.linspace(0, 1, 11)
larva_probs = [param.larva_prob_bt_low_ss,
               param.larva_prob_bt_mid_ss,
               param.larva_prob_bt_high_ss]

prob_data = []
for larva_prob in larva_probs:
    print('{}: Running Prob: {}'.format(datetime.datetime.now(), larva_prob))
    bt_data = []
    for bt_level in bt_levels:
        print('    {}: Running Bt: {}'.format(datetime.datetime.now(),
                                              bt_level))
        larva_data = []
        for num in range(trials):
            print('        {}: Running trial {}'.format(datetime.datetime.now(),
                                                        num))
            simulation = Simulator(initial_pops,
                                   bt_level,
                                   larva_prob)
            larva_data.append(simulation.run(t))
        bt_data.append(pd.concat(larva_data).groupby(level=0).
                         mean()['percent'].iat[-1])
    prob_data.append(bt_data)

survive_plot = plt.figure(plot_width=plot_width,
                           plot_height=plot_height,
                           y_range=(0, 1))
survive_plot.title.text       = 'Resistant Allele Frequency'
survive_plot.yaxis.axis_label = '% resistant'
survive_plot.xaxis.axis_label = '% Bt'

survive_plot.line(bt_levels, prob_data[0],
                   color=colors[0], line_width=line_width,
                   legend='P_SS: {}'.format(np.round(larva_probs[0], 3)))

survive_plot.line(bt_levels, prob_data[1],
                  color=colors[1], line_width=line_width,
                  legend='P_SS: {}'.format(np.round(larva_probs[1], 3)))

survive_plot.line(bt_levels, prob_data[2],
                  color=colors[2], line_width=line_width,
                  legend='P_SS: {}'.format(np.round(larva_probs[2], 3)))

survive_plot.legend.location = "bottom_right"

survive_plot.title.text_font_size = title_font_size
survive_plot.legend.label_text_font_size = legend_font_size
survive_plot.yaxis.axis_line_width = axis_line_width
survive_plot.xaxis.axis_line_width = axis_line_width
survive_plot.yaxis.axis_label_text_font_size = axis_font_size
survive_plot.xaxis.axis_label_text_font_size = axis_font_size
survive_plot.yaxis.major_label_text_font_size = axis_tick_font_size
survive_plot.xaxis.major_label_text_font_size = axis_tick_font_size
survive_plot.ygrid.grid_line_width = grid_line_width
survive_plot.xgrid.grid_line_width = grid_line_width

layout = lay.column(survive_plot)
plt.show(layout)
