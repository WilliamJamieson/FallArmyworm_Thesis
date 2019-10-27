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

import models.growth       as growth
import models.init_biomass as init_bio
import models.reproduction as repro
import models.survival     as sur

import source.hint    as hint
import source.keyword as keyword

import source.simulation.simulation as main_simulation


# Plotting parameters
trials     = 1000
dominance  = 0
num_steps  = 40
num_eggs   = 10
num_larvae = 1000
num_pupae  = 1000
num_adults = 1000

use_hetero = False

line_width       = 3.5
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

colors    = palettes.Colorblind[3]
save_file = 'survive_plots.html'

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

    grid        = [(keyword.hexagon, 1, 1, True),
                   (keyword.hexagon, 1, 1, True)]
    attrs       = {1: tracking.genotype_attrs}
    data        = (np.inf,)
    steps       = [({keyword.larva:  [keyword.survive],
                     keyword.egg:    [keyword.survive],
                     keyword.pupa:   [keyword.survive],
                     keyword.female: [keyword.survive]},)]
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
                    sur.egg_sur(param.egg_prob),
                    sur.pupa_sur(param.pupa_prob),
                    sur.adult_sur(param.adult_prob)]
    input_variables = param.repro_values

    # input_survive.larva_survival,
    nums:       hint.init_pops
    bt_prop:    float
    ss_bt_sur:  float           = param.larva_prob_bt_low_ss
    simulation: hint.simulation = None

    def __post_init__(self):

        larva_survive = sur.larva_sur(param.larva_prob_non_bt_rr,
                                      param.larva_prob_non_bt_ss,
                                      param.larva_prob_bt_rr,
                                      self.ss_bt_sur,
                                      dominance)
        input_models = self.input_models.copy()
        input_models.append(larva_survive)

        self.simulation = main_simulation.Simulation. \
            setup(self.nums,
                  self.grid,
                  self.attrs,
                  self.data,
                  self.bt_prop,
                  self.steps,
                  self.emigration,
                  self.immigration,
                  *input_models,
                  **self.input_variables)

    def run(self, times: list) -> None:
        """
        Run the simulation for each time

        Args:
            times: the times for the simulation

        Returns:
            biomass data
        """

        for _ in times[1:]:
            self.simulation.step()


def mean_data(dataframes: hint.dataframe_list) -> hint.dataframe:
    """
    Generate a mean data frame from the list of dataframes

    Args:
        dataframes: list of dataframes

    Returns:
        a mean dataframe
    """

    concat     = pd.concat(dataframes)
    row_concat = concat.groupby(concat.index)

    mean = row_concat.mean()
    mean['index'] = range(len(mean.index))

    return mean


t            = list(range(num_steps))
initial_pops = ((num_eggs,   num_eggs,   num_eggs),
                (num_larvae, num_larvae, num_larvae),
                (num_pupae,  num_pupae,  num_pupae),
                (num_adults, num_adults, num_adults),
                (0,          0,          0))
print('{} Running Survival Bt low survival simulations'.
      format(datetime.datetime.now()))
egg_bt       = []
larva_low_bt = []
pupa_bt      = []
adult_bt     = []
for num in range(trials):
    print('    {} Running Trial: {}'.format(datetime.datetime.now(), num))
    simulator_bt = Simulator(initial_pops, 1)
    simulator_bt.run(t)
    dataframes_bt = simulator_bt.simulation.agents.dataframes()
    egg_bt.      append(dataframes_bt['(0, 0)_egg'])
    larva_low_bt.append(dataframes_bt['(0, 0)_larva'])
    pupa_bt.     append(dataframes_bt['(0, 0)_pupa'])
    adult_bt.     append(dataframes_bt['(0, 0)_female'])

egg_bt_mean       = mean_data(egg_bt)
larva_low_bt_mean = mean_data(larva_low_bt)
pupa_bt_mean      = mean_data(pupa_bt)
adult_bt_mean     = mean_data(adult_bt)

egg_source   = mdl.ColumnDataSource(egg_bt_mean)
pupa_source  = mdl.ColumnDataSource(pupa_bt_mean)
adult_source = mdl.ColumnDataSource(adult_bt_mean)

larva_low_bt_source = mdl.ColumnDataSource(larva_low_bt_mean)

egg_plot = plt.figure(plot_width=plot_width,
                      plot_height=plot_height,
                      y_range=(0, 2100))
egg_plot.title.text       = 'Egg Survival, ' \
                            'Number of Trials: {}'.format(trials)
egg_plot.yaxis.axis_label = 'population'
egg_plot.xaxis.axis_label = 'time (days)'

egg_plot.line(x='index', y='genotype_resistant',
              source=egg_source,
              color=colors[0], line_width=line_width,
              legend='Resistant')
egg_plot.line(x='index', y='genotype_susceptible',
              source=egg_source,
              color=colors[1], line_width=line_width,
              legend='Susceptible')
if use_hetero:
    egg_plot.line(x='index', y='genotype_heterozygous',
                  source=egg_source,
                  color=colors[2], line_width=line_width,
                  legend='Heterozygous')

egg_plot.legend.location = 'top_right'

egg_plot.title.text_font_size = title_font_size
egg_plot.legend.label_text_font_size = legend_font_size
egg_plot.yaxis.axis_line_width = axis_line_width
egg_plot.xaxis.axis_line_width = axis_line_width
egg_plot.yaxis.axis_label_text_font_size = axis_font_size
egg_plot.xaxis.axis_label_text_font_size = axis_font_size
egg_plot.yaxis.major_label_text_font_size = axis_tick_font_size
egg_plot.xaxis.major_label_text_font_size = axis_tick_font_size
egg_plot.ygrid.grid_line_width = grid_line_width
egg_plot.xgrid.grid_line_width = grid_line_width

# plt.show(egg_plot)

pupa_plot = plt.figure(plot_width=plot_width,
                       plot_height=plot_height,
                       y_range=(0, 1050))
pupa_plot.title.text       = 'Pupa Survival, ' \
                             'Number of Trials: {}'.format(trials)
pupa_plot.yaxis.axis_label = 'population'
pupa_plot.xaxis.axis_label = 'time (days)'

pupa_plot.line(x='index', y='genotype_resistant',
               source=pupa_source,
               color=colors[0], line_width=line_width,
               legend='Resistant')
pupa_plot.line(x='index', y='genotype_susceptible',
               source=pupa_source,
               color=colors[1], line_width=line_width,
               legend='Susceptible')
if use_hetero:
    pupa_plot.line(x='index', y='genotype_heterozygous',
                   source=pupa_source,
                   color=colors[2], line_width=line_width,
                   legend='Heterozygous')

pupa_plot.legend.location = 'top_right'

pupa_plot.title.text_font_size = title_font_size
pupa_plot.legend.label_text_font_size = legend_font_size
pupa_plot.yaxis.axis_line_width = axis_line_width
pupa_plot.xaxis.axis_line_width = axis_line_width
pupa_plot.yaxis.axis_label_text_font_size = axis_font_size
pupa_plot.xaxis.axis_label_text_font_size = axis_font_size
pupa_plot.yaxis.major_label_text_font_size = axis_tick_font_size
pupa_plot.xaxis.major_label_text_font_size = axis_tick_font_size
pupa_plot.ygrid.grid_line_width = grid_line_width
pupa_plot.xgrid.grid_line_width = grid_line_width

# layout = lay.column(egg_plot, pupa_plot)
# plt.show(layout)

adult_plot = plt.figure(plot_width=plot_width,
                        plot_height=plot_height,
                        y_range=(0, 1050))
adult_plot.title.text       = 'Adult Survival, ' \
                              'Number of Trials: {}'.format(trials)
adult_plot.yaxis.axis_label = 'population'
adult_plot.xaxis.axis_label = 'time (days)'

adult_plot.line(x='index', y='genotype_resistant',
                source=adult_source,
                color=colors[0], line_width=line_width,
                legend='Resistant')
adult_plot.line(x='index', y='genotype_susceptible',
                source=adult_source,
                color=colors[1], line_width=line_width,
                legend='Susceptible')
if use_hetero:
    adult_plot.line(x='index', y='genotype_heterozygous',
                    source=adult_source,
                    color=colors[2], line_width=line_width,
                    legend='Heterozygous')

adult_plot.legend.location = 'top_right'

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

# layout = lay.column(egg_plot, pupa_plot, adult_plot)
# plt.show(layout)

larva_low_bt_plot = plt.figure(plot_width=plot_width,
                               plot_height=plot_height,
                               y_range=(0, 1050))
larva_low_bt_plot.title.text       = 'Larva on Bt with Low Survival, ' \
                                 'Number of Trials: {}'.format(trials)
larva_low_bt_plot.yaxis.axis_label = 'population'
larva_low_bt_plot.xaxis.axis_label = 'time (days)'

larva_low_bt_plot.line(x='index', y='genotype_resistant',
                       source=larva_low_bt_source,
                       color=colors[0], line_width=line_width,
                       legend='Resistant')
larva_low_bt_plot.line(x='index', y='genotype_susceptible',
                       source=larva_low_bt_source,
                       color=colors[1], line_width=line_width,
                       legend='Susceptible')
if use_hetero:
    larva_low_bt_plot.line(x='index', y='genotype_heterozygous',
                           source=larva_low_bt_source,
                           color=colors[2], line_width=line_width,
                           legend='Heterozygous')

larva_low_bt_plot.legend.location = 'top_right'

larva_low_bt_plot.title.text_font_size = title_font_size
larva_low_bt_plot.legend.label_text_font_size = legend_font_size
larva_low_bt_plot.yaxis.axis_line_width = axis_line_width
larva_low_bt_plot.xaxis.axis_line_width = axis_line_width
larva_low_bt_plot.yaxis.axis_label_text_font_size = axis_font_size
larva_low_bt_plot.xaxis.axis_label_text_font_size = axis_font_size
larva_low_bt_plot.yaxis.major_label_text_font_size = axis_tick_font_size
larva_low_bt_plot.xaxis.major_label_text_font_size = axis_tick_font_size
larva_low_bt_plot.ygrid.grid_line_width = grid_line_width
larva_low_bt_plot.xgrid.grid_line_width = grid_line_width

# layout = lay.column(egg_plot, pupa_plot, adult_plot, larva_bt_plot)
# plt.show(layout)


initial_pops = ((0,          0,          0),
                (num_larvae, num_larvae, num_larvae),
                (0,          0,          0),
                (0,          0,          0),
                (0,          0,          0))
print('{} Running Survival Bt mid survival simulations'.
      format(datetime.datetime.now()))
larva_mid_bt = []
for num in range(trials):
    print('    {} Running Trial: {}'.format(datetime.datetime.now(), num))
    simulator_bt = Simulator(initial_pops, 1, param.larva_prob_bt_mid_ss)
    simulator_bt.run(t)
    dataframes_bt = simulator_bt.simulation.agents.dataframes()
    larva_mid_bt.append(dataframes_bt['(0, 0)_larva'])

larva_mid_bt_mean   = mean_data(larva_mid_bt)
larva_mid_bt_source = mdl.ColumnDataSource(larva_mid_bt_mean)

larva_mid_bt_plot = plt.figure(plot_width=plot_width,
                               plot_height=plot_height,
                               y_range=(0, 1050))
larva_mid_bt_plot.title.text       = 'Larva on Bt with Intermediate Survival, '\
                                     'Number of Trials: {}'.format(trials)
larva_mid_bt_plot.yaxis.axis_label = 'population'
larva_mid_bt_plot.xaxis.axis_label = 'time (days)'

larva_mid_bt_plot.line(x='index', y='genotype_resistant',
                       source=larva_mid_bt_source,
                       color=colors[0], line_width=line_width,
                       legend='Resistant')
larva_mid_bt_plot.line(x='index', y='genotype_susceptible',
                       source=larva_mid_bt_source,
                       color=colors[1], line_width=line_width,
                       legend='Susceptible')
if use_hetero:
    larva_mid_bt_plot.line(x='index', y='genotype_heterozygous',
                           source=larva_mid_bt_source,
                           color=colors[2], line_width=line_width,
                           legend='Heterozygous')

larva_mid_bt_plot.legend.location = 'top_right'

larva_mid_bt_plot.title.text_font_size = title_font_size
larva_mid_bt_plot.legend.label_text_font_size = legend_font_size
larva_mid_bt_plot.yaxis.axis_line_width = axis_line_width
larva_mid_bt_plot.xaxis.axis_line_width = axis_line_width
larva_mid_bt_plot.yaxis.axis_label_text_font_size = axis_font_size
larva_mid_bt_plot.xaxis.axis_label_text_font_size = axis_font_size
larva_mid_bt_plot.yaxis.major_label_text_font_size = axis_tick_font_size
larva_mid_bt_plot.xaxis.major_label_text_font_size = axis_tick_font_size
larva_mid_bt_plot.ygrid.grid_line_width = grid_line_width
larva_mid_bt_plot.xgrid.grid_line_width = grid_line_width

print('{} Running Survival Bt high survival simulations'.
      format(datetime.datetime.now()))
larva_high_bt = []
for num in range(trials):
    print('    {} Running Trial: {}'.format(datetime.datetime.now(), num))
    simulator_bt = Simulator(initial_pops, 1, param.larva_prob_bt_high_ss)
    simulator_bt.run(t)
    dataframes_bt = simulator_bt.simulation.agents.dataframes()
    larva_high_bt.append(dataframes_bt['(0, 0)_larva'])

larva_high_bt_mean = mean_data(larva_high_bt)
larva_high_bt_source = mdl.ColumnDataSource(larva_high_bt_mean)

larva_high_bt_plot = plt.figure(plot_width=plot_width,
                                plot_height=plot_height,
                                y_range=(0, 1050))
larva_high_bt_plot.title.text       = 'Larva on Bt with High Survival, ' \
                                     'Number of Trials: {}'.format(trials)
larva_high_bt_plot.yaxis.axis_label = 'population'
larva_high_bt_plot.xaxis.axis_label = 'time (days)'

larva_high_bt_plot.line(x='index', y='genotype_resistant',
                        source=larva_high_bt_source,
                        color=colors[0], line_width=line_width,
                        legend='Resistant')
larva_high_bt_plot.line(x='index', y='genotype_susceptible',
                        source=larva_high_bt_source,
                        color=colors[1], line_width=line_width,
                        legend='Susceptible')
if use_hetero:
    larva_high_bt_plot.line(x='index', y='genotype_heterozygous',
                            source=larva_high_bt_source,
                            color=colors[2], line_width=line_width,
                            legend='Heterozygous')

larva_high_bt_plot.legend.location = 'top_right'

larva_high_bt_plot.title.text_font_size = title_font_size
larva_high_bt_plot.legend.label_text_font_size = legend_font_size
larva_high_bt_plot.yaxis.axis_line_width = axis_line_width
larva_high_bt_plot.xaxis.axis_line_width = axis_line_width
larva_high_bt_plot.yaxis.axis_label_text_font_size = axis_font_size
larva_high_bt_plot.xaxis.axis_label_text_font_size = axis_font_size
larva_high_bt_plot.yaxis.major_label_text_font_size = axis_tick_font_size
larva_high_bt_plot.xaxis.major_label_text_font_size = axis_tick_font_size
larva_high_bt_plot.ygrid.grid_line_width = grid_line_width
larva_high_bt_plot.xgrid.grid_line_width = grid_line_width

larva_bt_plot = plt.figure(plot_width=plot_width,
                           plot_height=plot_height,
                           y_range=(0, 1050))
larva_bt_plot.title.text       = 'Larva on Bt Survival, ' \
                                     'Number of Trials: {}'.format(trials)
larva_bt_plot.yaxis.axis_label = 'population'
larva_bt_plot.xaxis.axis_label = 'time (days)'

larva_bt_plot.line(x='index', y='genotype_resistant',
                   source=larva_low_bt_source,
                   color=colors[0], line_width=line_width,
                   legend='Low Resistant')
larva_bt_plot.line(x='index', y='genotype_susceptible',
                   source=larva_low_bt_source,
                   color=colors[1], line_width=line_width,
                   legend='Low Susceptible')
if use_hetero:
    larva_bt_plot.line(x='index', y='genotype_heterozygous',
                       source=larva_low_bt_source,
                       color=colors[2], line_width=line_width,
                       legend='Low Heterozygous')

larva_bt_plot.line(x='index', y='genotype_resistant',
                   source=larva_mid_bt_source,
                   color=colors[0], line_width=line_width,
                   line_dash='dashed',
                   legend='Intermediate Resistant')
larva_bt_plot.line(x='index', y='genotype_susceptible',
                   source=larva_mid_bt_source,
                   color=colors[1], line_width=line_width,
                   line_dash='dashed',
                   legend='Intermediate Susceptible')
if use_hetero:
    larva_bt_plot.line(x='index', y='genotype_heterozygous',
                       source=larva_mid_bt_source,
                       color=colors[2], line_width=line_width,
                       line_dash='dashed',
                       legend='Intermediate Heterozygous')

larva_bt_plot.line(x='index', y='genotype_resistant',
                   source=larva_high_bt_source,
                   color=colors[0], line_width=line_width,
                   line_dash='dashdot',
                   legend='High Resistant')
larva_bt_plot.line(x='index', y='genotype_susceptible',
                   source=larva_high_bt_source,
                   color=colors[1], line_width=line_width,
                   line_dash='dashdot',
                   legend='High Susceptible')
if use_hetero:
    larva_bt_plot.line(x='index', y='genotype_heterozygous',
                       source=larva_high_bt_source,
                       color=colors[2], line_width=line_width,
                       line_dash='dashdot',
                       legend='High Heterozygous')

larva_bt_plot.legend.location = 'top_right'

larva_bt_plot.title.text_font_size = title_font_size
larva_bt_plot.legend.label_text_font_size = legend_font_size
larva_bt_plot.yaxis.axis_line_width = axis_line_width
larva_bt_plot.xaxis.axis_line_width = axis_line_width
larva_bt_plot.yaxis.axis_label_text_font_size = axis_font_size
larva_bt_plot.xaxis.axis_label_text_font_size = axis_font_size
larva_bt_plot.yaxis.major_label_text_font_size = axis_tick_font_size
larva_bt_plot.xaxis.major_label_text_font_size = axis_tick_font_size
larva_bt_plot.ygrid.grid_line_width = grid_line_width
larva_bt_plot.xgrid.grid_line_width = grid_line_width

print('{} Running Survival not Bt simulations'.format(datetime.datetime.now()))
larva_not_bt = []
for num in range(trials):
    print('    {} Running Trial: {}'.format(datetime.datetime.now(), num))
    simulator_not_bt = Simulator(initial_pops, 0)
    simulator_not_bt.run(t)
    dataframes_not_bt = simulator_not_bt.simulation.agents.dataframes()
    larva_not_bt.append(dataframes_not_bt['(0, 0)_larva'])

larva_not_bt_mean = mean_data(larva_not_bt)

larva_not_bt_source = mdl.ColumnDataSource(larva_not_bt_mean)

larva_not_bt_plot = plt.figure(plot_width=plot_width,
                               plot_height=plot_height,
                               y_range=(0, 1050))
larva_not_bt_plot.title.text       = 'Larva on Non-Bt Survival, ' \
                                     'Number of Trials: {}'.format(trials)
larva_not_bt_plot.yaxis.axis_label = 'population'
larva_not_bt_plot.xaxis.axis_label = 'time (days)'

larva_not_bt_plot.line(x='index', y='genotype_resistant',
                       source=larva_not_bt_source,
                       color=colors[0], line_width=line_width,
                       legend='Resistant')
larva_not_bt_plot.line(x='index', y='genotype_susceptible',
                       source=larva_not_bt_source,
                       color=colors[1], line_width=line_width,
                       legend='Susceptible')
if use_hetero:
    larva_not_bt_plot.line(x='index', y='genotype_heterozygous',
                           source=larva_not_bt_source,
                           color=colors[2], line_width=line_width,
                           legend='Heterozygous')

larva_not_bt_plot.legend.location = 'top_right'

larva_not_bt_plot.title.text_font_size = title_font_size
larva_not_bt_plot.legend.label_text_font_size = legend_font_size
larva_not_bt_plot.yaxis.axis_line_width = axis_line_width
larva_not_bt_plot.xaxis.axis_line_width = axis_line_width
larva_not_bt_plot.yaxis.axis_label_text_font_size = axis_font_size
larva_not_bt_plot.xaxis.axis_label_text_font_size = axis_font_size
larva_not_bt_plot.yaxis.major_label_text_font_size = axis_tick_font_size
larva_not_bt_plot.xaxis.major_label_text_font_size = axis_tick_font_size
larva_not_bt_plot.ygrid.grid_line_width = grid_line_width
larva_not_bt_plot.xgrid.grid_line_width = grid_line_width

larva_plot = plt.figure(plot_width=plot_width,
                           plot_height=plot_height,
                           y_range=(0, 1050))
larva_plot.title.text       = 'Larva Survival, ' \
                                 'Number of Trials: {}'.format(trials)
larva_plot.yaxis.axis_label = 'population'
larva_plot.xaxis.axis_label = 'time (days)'

larva_plot.line(x='index', y='genotype_resistant',
                   source=larva_low_bt_source,
                   color=colors[0], line_width=line_width,
                   legend='Bt Low Resistant')
larva_plot.line(x='index', y='genotype_susceptible',
                   source=larva_low_bt_source,
                   color=colors[1], line_width=line_width,
                   legend='Bt Low Susceptible')
if use_hetero:
    larva_plot.line(x='index', y='genotype_heterozygous',
                       source=larva_low_bt_source,
                       color=colors[2], line_width=line_width,
                       legend='Bt Low Heterozygous')

larva_plot.line(x='index', y='genotype_resistant',
                   source=larva_mid_bt_source,
                   color=colors[0], line_width=line_width,
                   line_dash='dashed',
                   legend='Bt Intermediate Resistant')
larva_plot.line(x='index', y='genotype_susceptible',
                   source=larva_mid_bt_source,
                   color=colors[1], line_width=line_width,
                   line_dash='dashed',
                   legend='Bt Intermediate Susceptible')
if use_hetero:
    larva_plot.line(x='index', y='genotype_heterozygous',
                       source=larva_mid_bt_source,
                       color=colors[2], line_width=line_width,
                       line_dash='dashed',
                       legend='Bt Intermediate Heterozygous')

larva_plot.line(x='index', y='genotype_resistant',
                   source=larva_high_bt_source,
                   color=colors[0], line_width=line_width,
                   line_dash='dashdot',
                   legend='Bt High Resistant')
larva_plot.line(x='index', y='genotype_susceptible',
                   source=larva_high_bt_source,
                   color=colors[1], line_width=line_width,
                   line_dash='dashdot',
                   legend='Bt High Susceptible')
if use_hetero:
    larva_plot.line(x='index', y='genotype_heterozygous',
                       source=larva_high_bt_source,
                       color=colors[2], line_width=line_width,
                       line_dash='dashdot',
                       legend='Bt High Heterozygous')

larva_plot.line(x='index', y='genotype_resistant',
                source=larva_not_bt_source,
                color=colors[0], line_width=line_width,
                line_dash='dotted',
                legend='Non-Bt Resistant')
larva_plot.line(x='index', y='genotype_susceptible',
                source=larva_not_bt_source,
                color=colors[1], line_width=line_width,
                line_dash='dotted',
                legend='Non-Bt Susceptible')
if use_hetero:
    larva_plot.line(x='index', y='genotype_heterozygous',
                    source=larva_not_bt_source,
                    color=colors[2], line_width=line_width,
                    line_dash='dotted',
                    legend='Non-Bt Heterozygous')

larva_plot.legend.location = 'top_right'

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

layout = lay.column(egg_plot, pupa_plot, adult_plot,
                    larva_low_bt_plot, larva_mid_bt_plot, larva_high_bt_plot,
                    larva_bt_plot, larva_not_bt_plot, larva_plot)
plt.show(layout)
