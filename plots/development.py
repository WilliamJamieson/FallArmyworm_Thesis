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

import models.development  as dev
import models.forage       as forage
import models.growth       as growth
import models.init_biomass as init_bio
import models.reproduction as repro

import source.hint    as hint
import source.keyword as keyword

import source.simulation.simulation as main_simulation


# Plotting parameters
trials     = 1000
dominance  = 0
num_steps  = 45

num_steps_eggs = 10
num_eggs       = 10

num_steps_larvae = 40
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

colors    = palettes.Colorblind[3]
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

    grid        = [(keyword.hexagon, 1, 1, True),
                   (keyword.hexagon, 1, 1, True)]
    attrs       = {1: tracking.genotype_attrs}
    data        = (np.inf,)
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
                    forage.adlibitum(1),
                    sex_model,
                    dev.egg_dev(param.mu_egg_dev,
                                param.sig_egg_dev),
                    dev.pupa_dev(param.mu_pupa_dev,
                                 param.sig_pupa_dev),
                    dev.larva_dev(param.mu_larva_dev_ss + 16,
                                  param.mu_larva_dev_rr + 31,
                                  param.sig_larva_dev_ss,
                                  param.sig_larva_dev_rr,
                                  dominance)]
    input_variables = param.repro_values

    nums:       hint.init_pops
    bt_prop:    float
    steps:      hint.step_tuples
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

    def collect(self) -> dict:
        """
        Collect a list of masses

        Returns:
            list of all masses in system
        """

        larvae = self.simulation.agents.agents(keyword.pupa)

        values = {
            keyword.homo_r: [],
            keyword.hetero: [],
            keyword.homo_s: [],
        }

        for agent in larvae:
            # noinspection PyUnresolvedReferences
            values[agent.genotype].append(agent.mass)

        return values

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


t            = list(range(num_steps_eggs))
initial_pops = ((num_eggs,   num_eggs,   num_eggs),
                (0,          0,          0),
                (0,          0,          0),
                (0,          0,          0),
                (0,          0,          0))
steps_egg = [({keyword.egg: [keyword.develop,
                             keyword.advance_age]},)]
print('{} Running Development Egg simulations'.
      format(datetime.datetime.now()))
egg_egg   = []
egg_larva = []
for num in range(trials):
    print('    {} Running Trial: {}'.format(datetime.datetime.now(), num))
    simulator_egg = Simulator(initial_pops, 1, steps_egg)
    simulator_egg.run(t)
    dataframes_egg = simulator_egg.simulation.agents.dataframes()
    egg_egg.  append(dataframes_egg['(0, 0)_egg'])
    egg_larva.append(dataframes_egg['(0, 0)_larva'])

egg_egg_mean   = mean_data(egg_egg)
egg_larva_mean = mean_data(egg_larva)

egg_egg_source   = mdl.ColumnDataSource(egg_egg_mean)
egg_larva_source = mdl.ColumnDataSource(egg_larva_mean)

egg_plot = plt.figure(plot_width=plot_width,
                      plot_height=plot_height)
egg_plot.title.text       = 'Egg Development, Number of Trials: {}'.\
    format(trials)
egg_plot.yaxis.axis_label = 'population'
egg_plot.xaxis.axis_label = 'time (days)'

egg_plot.line(x='index', y='genotype_resistant',
              source=egg_egg_source,
              color=colors[0], line_width=line_width,
              legend='Resistant Egg')
egg_plot.line(x='index', y='genotype_susceptible',
              source=egg_egg_source,
              color=colors[1], line_width=line_width,
              legend='Susceptible Egg')
if use_hetero:
    egg_plot.line(x='index', y='genotype_heterozygous',
                  source=egg_egg_source,
                  color=colors[2], line_width=line_width,
                  legend='Heterozygous Egg')

egg_plot.line(x='index', y='genotype_resistant',
              source=egg_larva_source,
              color=colors[0], line_dash='dashed', line_width=line_width,
              legend='Resistant Larva')
egg_plot.line(x='index', y='genotype_susceptible',
              source=egg_larva_source,
              color=colors[1], line_dash='dashed', line_width=line_width,
              legend='Susceptible Larva')
if use_hetero:
    egg_plot.line(x='index', y='genotype_heterozygous',
                  source=egg_larva_source,
                  color=colors[2], line_dash='dashed', line_width=line_width,
                  legend='Heterozygous Larva')

egg_plot.legend.location = 'center_right'

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

t            = list(range(num_steps_larvae))
initial_pops = ((0,          0,          0),
                (num_larvae, num_larvae, num_larvae),
                (0,          0,          0),
                (0,          0,          0),
                (0,          0,          0))
steps_larva = [({keyword.larva:  [keyword.consume,
                                  keyword.grow,
                                  keyword.develop,
                                  keyword.advance_age,
                                  keyword.reset]},)]
print('{} Running Development Larva simulations'.
      format(datetime.datetime.now()))
larva_larva = []
larva_pupa  = []
pupa_mass_homo_r = []
pupa_mass_hetero = []
pupa_mass_homo_s = []
for num in range(trials):
    print('    {} Running Trial: {}'.format(datetime.datetime.now(), num))
    simulator_larva = Simulator(initial_pops, 1, steps_larva)
    simulator_larva.run(t)

    pupa_mass = simulator_larva.collect()
    pupa_mass_homo_r.extend(pupa_mass[keyword.homo_r])
    pupa_mass_hetero.extend(pupa_mass[keyword.hetero])
    pupa_mass_homo_s.extend(pupa_mass[keyword.homo_s])

    dataframes_larva = simulator_larva.simulation.agents.dataframes()
    larva_larva.append(dataframes_larva['(0, 0)_larva'])
    larva_pupa. append(dataframes_larva['(0, 0)_pupa'])

larva_larva_mean = mean_data(larva_larva)
larva_pupa_mean  = mean_data(larva_pupa)


larva_larva_source = mdl.ColumnDataSource(larva_larva_mean)
larva_pupa_source  = mdl.ColumnDataSource(larva_pupa_mean)

larva_plot = plt.figure(plot_width=plot_width,
                        plot_height=plot_height)
larva_plot.title.text       = 'Larva Development, Number of Trials: {}'.\
    format(trials)
larva_plot.yaxis.axis_label = 'population'
larva_plot.xaxis.axis_label = 'time (days)'

larva_plot.line(x='index', y='genotype_resistant',
                source=larva_larva_source,
                color=colors[0], line_width=line_width,
                legend='Resistant Larva')
larva_plot.line(x='index', y='genotype_susceptible',
                source=larva_larva_source,
                color=colors[1], line_width=line_width,
                legend='Susceptible Larva')
if use_hetero:
    larva_plot.line(x='index', y='genotype_heterozygous',
                    source=larva_larva_source,
                    color=colors[2], line_width=line_width,
                    legend='Heterozygous Larva')

larva_plot.line(x='index', y='genotype_resistant',
                source=larva_pupa_source,
                color=colors[0], line_dash='dashed', line_width=line_width,
                legend='Resistant Pupa')
larva_plot.line(x='index', y='genotype_susceptible',
                source=larva_pupa_source,
                color=colors[1], line_dash='dashed', line_width=line_width,
                legend='Susceptible Pupa')
if use_hetero:
    larva_plot.line(x='index', y='genotype_heterozygous',
                    source=larva_pupa_source,
                    color=colors[2], line_dash='dashed', line_width=line_width,
                    legend='Heterozygous Pupa')

larva_plot.legend.location = 'center_right'

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


# layout = lay.column(egg_plot, larva_plot)
# plt.show(layout)


# Create a histogram of the pupation mass data
hist_homo_r, edges_homo_r = np.histogram(pupa_mass_homo_r,
                                         density=hist_density,
                                         bins=mass_bins)
hist_hetero, edges_hetero = np.histogram(pupa_mass_hetero,
                                         density=hist_density,
                                         bins=mass_bins)
hist_homo_s, edges_homo_s = np.histogram(pupa_mass_homo_s,
                                         density=hist_density,
                                         bins=mass_bins)

num_homo_r = len(pupa_mass_homo_r)
mu_homo_r  = np.mean(pupa_mass_homo_r)
sig_homo_r = np.std( pupa_mass_homo_r)

num_hetero = len(pupa_mass_hetero)
mu_hetero  = np.mean(pupa_mass_hetero)
sig_hetero = np.std( pupa_mass_hetero)

num_homo_s = len(pupa_mass_homo_s)
mu_homo_s  = np.mean(pupa_mass_homo_s)
sig_homo_s = np.std( pupa_mass_homo_s)

hist_plot = plt.figure(plot_width=plot_width,
                       plot_height=plot_height)
hist_plot.title.text       = 'Pupation Mass Histogram'
hist_plot.yaxis.axis_label = 'pupa per mass'
hist_plot.xaxis.axis_label = 'mass (mg)'

hist_plot.quad(top=hist_homo_r, bottom=0,
               left=edges_homo_r[:-1],
               right=edges_homo_r[1:],
               fill_color=colors[0],
               line_color='white',
               alpha=alpha,
               legend='Resistant, (μ={}, σ={}, n={})'.
                   format(np.round(mu_homo_r, digits),
                          np.round(sig_homo_r, digits),
                          num_homo_r))
hist_plot.quad(top=hist_homo_s, bottom=0,
               left=edges_homo_s[:-1],
               right=edges_homo_s[1:],
               fill_color=colors[1],
               line_color='white',
               alpha=alpha,
               legend='Susceptible, (μ={}, σ={}, n={})'.
                   format(np.round(mu_homo_s, digits),
                          np.round(sig_homo_s, digits),
                          num_homo_s))
if use_hetero:
    hist_plot.quad(top=hist_hetero, bottom=0,
                   left=edges_hetero[:-1],
                   right=edges_hetero[1:],
                   fill_color=colors[2],
                   line_color='white',
                   alpha=alpha,
                   legend='Heterozygous, (μ={}, σ={}, n={})'.
                   format(np.round(mu_hetero, digits),
                          np.round(sig_hetero, digits),
                          num_hetero))

hist_plot.legend.location = 'top_left'

hist_plot.title.text_font_size = title_font_size
hist_plot.legend.label_text_font_size = legend_font_size
hist_plot.yaxis.axis_line_width = axis_line_width
hist_plot.xaxis.axis_line_width = axis_line_width
hist_plot.yaxis.axis_label_text_font_size = axis_font_size
hist_plot.xaxis.axis_label_text_font_size = axis_font_size
hist_plot.yaxis.major_label_text_font_size = axis_tick_font_size
hist_plot.xaxis.major_label_text_font_size = axis_tick_font_size
hist_plot.ygrid.grid_line_width = grid_line_width
hist_plot.xgrid.grid_line_width = grid_line_width


# layout = lay.column(egg_plot, larva_plot, hist_plot)
# plt.show(layout)


t            = list(range(num_steps_pupae))
initial_pops = ((0,          0,          0),
                (0,          0,          0),
                (num_pupae, num_pupae, num_pupae),
                (0,          0,          0),
                (0,          0,          0))
steps_pupa = [({keyword.pupa:  [keyword.develop,
                                keyword.advance_age]},)]
print('{} Running Development Pupa simulations'.
      format(datetime.datetime.now()))
pupa_pupa  = []
pupa_adult = []
for num in range(trials):
    print('    {} Running Trial: {}'.format(datetime.datetime.now(), num))
    simulator_pupa = Simulator(initial_pops, 1, steps_pupa)
    simulator_pupa.run(t)
    dataframes_pupa = simulator_pupa.simulation.agents.dataframes()
    pupa_pupa.append(dataframes_pupa['(0, 0)_pupa'])
    pupa_adult.append(dataframes_pupa['(0, 0)_female'])

pupa_pupa_mean  = mean_data(pupa_pupa)
pupa_adult_mean = mean_data(pupa_adult)

pupa_pupa_source  = mdl.ColumnDataSource(pupa_pupa_mean)
pupa_adult_source = mdl.ColumnDataSource(pupa_adult_mean)

pupa_plot = plt.figure(plot_width=plot_width,
                       plot_height=plot_height)
pupa_plot.title.text       = 'Pupa Development, Number of Trials: {}'.\
    format(trials)
pupa_plot.yaxis.axis_label = 'population'
pupa_plot.xaxis.axis_label = 'time (days)'

pupa_plot.line(x='index', y='genotype_resistant',
               source=pupa_pupa_source,
               color=colors[0], line_width=line_width,
               legend='Resistant Pupa')
pupa_plot.line(x='index', y='genotype_susceptible',
               source=pupa_pupa_source,
               color=colors[1], line_width=line_width,
               legend='Susceptible Pupa')
if use_hetero:
    pupa_plot.line(x='index', y='genotype_heterozygous',
                   source=pupa_pupa_source,
                   color=colors[2], line_width=line_width,
                   legend='Heterozygous Pupa')

pupa_plot.line(x='index', y='genotype_resistant',
               source=pupa_adult_source,
               color=colors[0], line_dash='dashed', line_width=line_width,
               legend='Resistant Adult')
pupa_plot.line(x='index', y='genotype_susceptible',
               source=pupa_adult_source,
               color=colors[1], line_dash='dashed', line_width=line_width,
               legend='Susceptible Adult')
if use_hetero:
    pupa_plot.line(x='index', y='genotype_heterozygous',
                   source=pupa_adult_source,
                   color=colors[2], line_dash='dashed', line_width=line_width,
                   legend='Heterozygous Adult')

pupa_plot.legend.location = 'center_right'

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


# layout = lay.column(egg_plot, larva_plot, pupa_plot, hist_plot)
# plt.show(layout)


t              = list(range(num_steps))
initial_pops = ((num_eggs,   num_eggs,   num_eggs),
                (0,          0,          0),
                (0,          0,          0),
                (0,          0,          0),
                (0,          0,          0))
steps_full = [({keyword.egg:   [keyword.develop,
                                keyword.advance_age],
                keyword.larva: [keyword.consume,
                                keyword.grow,
                                keyword.develop,
                                keyword.advance_age,
                                keyword.reset],
                keyword.pupa:  [keyword.develop,
                                keyword.advance_age]},)]
print('{} Running Development Full simulations'.
      format(datetime.datetime.now()))
full_egg   = []
full_larva = []
full_pupa  = []
full_adult = []
for num in range(trials):
    print('    {} Running Trial: {}'.format(datetime.datetime.now(), num))
    simulator_full = Simulator(initial_pops, 1, steps_full)
    simulator_full.run(t)
    dataframes_full = simulator_full.simulation.agents.dataframes()
    full_egg.  append(dataframes_full['(0, 0)_egg'])
    full_larva.append(dataframes_full['(0, 0)_larva'])
    full_pupa. append(dataframes_full['(0, 0)_pupa'])
    full_adult.append(dataframes_full['(0, 0)_female'])

full_egg_mean   = mean_data(full_egg)
full_larva_mean = mean_data(full_larva)
full_pupa_mean  = mean_data(full_pupa)
full_adult_mean = mean_data(full_adult)

full_egg_source   = mdl.ColumnDataSource(full_egg_mean)
full_larva_source = mdl.ColumnDataSource(full_larva_mean)
full_pupa_source  = mdl.ColumnDataSource(full_pupa_mean)
full_adult_source = mdl.ColumnDataSource(full_adult_mean)

full_plot = plt.figure(plot_width=plot_width,
                       plot_height=plot_height)
full_plot.title.text       = 'Full Life-Cycle Development, ' \
                             'Number of Trials: {}'.format(trials)
full_plot.yaxis.axis_label = 'population'
full_plot.xaxis.axis_label = 'time (days)'

full_plot.line(x='index', y='genotype_resistant',
               source=full_egg_source,
               color=colors[0], line_width=line_width,
               legend='Resistant Egg')
full_plot.line(x='index', y='genotype_susceptible',
               source=full_egg_source,
               color=colors[1], line_width=line_width,
               legend='Susceptible Egg')
if use_hetero:
    full_plot.line(x='index', y='genotype_heterozygous',
                   source=full_egg_source,
                   color=colors[2], line_width=line_width,
                   legend='Heterozygous Egg')

full_plot.line(x='index', y='genotype_resistant',
               source=full_larva_source,
               color=colors[0], line_dash='dashed', line_width=line_width,
               legend='Resistant Larva')
full_plot.line(x='index', y='genotype_susceptible',
               source=full_larva_source,
               color=colors[1], line_dash='dashed', line_width=line_width,
               legend='Susceptible Larva')
if use_hetero:
    full_plot.line(x='index', y='genotype_heterozygous',
                   source=full_larva_source,
                   color=colors[2], line_dash='dashed', line_width=line_width,
                   legend='Heterozygous Larva')

full_plot.line(x='index', y='genotype_resistant',
               source=full_pupa_source,
               color=colors[0], line_dash='dotted', line_width=line_width,
               legend='Resistant Pupa')
full_plot.line(x='index', y='genotype_susceptible',
               source=full_pupa_source,
               color=colors[1], line_dash='dotted', line_width=line_width,
               legend='Susceptible Pupa')
if use_hetero:
    full_plot.line(x='index', y='genotype_heterozygous',
                   source=full_pupa_source,
                   color=colors[2], line_dash='dotted', line_width=line_width,
                   legend='Heterozygous Pupa')

full_plot.line(x='index', y='genotype_resistant',
               source=full_adult_source,
               color=colors[0], line_dash='dashdot', line_width=line_width,
               legend='Resistant Adult')
full_plot.line(x='index', y='genotype_susceptible',
               source=full_adult_source,
               color=colors[1], line_dash='dashdot', line_width=line_width,
               legend='Susceptible Adult')
if use_hetero:
    full_plot.line(x='index', y='genotype_heterozygous',
                   source=full_adult_source,
                   color=colors[2], line_dash='dashdot', line_width=line_width,
                   legend='Heterozygous Adult')

full_plot.legend.location = 'center_right'

full_plot.title.text_font_size = title_font_size
full_plot.legend.label_text_font_size = legend_font_size
full_plot.yaxis.axis_line_width = axis_line_width
full_plot.xaxis.axis_line_width = axis_line_width
full_plot.yaxis.axis_label_text_font_size = axis_font_size
full_plot.xaxis.axis_label_text_font_size = axis_font_size
full_plot.yaxis.major_label_text_font_size = axis_tick_font_size
full_plot.xaxis.major_label_text_font_size = axis_tick_font_size
full_plot.ygrid.grid_line_width = grid_line_width
full_plot.xgrid.grid_line_width = grid_line_width


layout = lay.column(egg_plot, larva_plot, pupa_plot, full_plot, hist_plot)
plt.show(layout)
