import datetime
import dataclasses  as dclass
import numpy        as np
import pandas       as pd

import bokeh.plotting as plt
import bokeh.layouts  as lay
import bokeh.palettes as palettes

import parameters.data_tracking    as tracking
import parameters.model_parameters as param

import models.forage       as forage
import models.graph        as graph
import models.growth       as growth
import models.init_biomass as init_bio
import models.movement     as move
import models.reproduction as repro

import source.hint    as hint
import source.keyword as keyword

import source.simulation.simulation as main_simulation


line_width       = 3.5
point_size       = 10
point_size_stoch = 8

axis_line_width     = 2
grid_line_width     = 2
title_font_size     = '16pt'
legend_font_size    = '12pt'
axis_font_size      = '12pt'
axis_tick_font_size = '10pt'


# Plotting parameters
dominance  = 0
trials     = 100

k_lower    = 0.5
k_upper    = 4
num_k      = 8

num_steps  = 10
num_eggs   = 10
num_larvae = 100
save_fig   = True


plot_width  = 800
plot_height = 500

colors    = palettes.Colorblind[8]
save_file = 'cannibalism_plots.html'

plt.output_file(save_file)


@dclass.dataclass
class Simulator(object):
    """
    Class to setup and run a simulation of only biomass growth:

    Variables:
        nums:   initial population numbers
        forage: the plant forage model
    """

    attrs       = {0: tracking.genotype_attrs}
    data        = (np.inf,)
    steps       = [({keyword.larva: [keyword.move,
                                     keyword.consume]}, param.forage_steps),
                   ({keyword.larva: [keyword.grow,
                                     keyword.reset]},)]
    emigration  = []
    immigration = []

    input_variables = param.repro_values

    nums:        hint.init_pops
    bt_prop:     float
    fight_slope: float
    move_scale:  float
    move_shape:  float
    encounter:   float
    field_grid:  int
    plant_grid:  int
    alpha_ss:    float
    alpha_rr:    float
    beta_ss:     float
    beta_rr:     float
    simulation:  hint.simulation = None

    def __post_init__(self):

        grid = self.grid(self.field_grid,
                         self.plant_grid)

        input_models = self.input_models(self.fight_slope,
                                         self.move_scale,
                                         self.move_shape,
                                         self.encounter,
                                         self.alpha_ss,
                                         self.alpha_rr,
                                         self.beta_ss,
                                         self.beta_rr)
        input_models = tuple(input_models)

        self.simulation = main_simulation.Simulation. \
            setup(self.nums,
                  grid,
                  self.attrs,
                  self.data,
                  self.bt_prop,
                  self.steps,
                  self.emigration,
                  self.immigration,
                  *input_models,
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
    def input_models(fight_slope:    float,
                     move_scale:     float,
                     move_shape:     float,
                     encounter_rate: float,
                     alpha_ss:       float,
                     alpha_rr:       float,
                     beta_ss:        float,
                     beta_rr:        float) -> list:
        """
        Create the input models
        Args:
            fight_slope:    slope of a fight
            move_scale:     movement scale parameter
            move_shape:     movement shape parameter
            encounter_rate: encounter rate constant
            alpha_ss:       growth rate ss
            alpha_rr:       growth rate rr
            beta_ss:        cost ss
            beta_rr:        cost rr

        Returns:

        """

        return [
            growth.max_gut(),
            growth.growth(alpha_ss,
                          alpha_rr,
                          beta_ss,
                          beta_rr,
                          dominance),
            init_bio.init_num(param.lam_0_egg),
            init_bio.init_mass(param.mu_0_egg_ss,
                               param.mu_0_egg_rr,
                               param.sig_0_egg_ss,
                               param.sig_0_egg_rr,
                               dominance),
            init_bio.init_juvenile(44.194,
                                   18.947,
                                   0.552,
                                   0.17,
                                   dominance),
            init_bio.init_mature(param.mu_0_mature_ss,
                                 param.mu_0_mature_rr,
                                 param.sig_0_mature_ss,
                                 param.sig_0_mature_rr,
                                 dominance),
            init_bio.init_plant(param.mu_leaf,
                                param.sig_leaf),
            repro.init_sex(param.female_prob),
            move.larva(move_scale,
                       move_shape),
            forage.adlibitum(param.forage_steps),
            forage.egg(param.egg_factor),
            forage.larva(param.larva_factor),
            forage.fight(fight_slope),
            forage.radius(param.cannibalism_radius),
            forage.encounter(encounter_rate)
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
            print('               {} Running step: {}'.
                  format(datetime.datetime.now(), this))
            self.simulation.step()

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

alphas = np.linspace(param.alpha_rr, param.alpha_ss, 5)
betas  = np.linspace(param.beta_rr,  param.beta_ss,  5)

print('{} Running alpha change'.format(datetime.datetime.now()))
alpha_ss_data   = []
alpha_rr_data   = []
alpha_ss_series = []
alpha_rr_series = []
for alpha in alphas:
    print('    {} Running alpha: {}'.format(datetime.datetime.now(), alpha))
    larva_ss_data = []
    larva_rr_data = []
    for num in range(trials):
        print('       {} Running trial: {}'.format(datetime.datetime.now(), num))

        print('           {} Running SS'.format(datetime.datetime.now()))
        simulation = Simulator(initial_pops,
                               1,
                               param.fight_slope,
                               param.larva_scale,
                               param.larva_shape,
                               param.cannibalism_encounter,
                               1,
                               10,
                               alpha,
                               param.alpha_rr,
                               param.beta_ss,
                               param.beta_rr)
        larva_ss_data.append(simulation.run(t))

        print('           {} Running RR'.format(datetime.datetime.now()))
        simulation = Simulator(initial_pops,
                               1,
                               param.fight_slope,
                               param.larva_scale,
                               param.larva_shape,
                               param.cannibalism_encounter,
                               1,
                               10,
                               param.alpha_ss,
                               alpha,
                               param.beta_ss,
                               param.beta_rr)
        larva_rr_data.append(simulation.run(t))

    alpha_ss_data.append(pd.concat(larva_ss_data).groupby(level=0).
                         mean()['percent'].iat[-1])
    alpha_rr_data.append(pd.concat(larva_rr_data).groupby(level=0).
                         mean()['percent'].iat[-1])
    alpha_ss_series.append(pd.concat(larva_ss_data).groupby(level=0).mean())
    alpha_rr_series.append(pd.concat(larva_rr_data).groupby(level=0).mean())

alpha_plot = plt.figure(plot_width=plot_width,
                        plot_height=plot_height,
                        y_range=(0, 1))
alpha_plot.title.text       = 'Resistant Allele Frequency'
alpha_plot.yaxis.axis_label = '% resistant'
alpha_plot.xaxis.axis_label = 'α'

alpha_plot.line(alphas, alpha_ss_data,
                  color=colors[0], line_width=line_width,
                  legend='SS with β={}'.format(np.round(param.beta_ss, 3)))

alpha_plot.line(alphas, alpha_rr_data,
                color=colors[1], line_width=line_width,
                legend='RR with β={}'.format(np.round(param.beta_rr), 3))

alpha_plot.title.text_font_size = title_font_size
alpha_plot.yaxis.axis_line_width = axis_line_width
alpha_plot.xaxis.axis_line_width = axis_line_width
alpha_plot.yaxis.axis_label_text_font_size = axis_font_size
alpha_plot.xaxis.axis_label_text_font_size = axis_font_size
alpha_plot.yaxis.major_label_text_font_size = axis_tick_font_size
alpha_plot.xaxis.major_label_text_font_size = axis_tick_font_size
alpha_plot.ygrid.grid_line_width = grid_line_width
alpha_plot.xgrid.grid_line_width = grid_line_width

alpha_ss_plot = plt.figure(plot_width=plot_width,
                           plot_height=plot_height,
                           y_range=(0, 1))
alpha_ss_plot.title.text       = 'Resistant Allele Frequency, β={}'. \
    format(np.round(param.beta_ss, 3))
alpha_ss_plot.yaxis.axis_label = '% resistant'
alpha_ss_plot.xaxis.axis_label = 'time (days)'

alpha_ss_plot.line(t, alpha_ss_series[0]['percent'],
                   color=colors[0], line_width=line_width,
                   legend='α: {}'.format(np.round(alphas[0], 3)))

alpha_ss_plot.line(t, alpha_ss_series[1]['percent'],
                   color=colors[1], line_width=line_width,
                   legend='α: {}'.format(np.round(alphas[1], 3)))

alpha_ss_plot.line(t, alpha_ss_series[2]['percent'],
                   color=colors[2], line_width=line_width,
                   legend='α: {}'.format(np.round(alphas[2], 3)))

alpha_ss_plot.line(t, alpha_ss_series[3]['percent'],
                   color=colors[3], line_width=line_width,
                   legend='α: {}'.format(np.round(alphas[3], 3)))

alpha_ss_plot.line(t, alpha_ss_series[4]['percent'],
                   color=colors[4], line_width=line_width,
                   legend='α: {}'.format(np.round(alphas[4], 3)))

alpha_ss_plot.legend.location = "top_left"

alpha_ss_plot.title.text_font_size = title_font_size
alpha_ss_plot.legend.label_text_font_size = legend_font_size
alpha_ss_plot.yaxis.axis_line_width = axis_line_width
alpha_ss_plot.xaxis.axis_line_width = axis_line_width
alpha_ss_plot.yaxis.axis_label_text_font_size = axis_font_size
alpha_ss_plot.xaxis.axis_label_text_font_size = axis_font_size
alpha_ss_plot.yaxis.major_label_text_font_size = axis_tick_font_size
alpha_ss_plot.xaxis.major_label_text_font_size = axis_tick_font_size
alpha_ss_plot.ygrid.grid_line_width = grid_line_width
alpha_ss_plot.xgrid.grid_line_width = grid_line_width

alpha_rr_plot = plt.figure(plot_width=plot_width,
                           plot_height=plot_height,
                           y_range=(0, 1))
alpha_rr_plot.title.text       = 'Resistant Allele Frequency, β={}'. \
    format(np.round(param.beta_rr, 3))
alpha_rr_plot.yaxis.axis_label = '% resistant'
alpha_rr_plot.xaxis.axis_label = 'time (days)'

alpha_rr_plot.line(t, alpha_rr_series[0]['percent'],
                   color=colors[0], line_width=line_width,
                   legend='α: {}'.format(np.round(alphas[0], 3)))

alpha_rr_plot.line(t, alpha_rr_series[1]['percent'],
                   color=colors[1], line_width=line_width,
                   legend='α: {}'.format(np.round(alphas[1], 3)))

alpha_rr_plot.line(t, alpha_rr_series[2]['percent'],
                   color=colors[2], line_width=line_width,
                   legend='α: {}'.format(np.round(alphas[2], 3)))

alpha_rr_plot.line(t, alpha_rr_series[3]['percent'],
                   color=colors[3], line_width=line_width,
                   legend='α: {}'.format(np.round(alphas[3], 3)))

alpha_rr_plot.line(t, alpha_rr_series[4]['percent'],
                   color=colors[4], line_width=line_width,
                   legend='α: {}'.format(np.round(alphas[4], 3)))

alpha_rr_plot.legend.location = "top_left"

alpha_rr_plot.title.text_font_size = title_font_size
alpha_rr_plot.legend.label_text_font_size = legend_font_size
alpha_rr_plot.yaxis.axis_line_width = axis_line_width
alpha_rr_plot.xaxis.axis_line_width = axis_line_width
alpha_rr_plot.yaxis.axis_label_text_font_size = axis_font_size
alpha_rr_plot.xaxis.axis_label_text_font_size = axis_font_size
alpha_rr_plot.yaxis.major_label_text_font_size = axis_tick_font_size
alpha_rr_plot.xaxis.major_label_text_font_size = axis_tick_font_size
alpha_rr_plot.ygrid.grid_line_width = grid_line_width
alpha_rr_plot.xgrid.grid_line_width = grid_line_width

# layout = lay.column(alpha_plot)
# plt.show(layout)

print('{} Running beta change'.format(datetime.datetime.now()))
beta_ss_data   = []
beta_rr_data   = []
beta_ss_series = []
beta_rr_series = []
for beta in betas:
    print('    {} Running beta: {}'.format(datetime.datetime.now(), beta))
    larva_ss_data = []
    larva_rr_data = []
    for num in range(trials):
        print('       {} Running trial: {}'.format(datetime.datetime.now(), num))

        print('           {} Running SS'.format(datetime.datetime.now()))
        simulation = Simulator(initial_pops,
                               1,
                               param.fight_slope,
                               param.larva_scale,
                               param.larva_shape,
                               param.cannibalism_encounter,
                               1,
                               10,
                               param.alpha_ss,
                               param.alpha_rr,
                               beta,
                               param.beta_rr)
        larva_ss_data.append(simulation.run(t))

        print('           {} Running RR'.format(datetime.datetime.now()))
        simulation = Simulator(initial_pops,
                               1,
                               param.fight_slope,
                               param.larva_scale,
                               param.larva_shape,
                               param.cannibalism_encounter,
                               1,
                               10,
                               param.alpha_ss,
                               param.alpha_rr,
                               param.beta_ss,
                               beta)
        larva_rr_data.append(simulation.run(t))

    beta_ss_data.append(pd.concat(larva_ss_data).groupby(level=0).
                        mean()['percent'].iat[-1])
    beta_rr_data.append(pd.concat(larva_rr_data).groupby(level=0).
                        mean()['percent'].iat[-1])
    beta_ss_series.append(pd.concat(larva_ss_data).groupby(level=0).mean())
    beta_rr_series.append(pd.concat(larva_rr_data).groupby(level=0).mean())

beta_plot = plt.figure(plot_width=plot_width,
                       plot_height=plot_height,
                       y_range=(0, 1))
beta_plot.title.text       = 'Resistant Allele Frequency'
beta_plot.yaxis.axis_label = '% resistant'
beta_plot.xaxis.axis_label = 'β'

beta_plot.line(betas, beta_ss_data,
                color=colors[0], line_width=line_width,
                legend='SS with α={}'.format(np.round(param.alpha_ss, 3)))

beta_plot.line(betas, beta_rr_data,
               color=colors[1], line_width=line_width,
               legend='RR with α={}'.format(np.round(param.alpha_rr, 3)))

beta_plot.title.text_font_size = title_font_size
beta_plot.yaxis.axis_line_width = axis_line_width
beta_plot.xaxis.axis_line_width = axis_line_width
beta_plot.yaxis.axis_label_text_font_size = axis_font_size
beta_plot.xaxis.axis_label_text_font_size = axis_font_size
beta_plot.yaxis.major_label_text_font_size = axis_tick_font_size
beta_plot.xaxis.major_label_text_font_size = axis_tick_font_size
beta_plot.ygrid.grid_line_width = grid_line_width
beta_plot.xgrid.grid_line_width = grid_line_width

beta_ss_plot = plt.figure(plot_width=plot_width,
                          plot_height=plot_height,
                          y_range=(0, 1))
beta_ss_plot.title.text       = 'Resistant Allele Frequency, α={}'.\
    format(np.round(param.alpha_ss, 3))
beta_ss_plot.yaxis.axis_label = '% resistant'
beta_ss_plot.xaxis.axis_label = 'time (days)'

beta_ss_plot.line(t, beta_ss_series[0]['percent'],
                  color=colors[0], line_width=line_width,
                  legend='β: {}'.format(np.round(betas[0], 3)))

beta_ss_plot.line(t, beta_ss_series[1]['percent'],
                  color=colors[1], line_width=line_width,
                  legend='β: {}'.format(np.round(betas[1], 3)))

beta_ss_plot.line(t, beta_ss_series[2]['percent'],
                  color=colors[2], line_width=line_width,
                  legend='β: {}'.format(np.round(betas[2], 3)))

beta_ss_plot.line(t, beta_ss_series[3]['percent'],
                  color=colors[3], line_width=line_width,
                  legend='β: {}'.format(np.round(betas[3], 3)))

beta_ss_plot.line(t, beta_ss_series[4]['percent'],
                  color=colors[4], line_width=line_width,
                  legend='β: {}'.format(np.round(betas[4], 3)))

beta_ss_plot.legend.location = "top_left"

beta_ss_plot.title.text_font_size = title_font_size
beta_ss_plot.legend.label_text_font_size = legend_font_size
beta_ss_plot.yaxis.axis_line_width = axis_line_width
beta_ss_plot.xaxis.axis_line_width = axis_line_width
beta_ss_plot.yaxis.axis_label_text_font_size = axis_font_size
beta_ss_plot.xaxis.axis_label_text_font_size = axis_font_size
beta_ss_plot.yaxis.major_label_text_font_size = axis_tick_font_size
beta_ss_plot.xaxis.major_label_text_font_size = axis_tick_font_size
beta_ss_plot.ygrid.grid_line_width = grid_line_width
beta_ss_plot.xgrid.grid_line_width = grid_line_width

beta_rr_plot = plt.figure(plot_width=plot_width,
                          plot_height=plot_height,
                          y_range=(0, 1))
beta_rr_plot.title.text       = 'Resistant Allele Frequency, α={}'. \
    format(np.round(param.alpha_rr, 3))
beta_rr_plot.yaxis.axis_label = '% resistant'
beta_rr_plot.xaxis.axis_label = 'time (days)'

beta_rr_plot.line(t, beta_rr_series[0]['percent'],
                  color=colors[0], line_width=line_width,
                  legend='β: {}'.format(np.round(betas[0], 3)))

beta_rr_plot.line(t, beta_rr_series[1]['percent'],
                  color=colors[1], line_width=line_width,
                  legend='β: {}'.format(np.round(betas[1], 3)))

beta_rr_plot.line(t, beta_rr_series[2]['percent'],
                  color=colors[2], line_width=line_width,
                  legend='β: {}'.format(np.round(betas[2], 3)))

beta_rr_plot.line(t, beta_rr_series[3]['percent'],
                  color=colors[3], line_width=line_width,
                  legend='β: {}'.format(np.round(betas[3], 3)))

beta_rr_plot.line(t, beta_rr_series[4]['percent'],
                  color=colors[4], line_width=line_width,
                  legend='β: {}'.format(np.round(betas[4], 3)))

beta_rr_plot.legend.location = "top_left"

beta_rr_plot.title.text_font_size = title_font_size
beta_rr_plot.legend.label_text_font_size = legend_font_size
beta_rr_plot.yaxis.axis_line_width = axis_line_width
beta_rr_plot.xaxis.axis_line_width = axis_line_width
beta_rr_plot.yaxis.axis_label_text_font_size = axis_font_size
beta_rr_plot.xaxis.axis_label_text_font_size = axis_font_size
beta_rr_plot.yaxis.major_label_text_font_size = axis_tick_font_size
beta_rr_plot.xaxis.major_label_text_font_size = axis_tick_font_size
beta_rr_plot.ygrid.grid_line_width = grid_line_width
beta_rr_plot.xgrid.grid_line_width = grid_line_width

# # layout = lay.column(alpha_plot, beta_plot)
# # plt.show(layout)

k_values = np.array([0.25, 0.3, 0.4, 0.5, 0.75])
print('{} Running fight change'.format(datetime.datetime.now()))
fight_data   = []
fight_series = []
for k_value in k_values:
    print('    {} Running Slope: {}'.format(datetime.datetime.now(), k_value))
    larva_data = []
    for num in range(trials):
        print('       {} Running trial: {}'.format(datetime.datetime.now(), num))

        print('           {} Running fight'.format(datetime.datetime.now()))
        simulation = Simulator(initial_pops,
                               1,
                               k_value,
                               param.larva_scale,
                               param.larva_shape,
                               param.cannibalism_encounter,
                               1,
                               10,
                               param.alpha_ss,
                               param.alpha_rr,
                               param.beta_ss,
                               param.beta_rr)
        larva_data.append(simulation.run(t))
    fight_data.append(pd.concat(larva_data).groupby(level=0).
                        mean()['percent'].iat[-1])
    fight_series.append(pd.concat(larva_data).groupby(level=0).mean())

fight_plot = plt.figure(plot_width=plot_width,
                        plot_height=plot_height,
                        y_range=(0, 1))
fight_plot.title.text       = 'Resistant Allele Frequency'
fight_plot.yaxis.axis_label = '% resistant'
fight_plot.xaxis.axis_label = 'k'

fight_plot.line(k_values, fight_data,
                color=colors[0], line_width=line_width)

fight_plot.title.text_font_size = title_font_size
fight_plot.yaxis.axis_line_width = axis_line_width
fight_plot.xaxis.axis_line_width = axis_line_width
fight_plot.yaxis.axis_label_text_font_size = axis_font_size
fight_plot.xaxis.axis_label_text_font_size = axis_font_size
fight_plot.yaxis.major_label_text_font_size = axis_tick_font_size
fight_plot.xaxis.major_label_text_font_size = axis_tick_font_size
fight_plot.ygrid.grid_line_width = grid_line_width
fight_plot.xgrid.grid_line_width = grid_line_width

fight_series_plot = plt.figure(plot_width=plot_width,
                               plot_height=plot_height,
                               y_range=(0, 1))
fight_series_plot.title.text       = 'Resistant Allele Frequency'
fight_series_plot.yaxis.axis_label = '% resistant'
fight_series_plot.xaxis.axis_label = 'time (days)'

fight_series_plot.line(t, fight_series[0]['percent'],
                       color=colors[0], line_width=line_width,
                       legend='k: {}'.format(np.round(k_values[0], 3)))

fight_series_plot.line(t, fight_series[1]['percent'],
                       color=colors[1], line_width=line_width,
                       legend='k: {}'.format(np.round(k_values[1], 3)))

fight_series_plot.line(t, fight_series[2]['percent'],
                       color=colors[2], line_width=line_width,
                       legend='k: {}'.format(np.round(k_values[2], 3)))

fight_series_plot.line(t, fight_series[3]['percent'],
                       color=colors[3], line_width=line_width,
                       legend='k: {}'.format(np.round(k_values[3], 3)))

fight_series_plot.line(t, fight_series[4]['percent'],
                       color=colors[4], line_width=line_width,
                       legend='k: {}'.format(np.round(k_values[4], 3)))

fight_series_plot.legend.location = "top_left"

fight_series_plot.title.text_font_size = title_font_size
fight_series_plot.legend.label_text_font_size = legend_font_size
fight_series_plot.yaxis.axis_line_width = axis_line_width
fight_series_plot.xaxis.axis_line_width = axis_line_width
fight_series_plot.yaxis.axis_label_text_font_size = axis_font_size
fight_series_plot.xaxis.axis_label_text_font_size = axis_font_size
fight_series_plot.yaxis.major_label_text_font_size = axis_tick_font_size
fight_series_plot.xaxis.major_label_text_font_size = axis_tick_font_size
fight_series_plot.ygrid.grid_line_width = grid_line_width
fight_series_plot.xgrid.grid_line_width = grid_line_width

# layout = lay.column(alpha_plot, beta_plot, fight_plot)
# plt.show(layout)

grid_sizes = [1, 2, 4, 8, 10, 25]
print('{} Running grid change'.format(datetime.datetime.now()))
grid_data   = []
grid_series = []
for grid_size in grid_sizes:
    print('    {} Running Grid Size: {}'.format(datetime.datetime.now(),
                                                grid_size))
    larva_data = []
    for num in range(trials):
        print('       {} Running trial: {}'.format(datetime.datetime.now(), num))

        print('           {} Running grid'.format(datetime.datetime.now()))
        simulation = Simulator(initial_pops,
                               1,
                               param.fight_slope,
                               param.larva_scale,
                               param.larva_shape,
                               param.cannibalism_encounter,
                               1,
                               grid_size,
                               param.alpha_ss,
                               param.alpha_rr,
                               param.beta_ss,
                               param.beta_rr)
        larva_data.append(simulation.run(t))
    grid_data.append(pd.concat(larva_data).groupby(level=0).
                      mean()['percent'].iat[-1])
    grid_series.append(pd.concat(larva_data).groupby(level=0).mean())

grid_plot = plt.figure(plot_width=plot_width,
                        plot_height=plot_height,
                        y_range=(0, 1))
grid_plot.title.text       = 'Resistant Allele Frequency'
grid_plot.yaxis.axis_label = '% resistant'
grid_plot.xaxis.axis_label = 'grid size'

grid_plot.line(grid_sizes, grid_data,
               color=colors[0], line_width=line_width)

grid_plot.title.text_font_size = title_font_size
grid_plot.yaxis.axis_line_width = axis_line_width
grid_plot.xaxis.axis_line_width = axis_line_width
grid_plot.yaxis.axis_label_text_font_size = axis_font_size
grid_plot.xaxis.axis_label_text_font_size = axis_font_size
grid_plot.yaxis.major_label_text_font_size = axis_tick_font_size
grid_plot.xaxis.major_label_text_font_size = axis_tick_font_size
grid_plot.ygrid.grid_line_width = grid_line_width
grid_plot.xgrid.grid_line_width = grid_line_width

grid_series_plot = plt.figure(plot_width=plot_width,
                                 plot_height=plot_height,
                                 y_range=(0, 1))
grid_series_plot.title.text       = 'Resistant Allele Frequency'
grid_series_plot.yaxis.axis_label = '% resistant'
grid_series_plot.xaxis.axis_label = 'time (days)'

grid_series_plot.line(t, grid_series[0]['percent'],
                         color=colors[0], line_width=line_width,
                         legend='Side: {}'.format(np.round(grid_sizes[0], 3)))

grid_series_plot.line(t, grid_series[1]['percent'],
                         color=colors[1], line_width=line_width,
                         legend='Side: {}'.format(np.round(grid_sizes[1], 3)))

grid_series_plot.line(t, grid_series[2]['percent'],
                         color=colors[2], line_width=line_width,
                         legend='Side: {}'.format(np.round(grid_sizes[2], 3)))

grid_series_plot.line(t, grid_series[3]['percent'],
                         color=colors[3], line_width=line_width,
                         legend='Side: {}'.format(np.round(grid_sizes[3], 3)))

grid_series_plot.line(t, grid_series[4]['percent'],
                         color=colors[4], line_width=line_width,
                         legend='Side: {}'.format(np.round(grid_sizes[4], 3)))

grid_series_plot.line(t, grid_series[5]['percent'],
                      color=colors[5], line_width=line_width,
                      legend='Side: {}'.format(np.round(grid_sizes[5], 3)))

grid_series_plot.legend.location = "top_left"

grid_series_plot.title.text_font_size = title_font_size
grid_series_plot.legend.label_text_font_size = legend_font_size
grid_series_plot.yaxis.axis_line_width = axis_line_width
grid_series_plot.xaxis.axis_line_width = axis_line_width
grid_series_plot.yaxis.axis_label_text_font_size = axis_font_size
grid_series_plot.xaxis.axis_label_text_font_size = axis_font_size
grid_series_plot.yaxis.major_label_text_font_size = axis_tick_font_size
grid_series_plot.xaxis.major_label_text_font_size = axis_tick_font_size
grid_series_plot.ygrid.grid_line_width = grid_line_width
grid_series_plot.xgrid.grid_line_width = grid_line_width

# layout = lay.column(fight_plot, grid_plot)
# plt.show(layout)

encounters = [param.cannib_0,
              param.cannib_1,
              param.cannib_2,
              param.cannib_3,
              param.cannib_4]
print('{} Running Encounter'.format(datetime.datetime.now()))
encount_data   = []
encount_series = []
for encounter in encounters:
    print('    {} Running rho: {}'.format(datetime.datetime.now(),
                                                encounter))
    larva_data = []
    for num in range(trials):
        print('       {} Running trial: {}'.format(datetime.datetime.now(), num))

        print('           {} Running encounter'.format(datetime.datetime.now()))
        simulation = Simulator(initial_pops,
                               1,
                               param.fight_slope,
                               param.larva_scale,
                               param.larva_shape,
                               encounter,
                               1,
                               10,
                               param.alpha_ss,
                               param.alpha_rr,
                               param.beta_ss,
                               param.beta_rr)
        larva_data.append(simulation.run(t))
    encount_data.append(pd.concat(larva_data).groupby(level=0).
                        mean()['percent'].iat[-1])
    encount_series.append(pd.concat(larva_data).groupby(level=0).mean())

encount_plot = plt.figure(plot_width=plot_width,
                          plot_height=plot_height,
                          y_range=(0, 1))
encount_plot.title.text       = 'Resistant Allele Frequency'
encount_plot.yaxis.axis_label = '% resistant'
encount_plot.xaxis.axis_label = 'ρ'

encount_plot.line(encounters, encount_data,
                  color=colors[0], line_width=line_width)

encount_plot.title.text_font_size = title_font_size
encount_plot.yaxis.axis_line_width = axis_line_width
encount_plot.xaxis.axis_line_width = axis_line_width
encount_plot.yaxis.axis_label_text_font_size = axis_font_size
encount_plot.xaxis.axis_label_text_font_size = axis_font_size
encount_plot.yaxis.major_label_text_font_size = axis_tick_font_size
encount_plot.xaxis.major_label_text_font_size = axis_tick_font_size
encount_plot.ygrid.grid_line_width = grid_line_width
encount_plot.xgrid.grid_line_width = grid_line_width

encount_series_plot = plt.figure(plot_width=plot_width,
                                 plot_height=plot_height,
                                 y_range=(0, 1))
encount_series_plot.title.text       = 'Resistant Allele Frequency'
encount_series_plot.yaxis.axis_label = '% resistant'
encount_series_plot.xaxis.axis_label = 'time (days)'

encount_series_plot.line(t, encount_series[0]['percent'],
                         color=colors[0], line_width=line_width,
                         legend='ρ={}'.format(np.round(encounters[0], 3)))

encount_series_plot.line(t, encount_series[1]['percent'],
                         color=colors[1], line_width=line_width,
                         legend='ρ={}'.format(np.round(encounters[1], 3)))

encount_series_plot.line(t, encount_series[2]['percent'],
                         color=colors[2], line_width=line_width,
                         legend='ρ={}'.format(np.round(encounters[2], 3)))

encount_series_plot.line(t, encount_series[3]['percent'],
                         color=colors[3], line_width=line_width,
                         legend='ρ={}'.format(np.round(encounters[3], 3)))

encount_series_plot.line(t, encount_series[4]['percent'],
                         color=colors[4], line_width=line_width,
                         legend='ρ={}'.format(np.round(encounters[4], 3)))

encount_series_plot.legend.location = "top_left"

encount_series_plot.title.text_font_size = title_font_size
encount_series_plot.legend.label_text_font_size = legend_font_size
encount_series_plot.yaxis.axis_line_width = axis_line_width
encount_series_plot.xaxis.axis_line_width = axis_line_width
encount_series_plot.yaxis.axis_label_text_font_size = axis_font_size
encount_series_plot.xaxis.axis_label_text_font_size = axis_font_size
encount_series_plot.yaxis.major_label_text_font_size = axis_tick_font_size
encount_series_plot.xaxis.major_label_text_font_size = axis_tick_font_size
encount_series_plot.ygrid.grid_line_width = grid_line_width
encount_series_plot.xgrid.grid_line_width = grid_line_width

layout = lay.column(encount_plot, encount_series_plot,
                    grid_plot,    grid_series_plot,
                    fight_plot,   fight_series_plot,
                    alpha_plot,   alpha_ss_plot, alpha_rr_plot,
                    beta_plot,    beta_ss_plot,  beta_rr_plot)
plt.show(layout)
