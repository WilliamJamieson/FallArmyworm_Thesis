import datetime
import dataclasses       as dclass
import numpy             as np
# import matplotlib.pyplot as plt

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
dominance  = 0
num_steps  = 40

num_steps_eggs = 10
num_eggs       = 10

num_steps_larvae = 30
num_larvae       = 1000
mass_bins        = 100
digits           = 3

num_steps_pupae = 15
num_pupae       = 1000

use_hetero = False

plot_width  = 800
plot_height = 500

colors    = palettes.Set1[3]
save_file = 'biomass_plots.html'

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
    # steps       = [({keyword.larva:  [keyword.consume,
    #                                   keyword.grow,
    #                                   keyword.develop,
    #                                   keyword.reset],
    #                  keyword.egg:    [keyword.develop],
    #                  keyword.pupa:   [keyword.develop]},)]
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
                    dev.larva_dev(param.mu_larva_dev_ss,
                                  param.mu_larva_dev_rr,
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

    def collect(self) -> list:
        """
        Collect a list of masses

        Returns:
            list of all masses in system
        """

        larvae = self.simulation.agents.agents(keyword.pupa)

        values = []
        for agent in larvae:
            # noinspection PyUnresolvedReferences
            values.append(agent.mass)

        return values

    def run(self, times: list) -> None:
        """
        Run the simulation for each time

        Args:
            times: the times for the simulation

        Returns:
            biomass data
        """

        for time in times[1:]:
            print('     {} Running step: {}'.
                  format(datetime.datetime.now(), time))
            self.simulation.step()


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
simulator_egg = Simulator(initial_pops, 1, steps_egg)
simulator_egg.run(t)
dataframes_egg = simulator_egg.simulation.agents.dataframes()
egg_egg   = dataframes_egg['(0, 0)_egg']
egg_larva = dataframes_egg['(0, 0)_larva']

egg_egg[  'index'] = range(len(egg_egg.index))
egg_larva['index'] = range(len(egg_larva.index))

egg_egg_source   = mdl.ColumnDataSource(egg_egg)
egg_larva_source = mdl.ColumnDataSource(egg_larva)

egg_plot = plt.figure(plot_width=plot_width,
                      plot_height=plot_height)
egg_plot.title.text       = 'Egg Development'
egg_plot.yaxis.axis_label = 'population'
egg_plot.xaxis.axis_label = 'time (days)'

egg_plot.line(x='index', y='genotype_resistant',
              source=egg_egg_source,
              color=colors[0],
              legend='Resistant Egg')
if use_hetero:
    egg_plot.line(x='index', y='genotype_heterozygous',
                  source=egg_egg_source,
                  color=colors[1],
                  legend='Heterozygous Egg')
egg_plot.line(x='index', y='genotype_susceptible',
              source=egg_egg_source,
              color=colors[2],
              legend='Susceptible Egg')

egg_plot.line(x='index', y='genotype_resistant',
              source=egg_larva_source,
              color=colors[0], line_dash='dashed',
              legend='Resistant Larva')
if use_hetero:
    egg_plot.line(x='index', y='genotype_heterozygous',
                  source=egg_larva_source,
                  color=colors[1], line_dash='dashed',
                  legend='Heterozygous Larva')
egg_plot.line(x='index', y='genotype_susceptible',
              source=egg_larva_source,
              color=colors[2], line_dash='dashed',
              legend='Susceptible Larva')

egg_plot.legend.location = 'center_right'


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
simulator_larva = Simulator(initial_pops, 1, steps_larva)
simulator_larva.run(t)

pupa_mass = simulator_larva.collect()
pupa_mass_homo_r = pupa_mass[:num_larvae]
pupa_mass_hetero = pupa_mass[num_larvae: 2*num_larvae]
pupa_mass_homo_s = pupa_mass[2*num_larvae:]

dataframes_larva = simulator_larva.simulation.agents.dataframes()
larva_larva = dataframes_larva['(0, 0)_larva']
larva_pupa  = dataframes_larva['(0, 0)_pupa']

larva_larva['index'] = range(len(larva_larva.index))
larva_pupa[ 'index'] = range(len(larva_pupa.index))

larva_larva_source = mdl.ColumnDataSource(larva_larva)
larva_pupa_source  = mdl.ColumnDataSource(larva_pupa)

larva_plot = plt.figure(plot_width=plot_width,
                        plot_height=plot_height)
larva_plot.title.text       = 'Larva Development'
larva_plot.yaxis.axis_label = 'population'
larva_plot.xaxis.axis_label = 'time (days)'

larva_plot.line(x='index', y='genotype_resistant',
                source=larva_larva_source,
                color=colors[0],
                legend='Resistant Larva')
if use_hetero:
    larva_plot.line(x='index', y='genotype_heterozygous',
                    source=larva_larva_source,
                    color=colors[1],
                    legend='Heterozygous Larva')
larva_plot.line(x='index', y='genotype_susceptible',
                source=larva_larva_source,
                color=colors[2],
                legend='Susceptible Larva')

larva_plot.line(x='index', y='genotype_resistant',
                source=larva_pupa_source,
                color=colors[0], line_dash='dashed',
                legend='Resistant Pupa')
if use_hetero:
    larva_plot.line(x='index', y='genotype_heterozygous',
                    source=larva_pupa_source,
                    color=colors[1], line_dash='dashed',
                    legend='Heterozygous Pupa')
larva_plot.line(x='index', y='genotype_susceptible',
                source=larva_pupa_source,
                color=colors[2], line_dash='dashed',
                legend='Susceptible Pupa')

larva_plot.legend.location = 'center_right'

# Create a histogram of the pupation mass data
hist_homo_r, edges_homo_r = np.histogram(pupa_mass_homo_r,
                                         density=True, bins=mass_bins)
hist_hetero, edges_hetero = np.histogram(pupa_mass_hetero,
                                         density=True, bins=mass_bins)
hist_homo_s, edges_homo_s = np.histogram(pupa_mass_homo_s,
                                         density=True, bins=mass_bins)

mu_homo_r  = np.mean(pupa_mass_homo_r)
sig_homo_r = np.std( pupa_mass_homo_r)
mu_hetero  = np.mean(pupa_mass_hetero)
sig_hetero = np.std( pupa_mass_hetero)
mu_homo_s  = np.mean(pupa_mass_homo_s)
sig_homo_s = np.std( pupa_mass_homo_s)

hist_plot = plt.figure(plot_width=plot_width,
                       plot_height=plot_height)
hist_plot.title.text       = 'Pupation Mass Histogram'
hist_plot.yaxis.axis_label = 'pupa per pass'
hist_plot.xaxis.axis_label = 'mass (mg)'

hist_plot.quad(top=hist_homo_r, bottom=0,
               left=edges_homo_r[:-1],
               right=edges_homo_r[1:],
               fill_color=colors[0],
               legend='Resistant,(μ={}, σ={})'.
                   format(np.round(mu_homo_r, digits),
                          np.round(sig_homo_r, digits)))
if use_hetero:
    hist_plot.quad(top=hist_hetero, bottom=0,
                   left=edges_hetero[:-1],
                   right=edges_hetero[1:],
                   fill_color=colors[1],
                   legend='Heterozygous,(μ={}, σ={})'.
                       format(np.round(mu_hetero, digits),
                              np.round(sig_hetero, digits)))
hist_plot.quad(top=hist_homo_s, bottom=0,
               left=edges_homo_s[:-1],
               right=edges_homo_s[1:],
               fill_color=colors[2],
               legend='Susceptible,(μ={}, σ={})'.
                   format(np.round(mu_homo_s, digits),
                          np.round(sig_homo_s, digits)))

hist_plot.legend.location = 'top_left'


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
simulator_pupa = Simulator(initial_pops, 1, steps_pupa)
simulator_pupa.run(t)
dataframes_pupa = simulator_pupa.simulation.agents.dataframes()
pupa_pupa  = dataframes_pupa['(0, 0)_pupa']
pupa_adult = dataframes_pupa['(0, 0)_female']

pupa_pupa[ 'index'] = range(len(pupa_pupa.index))
pupa_adult['index'] = range(len(pupa_adult.index))

pupa_pupa_source  = mdl.ColumnDataSource(pupa_pupa)
pupa_adult_source = mdl.ColumnDataSource(pupa_adult)

pupa_plot = plt.figure(plot_width=plot_width,
                       plot_height=plot_height)
pupa_plot.title.text       = 'Pupa Development'
pupa_plot.yaxis.axis_label = 'population'
pupa_plot.xaxis.axis_label = 'time (days)'

pupa_plot.line(x='index', y='genotype_resistant',
               source=pupa_pupa_source,
               color=colors[0],
               legend='Resistant Pupa')
if use_hetero:
    pupa_plot.line(x='index', y='genotype_heterozygous',
                   source=pupa_pupa_source,
                   color=colors[1],
                   legend='Heterozygous Pupa')
pupa_plot.line(x='index', y='genotype_susceptible',
               source=pupa_pupa_source,
               color=colors[2],
               legend='Susceptible Pupa')

pupa_plot.line(x='index', y='genotype_resistant',
               source=pupa_adult_source,
               color=colors[0], line_dash='dashed',
               legend='Resistant Adult')
if use_hetero:
    pupa_plot.line(x='index', y='genotype_heterozygous',
                   source=pupa_adult_source,
                   color=colors[1], line_dash='dashed',
                   legend='Heterozygous Adult')
pupa_plot.line(x='index', y='genotype_susceptible',
               source=pupa_adult_source,
               color=colors[2], line_dash='dashed',
               legend='Susceptible Adult')

pupa_plot.legend.location = 'center_right'


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
simulator_full = Simulator(initial_pops, 1, steps_full)
start = datetime.datetime.now()
simulator_full.run(t)
end = datetime.datetime.now()
bt_time = end - start
print('Elapsed time: {}'.format(bt_time))
dataframes_full = simulator_full.simulation.agents.dataframes()
full_egg   = dataframes_full['(0, 0)_egg']
full_larva = dataframes_full['(0, 0)_larva']
full_pupa  = dataframes_full['(0, 0)_pupa']
full_adult = dataframes_full['(0, 0)_female']

full_egg[  'index'] = range(len(full_egg.index))
full_larva['index'] = range(len(full_larva.index))
full_pupa[ 'index'] = range(len(full_pupa.index))
full_adult['index'] = range(len(full_adult.index))

full_egg_source   = mdl.ColumnDataSource(full_egg)
full_larva_source = mdl.ColumnDataSource(full_larva)
full_pupa_source  = mdl.ColumnDataSource(full_pupa)
full_adult_source = mdl.ColumnDataSource(full_adult)

full_plot = plt.figure(plot_width=plot_width,
                       plot_height=plot_height)
full_plot.title.text       = 'Full Life-Cycle Development'
full_plot.yaxis.axis_label = 'population'
full_plot.xaxis.axis_label = 'time (days)'

full_plot.line(x='index', y='genotype_resistant',
               source=full_egg,
               color=colors[0],
               legend='Resistant Egg')
if use_hetero:
    full_plot.line(x='index', y='genotype_heterozygous',
                   source=full_egg,
                   color=colors[1],
                   legend='Heterozygous Egg')
full_plot.line(x='index', y='genotype_susceptible',
               source=full_egg,
               color=colors[2],
               legend='Susceptible Egg')

full_plot.line(x='index', y='genotype_resistant',
               source=full_larva,
               color=colors[0], line_dash='dashed',
               legend='Resistant Larva')
if use_hetero:
    full_plot.line(x='index', y='genotype_heterozygous',
                   source=full_larva,
                   color=colors[1], line_dash='dashed',
                   legend='Heterozygous Larva')
full_plot.line(x='index', y='genotype_susceptible',
               source=full_larva,
               color=colors[2], line_dash='dashed',
               legend='Susceptible Larva')

full_plot.line(x='index', y='genotype_resistant',
               source=full_pupa,
               color=colors[0], line_dash='dotted',
               legend='Resistant Pupa')
if use_hetero:
    full_plot.line(x='index', y='genotype_heterozygous',
                   source=full_pupa,
                   color=colors[1], line_dash='dotted',
                   legend='Heterozygous Pupa')
full_plot.line(x='index', y='genotype_susceptible',
               source=full_pupa,
               color=colors[2], line_dash='dotted',
               legend='Susceptible Pupa')

full_plot.line(x='index', y='genotype_resistant',
               source=full_adult,
               color=colors[0], line_dash='dashdot',
               legend='Resistant Adult')
if use_hetero:
    full_plot.line(x='index', y='genotype_heterozygous',
                   source=full_adult,
                   color=colors[1], line_dash='dashdot',
                   legend='Heterozygous Adult')
full_plot.line(x='index', y='genotype_susceptible',
               source=full_adult,
               color=colors[2], line_dash='dashdot',
               legend='Susceptible Adult')

full_plot.legend.location = 'center_right'


layout = lay.column(egg_plot, larva_plot, pupa_plot, full_plot, hist_plot)
plt.show(layout)
