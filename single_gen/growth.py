import datetime
import dataclasses as dclass
import numpy       as np
import scipy.stats as stats

import bokeh.plotting as plt
import bokeh.layouts  as lay
import bokeh.models   as mdl
import bokeh.palettes as palettes

import parameters.basic_data       as base_data
import parameters.data_tracking    as tracking
import parameters.model_parameters as param

import models.forage       as forage
import models.growth       as growth
import models.init_biomass as init_bio
import models.reproduction as repro

import source.hint    as hint
import source.keyword as keyword

import source.simulation.simulation as main_simulation


# Plotting parameters
trials     = 1000
num_steps  = 40
use_hetero = True

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

colors    = palettes.Colorblind[8]
save_file = 'growth_plots.html'

plt.output_file(save_file)

grow = np.linspace(param.alpha_rr, param.alpha_ss, 5)

grow_0 = grow[0]
grow_1 = grow[1]
grow_2 = grow[2]
grow_3 = grow[3]
grow_4 = grow[4]

cost = np.linspace(param.beta_rr, param.beta_ss, 5)

cost_0 = cost[0]
cost_1 = cost[1]
cost_2 = cost[2]
cost_3 = cost[3]
cost_4 = cost[4]


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
    attrs       = {0: tracking.genotype_attrs}
    data        = (np.inf,)
    emigration  = []
    immigration = []

    input_variables = param.repro_values

    nums:       hint.init_pops
    bt_prop:    float
    forage:     hint.forage_plant
    alpha_ss:   float
    alpha_rr:   float
    beta_ss:    float
    beta_rr:    float
    dominance:  float
    steps:      list            = None
    simulation: hint.simulation = None

    def __post_init__(self):
        input_models = self.input_models(self.alpha_ss,
                                         self.alpha_rr,
                                         self.beta_ss,
                                         self.beta_rr,
                                         self.dominance)

        input_models.append(self.forage)
        inputs = tuple(input_models)

        if self.steps is None:
            self.steps = [({keyword.larva: [keyword.consume,
                                            keyword.grow,
                                            keyword.reset]},)]

        self.simulation = main_simulation.Simulation.\
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
    def input_models(alpha_ss: float,
                     alpha_rr: float,
                     beta_ss: float,
                     beta_rr: float,
                     dominance: float) -> list:
        """
        Setup the input models

        Args:
            alpha_ss: growth constant ss
            alpha_rr: growth constant rr
            beta_ss:  cost   constant ss
            beta_rr:  cost   constant rr
            dominance: dominance degree

        Returns:
            input models
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
            repro.init_sex(param.female_prob)
        ]

    def collect(self) -> list:
        """
        Collect a list of masses

        Returns:
            list of all masses in system
        """

        larvae = self.simulation.agents.agents(keyword.larva)

        values = []
        for agent in larvae:
            # noinspection PyUnresolvedReferences
            values.append(agent.mass)

        return values

    def run(self, times: list) -> np.ndarray:
        """
        Run the simulation for each time

        Args:
            times: the times for the simulation

        Returns:
            biomass data
        """

        data = [self.collect()]

        for time in times[1:]:
            print('     {} Running step: {}'.
                  format(datetime.datetime.now(), time))
            self.simulation.step()
            data.append(self.collect())

        return np.array(data)


def extract_data(data: np.ndarray) -> tuple:
    """
    Extract the basic stats from the data

    Args:
        data: list of list of biomass

    Returns:
        (mean, std, min, max, sem, sem_lower, sem_upper, q_lower, q_upper)
    """

    mean  = np.mean(data, axis=1)
    std   = np.std( data, axis=1)
    lower = np.amin(data, axis=1)
    upper = np.amax(data, axis=1)

    sem       = stats.sem(data, axis=1)
    sem_lower = mean - sem*1.96
    sem_upper = mean + sem*1.96

    q_lower = np.percentile(data,  2.5, axis=1)
    q_upper = np.percentile(data, 97.5, axis=1)

    return mean, std, lower, upper, sem, sem_lower, sem_upper, q_lower, q_upper


fin_point_rr = (
    base_data.growth_times_rr[1] - base_data.growth_times_sem_rr[1],
    base_data.growth_mass_rr[ 1] + base_data.growth_mass_sem_rr[ 1]
)
fin_point_ss = (
    base_data.growth_times_ss[1] - base_data.growth_times_sem_ss[1],
    base_data.growth_mass_ss[ 1] + base_data.growth_mass_sem_ss[ 1]
)


fin_time_homo_r = mdl.Span(location=fin_point_rr[0],
                           dimension='height',
                           line_color=colors[0], line_width=line_width,
                           line_dash='dotted')
fin_mass_homo_r = mdl.Span(location=fin_point_rr[1],
                           dimension='width',
                           line_color=colors[0], line_width=line_width,
                           line_dash='dotted')

fin_time_homo_s = mdl.Span(location=fin_point_ss[0],
                           dimension='height',
                           line_color=colors[1], line_width=line_width,
                           line_dash='dotted')
fin_mass_homo_s = mdl.Span(location=fin_point_ss[1],
                           dimension='width',
                           line_color=colors[1], line_width=line_width,
                           line_dash='dotted')

t = list(range(num_steps))
initial_pops = ((0, 0, 0),
                (1, 1, 1),
                (0, 0, 0),
                (0, 0, 0),
                (0, 0, 0))
print('{} Running Dominance: {}'.format(datetime.datetime.now(),
                                        param.dominance_0))
simulator_dom_0 = Simulator(initial_pops,
                            1,
                            forage.adlibitum(1),
                            param.alpha_ss,
                            param.alpha_rr,
                            param.beta_ss,
                            param.beta_rr,
                            param.dominance_0)
bio_dom_0        = simulator_dom_0.run(t)
bio_dom_0_homo_r = bio_dom_0[:, 0]
bio_dom_0_hetero = bio_dom_0[:, 1]
bio_dom_0_homo_s = bio_dom_0[:, 2]
print('{} Running Dominance: {}'.format(datetime.datetime.now(),
                                        param.dominance_1))
simulator_dom_1 = Simulator(initial_pops,
                            1,
                            forage.adlibitum(1),
                            param.alpha_ss,
                            param.alpha_rr,
                            param.beta_ss,
                            param.beta_rr,
                            param.dominance_1)
bio_dom_1        = simulator_dom_1.run(t)
bio_dom_1_homo_r = bio_dom_1[:, 0]
bio_dom_1_hetero = bio_dom_1[:, 1]
bio_dom_1_homo_s = bio_dom_1[:, 2]
print('{} Running Dominance: {}'.format(datetime.datetime.now(),
                                        param.dominance_2))
simulator_dom_2 = Simulator(initial_pops,
                            1,
                            forage.adlibitum(1),
                            param.alpha_ss,
                            param.alpha_rr,
                            param.beta_ss,
                            param.beta_rr,
                            param.dominance_2)
bio_dom_2        = simulator_dom_2.run(t)
bio_dom_2_homo_r = bio_dom_2[:, 0]
bio_dom_2_hetero = bio_dom_2[:, 1]
bio_dom_2_homo_s = bio_dom_2[:, 2]

dom_plot = plt.figure(plot_width=plot_width,
                      plot_height=plot_height)
dom_plot.title.text       = 'Growth with Different Dominance D'
dom_plot.yaxis.axis_label = 'biomass (mg)'
dom_plot.xaxis.axis_label = 'time (days)'

dom_plot.add_layout(fin_time_homo_r)
dom_plot.add_layout(fin_mass_homo_r)
dom_plot.add_layout(fin_time_homo_s)
dom_plot.add_layout(fin_mass_homo_s)

dom_plot.line(t, bio_dom_0_homo_r,
              color=colors[0], line_width=line_width,
              legend='Resistant')
dom_plot.triangle(t, bio_dom_0_homo_r,
                  color=colors[0], size=point_size,
                  legend='Resistant')

dom_plot.line(t, bio_dom_0_homo_s,
              color=colors[1], line_width=line_width,
              legend='Susceptible')
dom_plot.circle(t, bio_dom_0_homo_s,
                color=colors[1], size=point_size,
                legend='Susceptible')

dom_plot.line(t, bio_dom_0_hetero,
              color=colors[2], line_width=line_width,
              legend='Heterozygous, D={}'.format(param.dominance_0))

dom_plot.line(t, bio_dom_1_hetero,
              color=colors[3], line_width=line_width,
              line_dash='dashed',
              legend='Heterozygous, D={}'.format(param.dominance_1))

dom_plot.line(t, bio_dom_2_hetero,
              color=colors[4], line_width=line_width,
              line_dash='dotted',
              legend='Heterozygous, D={}'.format(param.dominance_2))

dom_plot.square_x([fin_point_rr[0]],
                  [fin_point_rr[1]],
                  color=colors[0], size=20,
                  fill_color=None, line_width=line_width,
                  legend='Resistant Pupation')
dom_plot.square_x([fin_point_ss[0]],
                  [fin_point_ss[1]],
                  color=colors[1], size=20,
                  fill_color=None, line_width=line_width,
                  legend='Susceptible Pupation')

dom_plot.legend.location = "bottom_right"

dom_plot.title.text_font_size = title_font_size
dom_plot.legend.label_text_font_size = legend_font_size
dom_plot.yaxis.axis_line_width = axis_line_width
dom_plot.xaxis.axis_line_width = axis_line_width
dom_plot.yaxis.axis_label_text_font_size = axis_font_size
dom_plot.xaxis.axis_label_text_font_size = axis_font_size
dom_plot.yaxis.major_label_text_font_size = axis_tick_font_size
dom_plot.xaxis.major_label_text_font_size = axis_tick_font_size
dom_plot.ygrid.grid_line_width = grid_line_width
dom_plot.xgrid.grid_line_width = grid_line_width

print('{} Running Growth Rate: {}'.format(datetime.datetime.now(),
                                          grow_0))
simulator_grow_0 = Simulator(initial_pops,
                             1,
                             forage.adlibitum(1),
                             grow_0,
                             grow_0,
                             param.beta_ss,
                             param.beta_rr,
                             param.dominance_0)
bio_grow_0        = simulator_grow_0.run(t)
bio_grow_0_homo_r = bio_grow_0[:, 0]
bio_grow_0_hetero = bio_grow_0[:, 1]
bio_grow_0_homo_s = bio_grow_0[:, 2]

print('{} Running Growth Rate: {}'.format(datetime.datetime.now(),
                                          grow_1))
simulator_grow_1 = Simulator(initial_pops,
                             1,
                             forage.adlibitum(1),
                             grow_1,
                             grow_1,
                             param.beta_ss,
                             param.beta_rr,
                             param.dominance_0)
bio_grow_1        = simulator_grow_1.run(t)
bio_grow_1_homo_r = bio_grow_1[:, 0]
bio_grow_1_hetero = bio_grow_1[:, 1]
bio_grow_1_homo_s = bio_grow_1[:, 2]

print('{} Running Growth Rate: {}'.format(datetime.datetime.now(),
                                          grow_2))
simulator_grow_2 = Simulator(initial_pops,
                             1,
                             forage.adlibitum(1),
                             grow_2,
                             grow_2,
                             param.beta_ss,
                             param.beta_rr,
                             param.dominance_0)
bio_grow_2        = simulator_grow_2.run(t)
bio_grow_2_homo_r = bio_grow_2[:, 0]
bio_grow_2_hetero = bio_grow_2[:, 1]
bio_grow_2_homo_s = bio_grow_2[:, 2]

print('{} Running Growth Rate: {}'.format(datetime.datetime.now(),
                                          grow_3))
simulator_grow_3 = Simulator(initial_pops,
                             1,
                             forage.adlibitum(1),
                             grow_3,
                             grow_3,
                             param.beta_ss,
                             param.beta_rr,
                             param.dominance_0)
bio_grow_3        = simulator_grow_3.run(t)
bio_grow_3_homo_r = bio_grow_3[:, 0]
bio_grow_3_hetero = bio_grow_3[:, 1]
bio_grow_3_homo_s = bio_grow_3[:, 2]

print('{} Running Growth Rate: {}'.format(datetime.datetime.now(),
                                          grow_4))
simulator_grow_4 = Simulator(initial_pops,
                             1,
                             forage.adlibitum(1),
                             grow_4,
                             grow_4,
                             param.beta_ss,
                             param.beta_rr,
                             param.dominance_0)
bio_grow_4        = simulator_grow_4.run(t)
bio_grow_4_homo_r = bio_grow_4[:, 0]
bio_grow_4_hetero = bio_grow_4[:, 1]
bio_grow_4_homo_s = bio_grow_4[:, 2]

grow_ss_plot = plt.figure(plot_width=plot_width,
                          plot_height=plot_height)
grow_ss_plot.title.text       = 'Growth with Different Growth Rates, β={}'.\
    format(np.round(param.beta_ss, 3))
grow_ss_plot.yaxis.axis_label = 'biomass (mg)'
grow_ss_plot.xaxis.axis_label = 'time (days)'

grow_ss_plot.add_layout(fin_time_homo_r)
grow_ss_plot.add_layout(fin_mass_homo_r)
grow_ss_plot.add_layout(fin_time_homo_s)
grow_ss_plot.add_layout(fin_mass_homo_s)

grow_ss_plot.line(t, bio_grow_0_homo_s,
                  color=colors[0], line_width=line_width,
                  legend='α={}'.format(np.round(grow_0, 3)))
grow_ss_plot.triangle(t, bio_grow_0_homo_s,
                      color=colors[0], size=point_size,
                      legend='α={}'.format(np.round(grow_0, 3)))

grow_ss_plot.line(t, bio_grow_1_homo_s,
                  color=colors[2], line_width=line_width,
                  legend='α={}'.format(np.round(grow_1, 3)))

grow_ss_plot.line(t, bio_grow_2_homo_s,
                  color=colors[3], line_width=line_width,
                  line_dash='dashed',
                  legend='α={}'.format(np.round(grow_2, 3)))

grow_ss_plot.line(t, bio_grow_3_homo_s,
                  color=colors[4], line_width=line_width,
                  line_dash='dotted',
                  legend='α={}'.format(np.round(grow_3, 3)))

grow_ss_plot.line(t, bio_grow_4_homo_s,
                  color=colors[1], line_width=line_width,
                  legend='α={}'.format(np.round(grow_4, 3)))
grow_ss_plot.circle(t, bio_grow_4_homo_s,
                    color=colors[1], size=point_size,
                    legend='α={}'.format(np.round(grow_4, 3)))

grow_ss_plot.legend.location = "top_left"

grow_ss_plot.title.text_font_size = title_font_size
grow_ss_plot.legend.label_text_font_size = legend_font_size
grow_ss_plot.yaxis.axis_line_width = axis_line_width
grow_ss_plot.xaxis.axis_line_width = axis_line_width
grow_ss_plot.yaxis.axis_label_text_font_size = axis_font_size
grow_ss_plot.xaxis.axis_label_text_font_size = axis_font_size
grow_ss_plot.yaxis.major_label_text_font_size = axis_tick_font_size
grow_ss_plot.xaxis.major_label_text_font_size = axis_tick_font_size
grow_ss_plot.ygrid.grid_line_width = grid_line_width
grow_ss_plot.xgrid.grid_line_width = grid_line_width

grow_rr_plot = plt.figure(plot_width=plot_width,
                          plot_height=plot_height)
grow_rr_plot.title.text       = 'Growth with Different Growth Rates, β={}'. \
    format(np.round(param.beta_rr, 3))
grow_rr_plot.yaxis.axis_label = 'biomass (mg)'
grow_rr_plot.xaxis.axis_label = 'time (days)'

grow_rr_plot.add_layout(fin_time_homo_r)
grow_rr_plot.add_layout(fin_mass_homo_r)
grow_rr_plot.add_layout(fin_time_homo_s)
grow_rr_plot.add_layout(fin_mass_homo_s)

grow_rr_plot.line(t, bio_grow_0_homo_r,
                  color=colors[0], line_width=line_width,
                  legend='α={}'.format(np.round(grow_0, 3)))
grow_rr_plot.triangle(t, bio_grow_0_homo_r,
                      color=colors[0], size=point_size,
                      legend='α={}'.format(np.round(grow_0, 3)))

grow_rr_plot.line(t, bio_grow_1_homo_r,
                  color=colors[2], line_width=line_width,
                  legend='α={}'.format(np.round(grow_1, 3)))

grow_rr_plot.line(t, bio_grow_2_homo_r,
                  color=colors[3], line_width=line_width,
                  line_dash='dashed',
                  legend='α={}'.format(np.round(grow_2, 3)))

grow_rr_plot.line(t, bio_grow_3_homo_r,
                  color=colors[4], line_width=line_width,
                  line_dash='dotted',
                  legend='α={}'.format(np.round(grow_3, 3)))

grow_rr_plot.line(t, bio_grow_4_homo_r,
                  color=colors[1], line_width=line_width,
                  legend='α={}'.format(np.round(grow_4, 3)))
grow_rr_plot.circle(t, bio_grow_4_homo_r,
                    color=colors[1], size=point_size,
                    legend='α={}'.format(np.round(grow_4, 3)))

grow_rr_plot.legend.location = "top_left"

grow_rr_plot.title.text_font_size = title_font_size
grow_rr_plot.legend.label_text_font_size = legend_font_size
grow_rr_plot.yaxis.axis_line_width = axis_line_width
grow_rr_plot.xaxis.axis_line_width = axis_line_width
grow_rr_plot.yaxis.axis_label_text_font_size = axis_font_size
grow_rr_plot.xaxis.axis_label_text_font_size = axis_font_size
grow_rr_plot.yaxis.major_label_text_font_size = axis_tick_font_size
grow_rr_plot.xaxis.major_label_text_font_size = axis_tick_font_size
grow_rr_plot.ygrid.grid_line_width = grid_line_width
grow_rr_plot.xgrid.grid_line_width = grid_line_width

print('{} Running Growth Rate: {}'.format(datetime.datetime.now(),
                                          cost_0))
simulator_cost_0 = Simulator(initial_pops,
                             1,
                             forage.adlibitum(1),
                             param.alpha_ss,
                             param.alpha_rr,
                             cost_0,
                             cost_0,
                             param.dominance_0)
bio_cost_0        = simulator_cost_0.run(t)
bio_cost_0_homo_r = bio_cost_0[:, 0]
bio_cost_0_hetero = bio_cost_0[:, 1]
bio_cost_0_homo_s = bio_cost_0[:, 2]

print('{} Running Maintenance Cost: {}'.format(datetime.datetime.now(),
                                               cost_1))
simulator_cost_1 = Simulator(initial_pops,
                             1,
                             forage.adlibitum(1),
                             param.alpha_ss,
                             param.alpha_rr,
                             cost_1,
                             cost_1,
                             param.dominance_0)
bio_cost_1        = simulator_cost_1.run(t)
bio_cost_1_homo_r = bio_cost_1[:, 0]
bio_cost_1_hetero = bio_cost_1[:, 1]
bio_cost_1_homo_s = bio_cost_1[:, 2]

print('{} Running Maintenance Cost: {}'.format(datetime.datetime.now(),
                                               cost_2))
simulator_cost_2 = Simulator(initial_pops,
                             1,
                             forage.adlibitum(1),
                             param.alpha_ss,
                             param.alpha_rr,
                             cost_2,
                             cost_2,
                             param.dominance_0)
bio_cost_2        = simulator_cost_2.run(t)
bio_cost_2_homo_r = bio_cost_2[:, 0]
bio_cost_2_hetero = bio_cost_2[:, 1]
bio_cost_2_homo_s = bio_cost_2[:, 2]

print('{} Running Maintenance Cost: {}'.format(datetime.datetime.now(),
                                               cost_3))
simulator_cost_3 = Simulator(initial_pops,
                             1,
                             forage.adlibitum(1),
                             param.alpha_ss,
                             param.alpha_rr,
                             cost_3,
                             cost_3,
                             param.dominance_0)
bio_cost_3        = simulator_cost_3.run(t)
bio_cost_3_homo_r = bio_cost_3[:, 0]
bio_cost_3_hetero = bio_cost_3[:, 1]
bio_cost_3_homo_s = bio_cost_3[:, 2]

print('{} Running Maintenance Cost: {}'.format(datetime.datetime.now(),
                                               cost_4))
simulator_cost_4 = Simulator(initial_pops,
                             1,
                             forage.adlibitum(1),
                             param.alpha_ss,
                             param.alpha_rr,
                             cost_4,
                             cost_4,
                             param.dominance_0)
bio_cost_4        = simulator_cost_4.run(t)
bio_cost_4_homo_r = bio_cost_4[:, 0]
bio_cost_4_hetero = bio_cost_4[:, 1]
bio_cost_4_homo_s = bio_cost_4[:, 2]

cost_ss_plot = plt.figure(plot_width=plot_width,
                          plot_height=plot_height)
cost_ss_plot.title.text       = 'Growth with Different Maintenance Costs, α={}'. \
    format(np.round(param.alpha_ss, 3))
cost_ss_plot.yaxis.axis_label = 'biomass (mg)'
cost_ss_plot.xaxis.axis_label = 'time (days)'

cost_ss_plot.add_layout(fin_time_homo_r)
cost_ss_plot.add_layout(fin_mass_homo_r)
cost_ss_plot.add_layout(fin_time_homo_s)
cost_ss_plot.add_layout(fin_mass_homo_s)

cost_ss_plot.line(t, bio_cost_0_homo_s,
                  color=colors[0], line_width=line_width,
                  legend='β={}'.format(np.round(cost_0, 3)))
cost_ss_plot.triangle(t, bio_cost_0_homo_s,
                      color=colors[0], size=point_size,
                      legend='β={}'.format(np.round(cost_0, 3)))

cost_ss_plot.line(t, bio_cost_1_homo_s,
                  color=colors[2], line_width=line_width,
                  legend='β={}'.format(np.round(cost_1, 3)))

cost_ss_plot.line(t, bio_cost_2_homo_s,
                  color=colors[3], line_width=line_width,
                  line_dash='dashed',
                  legend='β={}'.format(np.round(cost_2, 3)))

cost_ss_plot.line(t, bio_cost_3_homo_s,
                  color=colors[4], line_width=line_width,
                  line_dash='dotted',
                  legend='β={}'.format(np.round(cost_3, 3)))

cost_ss_plot.line(t, bio_cost_4_homo_s,
                  color=colors[1], line_width=line_width,
                  legend='β={}'.format(np.round(cost_4, 3)))
cost_ss_plot.circle(t, bio_cost_4_homo_s,
                    color=colors[1], size=point_size,
                    legend='β={}'.format(np.round(cost_4, 3)))

cost_ss_plot.legend.location = "top_left"

cost_ss_plot.title.text_font_size = title_font_size
cost_ss_plot.legend.label_text_font_size = legend_font_size
cost_ss_plot.yaxis.axis_line_width = axis_line_width
cost_ss_plot.xaxis.axis_line_width = axis_line_width
cost_ss_plot.yaxis.axis_label_text_font_size = axis_font_size
cost_ss_plot.xaxis.axis_label_text_font_size = axis_font_size
cost_ss_plot.yaxis.major_label_text_font_size = axis_tick_font_size
cost_ss_plot.xaxis.major_label_text_font_size = axis_tick_font_size
cost_ss_plot.ygrid.grid_line_width = grid_line_width
cost_ss_plot.xgrid.grid_line_width = grid_line_width

cost_rr_plot = plt.figure(plot_width=plot_width,
                          plot_height=plot_height)
cost_rr_plot.title.text       = 'Growth with Different Maintenance Costs, α={}'. \
    format(np.round(param.alpha_rr, 3))
cost_rr_plot.yaxis.axis_label = 'biomass (mg)'
cost_rr_plot.xaxis.axis_label = 'time (days)'

cost_rr_plot.add_layout(fin_time_homo_r)
cost_rr_plot.add_layout(fin_mass_homo_r)
cost_rr_plot.add_layout(fin_time_homo_s)
cost_rr_plot.add_layout(fin_mass_homo_s)

cost_rr_plot.line(t, bio_cost_0_homo_r,
                  color=colors[0], line_width=line_width,
                  legend='β={}'.format(np.round(cost_0, 3)))
cost_rr_plot.triangle(t, bio_cost_0_homo_r,
                      color=colors[0], size=point_size,
                      legend='β={}'.format(np.round(cost_0, 3)))

cost_rr_plot.line(t, bio_cost_1_homo_r,
                  color=colors[2], line_width=line_width,
                  legend='β={}'.format(np.round(cost_1, 3)))

cost_rr_plot.line(t, bio_cost_2_homo_r,
                  color=colors[3], line_width=line_width,
                  line_dash='dashed',
                  legend='β={}'.format(np.round(cost_2, 3)))

cost_rr_plot.line(t, bio_cost_3_homo_r,
                  color=colors[4], line_width=line_width,
                  line_dash='dotted',
                  legend='β={}'.format(np.round(cost_3, 3)))

cost_rr_plot.line(t, bio_cost_4_homo_r,
                  color=colors[1], line_width=line_width,
                  legend='β={}'.format(np.round(cost_4, 3)))
cost_rr_plot.circle(t, bio_cost_4_homo_r,
                    color=colors[1], size=point_size,
                    legend='β={}'.format(np.round(cost_4, 3)))

cost_rr_plot.legend.location = "top_left"

cost_rr_plot.title.text_font_size = title_font_size
cost_rr_plot.legend.label_text_font_size = legend_font_size
cost_rr_plot.yaxis.axis_line_width = axis_line_width
cost_rr_plot.xaxis.axis_line_width = axis_line_width
cost_rr_plot.yaxis.axis_label_text_font_size = axis_font_size
cost_rr_plot.xaxis.axis_label_text_font_size = axis_font_size
cost_rr_plot.yaxis.major_label_text_font_size = axis_tick_font_size
cost_rr_plot.xaxis.major_label_text_font_size = axis_tick_font_size
cost_rr_plot.ygrid.grid_line_width = grid_line_width
cost_rr_plot.xgrid.grid_line_width = grid_line_width

layout = lay.column(dom_plot,
                    grow_ss_plot, grow_rr_plot,
                    cost_ss_plot, cost_rr_plot)
plt.show(layout)
