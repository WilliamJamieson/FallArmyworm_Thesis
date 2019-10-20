import datetime
import dataclasses  as dclass
import numpy        as np

import joblib as para

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
import models.movement     as move
import models.reproduction as repro

import source.hint    as hint
import source.keyword as keyword

import source.simulation.simulation as main_simulation


num_cpu = 8

line_width       = 2
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
trials     = 20

k_lower    = 0.5
k_upper    = 4
num_k      = 8

num_steps  = 40
num_eggs   = 10
num_larvae = 1000
save_fig   = True


plot_width  = 800
plot_height = 500

colors    = palettes.Colorblind[8]
save_file = 'forage_plots.html'

plt.output_file(save_file)


@dclass.dataclass
class Kokko(object):
    """
    Class to create a plot of the fight model

    Variables:
        interval: interval for diff
        k:        list of slope values
        fight:    dict of corresponding fight models
    """

    interval = np.linspace(-15, 15, 1000)

    k: np.array
    fight: dict = dclass.field(default=dict)

    def __post_init__(self):
        """Generate the fight"""

        self.fight = {k: forage.fight(k)
                        for k in self.k}

    def simulate(self, k: float) -> np.array:
        """
        Simulate the fight model for slope k

        Args:
            k: the slope

        Returns:
            the output of fight model
        """

        values = []
        fight  = self.fight[k]
        for m_0 in self.interval:
            values.append(fight.prob(m_0, 0))

        return np.array(values)

    def get_values(self) -> dict:
        """
        Get all the values for different k

        Returns:
            dict of outputs
        """

        return {k: self.simulate(k) for k in self.k}

    @classmethod
    def run(cls, k: np.array) -> tuple:
        """
        Run the Kokko Simulation
        Args:
            k: list of values for k

        Returns:
            interval, outputs
        """

        sim = cls(k)

        return sim.interval, sim.get_values()


@dclass.dataclass
class Simulator(object):
    """
    Class to setup and run a simulation of only biomass growth:

    Variables:
        nums:   initial population numbers
        forage: the plant forage model
    """

    grid        = [(keyword.hexagon, 1, 1, True),
                   graph.graph(25)]
    attrs       = {1: tracking.genotype_attrs}
    data        = (np.inf,)
    steps       = [({keyword.larva: [keyword.move,
                                     keyword.consume]}, param.forage_steps),
                   ({keyword.larva: [keyword.grow,
                                     keyword.develop,
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
                    repro.init_sex(param.female_prob),
                    move.larva(param.larva_scale,
                               param.larva_shape),
                    forage.starvation(param.forage_steps,
                                      param.theta_adlibitum,
                                      param.sig_scarce),
                    forage.egg(param.egg_factor),
                    forage.larva(param.larva_factor),
                    forage.fight(param.fight_slope),
                    forage.radius(param.cannibalism_radius),
                    # forage.encounter(param.cannibalism_encounter),
                    forage.loss(param.loss_slope,
                                param.mid,
                                param.egg_factor,
                                param.larva_factor),
                    dev.larva_dev(param.mu_larva_dev_ss,
                                  param.mu_larva_dev_rr,
                                  param.sig_larva_dev_ss,
                                  param.sig_larva_dev_rr,
                                  dominance)]
    input_variables = param.repro_values

    nums:       hint.init_pops
    bt_prop:    float
    encounter:  float
    simulation: hint.simulation = None

    def __post_init__(self):

        input_models = self.input_models.copy()
        input_models.append(forage.encounter(self.encounter))

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

    def run_sim(self, times: list) -> None:
        """
        Run the simulation for each time

        Args:
            times: the times for the simulation

        Returns:
            biomass data
        """

        for _ in times[1:]:
            self.simulation.step()

    def get_start_data(self, data_key: str) -> int:
        """
        Get the start population of larvae

        Args:
            data_key: the genotype table key

        Returns:
            the number of larvae at start
        """

        dataframes = self.simulation.agents.dataframes()

        larva  = dataframes['(0, 0)_larva']
        column = larva[data_key]

        return int(column[0])

    def get_final_data(self, data_key:  str) -> int:
        """
        Get the final population of pupae

        Args:
            data_key: the genotype table key

        Returns:
            the number of pupae at the end
        """

        dataframes = self.simulation.agents.dataframes()

        timestep = self.simulation.timestep
        pupa     = dataframes['(0, 0)_pupa']
        column   = pupa[data_key]
        value    = column[timestep]

        return int(value)

    @classmethod
    def run(cls, rho:        float,
                 times:      list,
                 data_key:   str,
                 nums:       hint.init_pops) -> tuple:
        """
        Run a bunch of trials
        Args:
            rho:        encounter constant
            times:      time interval
            data_key:   column key
            nums:       init_population

        Returns:
            value of cannibalism rate constant
        """

        # print('    {} Starting run for rho: {}'.
        #       format(datetime.datetime.now(), rho))
        #
        # def trial_run(trial_num: int) -> tuple:
        #     """
        #     Function to parallelize
        #
        #     Args:
        #         trial_num: number of the trial
        #
        #     Returns:
        #         start_pop, end_pop
        #     """
        #
        #     print('        {} running trial: {}'.
        #           format(datetime.datetime.now(), trial_num))
        #     sim = cls(nums, 1, rho)
        #     sim.run_sim(times)
        #
        #     return sim.get_start_data(data_key), sim.get_final_data(data_key)
        #
        # sim_data = para.Parallel(n_jobs=num_cpu)(
        #     para.delayed(trial_run)(trial_num) for trial_num in range(trials)
        # )
        #
        # start_data = []
        # end_data   = []
        # for data_point in sim_data:
        #     start_data.append(data_point[0])
        #     end_data.  append(data_point[1])

        print('    {} Starting run for rho: {}'.
              format(datetime.datetime.now(), rho))
        start_data = []
        end_data   = []
        for trial_num in range(trials):
            print('        {} running trial: {}'.
                  format(datetime.datetime.now(), trial_num))
            sim = cls(nums, 1, rho)
            sim.run_sim(times)
            start_data.append(sim.get_start_data(data_key))
            end_data.  append(sim.get_final_data(data_key))

        start_pop = np.mean(start_data)
        end_pop   = np.mean(end_data)

        prop = end_pop/start_pop

        return - np.log(prop) / start_pop, prop

    @classmethod
    def rho(cls, rhos:     np.array,
                 times:    list,
                 data_key: str,
                 nums:     hint.init_pops) -> tuple:
        """
        Run trials for each rho value

        Args:
            rhos:     list of encounter constants
            times:    time interval
            data_key: data key
            nums:     init population

        Returns:
            list of corresponding values for cannibalism
        """

        cannib = []
        prop   = []
        for rho in rhos:
            rho_cannib, rho_prop = cls.run(rho, times, data_key, nums)

            cannib.append(rho_cannib)
            prop.  append(rho_prop)

        return cannib, prop


# k_values = np.linspace(k_lower, k_upper, num_k)
k_values = np.array([0.25, 0.3, 0.4, 0.5, 0.75, 1, 2, 4])
mass_0, output_data = Kokko.run(k_values)

fight_plot = plt.figure(plot_width=plot_width,
                        plot_height=plot_height)
fight_plot.title.text = 'Fight Plots'
fight_plot.xaxis.axis_label = 'm_0 - m_1 (mg)'
fight_plot.yaxis.axis_label = 'probability  m_0  wins'

for index, k_slope in enumerate(k_values):
    fight_data = output_data[k_slope]

    fight_plot.line(mass_0, fight_data,
                    color=colors[index], line_width=line_width,
                    legend='k = {}'.format(k_slope))

fight_plot.legend.location = 'top_left'

fight_plot.title.text_font_size = title_font_size
fight_plot.legend.label_text_font_size = legend_font_size
fight_plot.yaxis.axis_line_width = axis_line_width
fight_plot.xaxis.axis_line_width = axis_line_width
fight_plot.yaxis.axis_label_text_font_size = axis_font_size
fight_plot.xaxis.axis_label_text_font_size = axis_font_size
fight_plot.yaxis.major_label_text_font_size = axis_tick_font_size
fight_plot.xaxis.major_label_text_font_size = axis_tick_font_size
fight_plot.ygrid.grid_line_width = grid_line_width
fight_plot.xgrid.grid_line_width = grid_line_width

plt.show(fight_plot)


# t            = list(range(num_steps))
# # encounters = [0.01, 0.02, 0.04, 0.06, 0.08, 0.1, 0.2, 0.4, 0.6, 0.8, 1, 2, 3]
# encounters = np.logspace(0, 3, 20)
# print('{} Running Cannibalism simulations for RR'.
#       format(datetime.datetime.now()))
# initial_pops = ((0,          0, 0),
#                 (num_larvae, 0, 0),
#                 (0,          0, 0),
#                 (0,          0, 0),
#                 (0,          0, 0))
# cannib_rr, prop_rr = Simulator.rho(encounters,
#                                    t, 'genotype_resistant',
#                                    initial_pops)
# print('{} Running Cannibalism simulations for SS'.
#       format(datetime.datetime.now()))
# initial_pops = ((0, 0, 0),
#                 (0, 0, num_larvae),
#                 (0, 0, 0),
#                 (0, 0, 0),
#                 (0, 0, 0))
# cannib_ss, prop_ss = Simulator.rho(encounters,
#                                    t, 'genotype_susceptible',
#                                    initial_pops)
#
# cannib_log = plt.figure(plot_width=plot_width,
#                         plot_height=plot_height,
#                         x_axis_type='log')
# cannib_log.title.text = 'Cannibalism Encounter Constant vs. ' \
#                         'Cannibalism Constant, ' \
#                         'Number of Trials: {}'.format(trials)
# cannib_log.xaxis.axis_label = 'encounter constant'
# cannib_log.yaxis.axis_label = 'cannibalism constant'
#
# cannib_log.circle(encounters, cannib_rr,
#                   color=colors[0], size=10,
#                   legend='Resistant')
# cannib_log.circle(encounters, cannib_ss,
#                   color=colors[2], size=10,
#                   legend='Susceptible')
# cannib_log.line(encounters, cannib_rr,
#                 color=colors[0])
# cannib_log.line(encounters, cannib_ss,
#                 color=colors[2])
#
# cannib_plot = plt.figure(plot_width=plot_width,
#                          plot_height=plot_height)
# cannib_plot.title.text = 'Cannibalism Encounter Constant vs. ' \
#                          'Cannibalism Constant, Number of Trials: {}'. \
#     format(trials)
# cannib_plot.xaxis.axis_label = 'encounter constant'
# cannib_plot.yaxis.axis_label = 'cannibalism constant'
#
# cannib_plot.circle(encounters, cannib_rr,
#                    color=colors[0], size=10,
#                    legend='Resistant')
# cannib_plot.circle(encounters, cannib_ss,
#                    color=colors[2], size=10,
#                    legend='Susceptible')
# cannib_plot.line(encounters, cannib_rr,
#                  color=colors[0])
# cannib_plot.line(encounters, cannib_ss,
#                  color=colors[2])
#
# prop_log = plt.figure(plot_width=plot_width,
#                       plot_height=plot_height,
#                       x_axis_type='log')
# prop_log.title.text = 'Cannibalism Encounter Constant vs. ' \
#                       'Survival Proportion, ' \
#                       'Number of Trials: {}'.format(trials)
# prop_log.xaxis.axis_label = 'encounter constant'
# prop_log.yaxis.axis_label = 'survival proportion'
#
# prop_log.circle(encounters, prop_rr,
#                 color=colors[0], size=10,
#                 legend='Resistant')
# prop_log.circle(encounters, prop_ss,
#                 color=colors[2], size=10,
#                 legend='Susceptible')
# prop_log.line(encounters, prop_rr,
#               color=colors[0])
# prop_log.line(encounters, prop_ss,
#               color=colors[2])
#
# prop_plot = plt.figure(plot_width=plot_width,
#                        plot_height=plot_height)
# prop_plot.title.text = 'Cannibalism Encounter Constant vs. ' \
#                        'Survival Proportion, Number of Trials: {}'. \
#     format(trials)
# prop_plot.xaxis.axis_label = 'encounter constant'
# prop_plot.yaxis.axis_label = 'survival proportion'
#
# prop_plot.circle(encounters, prop_rr,
#                  color=colors[0], size=10,
#                  legend='Resistant')
# prop_plot.circle(encounters, prop_ss,
#                  color=colors[2], size=10,
#                  legend='Susceptible')
# prop_plot.line(encounters, prop_rr,
#                color=colors[0])
# prop_plot.line(encounters, prop_ss,
#                color=colors[2])
#
# layout = lay.column(fight_plot, cannib_plot, cannib_log, prop_plot, prop_log)
# plt.show(layout)
