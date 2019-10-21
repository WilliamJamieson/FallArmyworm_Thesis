import datetime
import dataclasses  as dclass
import numpy        as np

import bokeh.plotting as plt
import bokeh.models   as mdl
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
trials     = 1000

k_lower    = 0.5
k_upper    = 4
num_k      = 8

num_steps  = 4
num_eggs   = 10
num_larvae = 10
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

    grid        = [(keyword.hexagon, 1, 1, True),
                   graph.graph(10)]
    attrs       = {1: tracking.genotype_attrs}
    data        = (np.inf,)
    steps       = [({keyword.larva: [keyword.move,
                                     keyword.consume]}, param.forage_steps),
                   ({keyword.larva: [keyword.grow,
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
                    move.larva(param.larva_scale,
                               param.larva_shape),
                    forage.starvation(param.forage_steps,
                                      param.theta_adlibitum,
                                      param.sig_scarce),
                    forage.egg(param.egg_factor),
                    forage.larva(param.larva_factor),
                    forage.fight(param.fight_slope),
                    forage.radius(param.cannibalism_radius),
                    # forage.loss(param.loss_slope,
                    #             param.mid,
                    #             param.egg_factor,
                    #             param.larva_factor)
                    ]
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
        Get the final population of larvae

        Args:
            data_key: the genotype table key

        Returns:
            the number of larvae at the end
        """

        dataframes = self.simulation.agents.dataframes()

        timestep = self.simulation.timestep
        pupa     = dataframes['(0, 0)_larva']
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
        rate = 1 - prop

        return - np.log(prop) / start_pop, prop, rate

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
        rate   = []
        for rho in rhos:
            rho_cannib, rho_prop, rho_rate = cls.run(rho, times, data_key, nums)

            cannib.append(rho_cannib)
            prop.  append(rho_prop)
            rate.  append(rho_rate)

        return cannib, prop, rate


raffa_point_high = 38.6/100
raffa_point_low  = 17.7/100

raffa_point_high_sur = 1 - raffa_point_high
raffa_point_low_sur  = 1 - raffa_point_low

raffa_span_high = mdl.Span(location=raffa_point_high,
                           dimension='width',
                           line_color=colors[2],
                           line_width=line_width,
                           line_dash='dotted')
raffa_span_low = mdl.Span(location=raffa_point_low,
                          dimension='width',
                          line_color=colors[2],
                          line_width=line_width,
                          line_dash='dotted')


t          = list(range(num_steps))
# encounters = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
# encounters = np.logspace(0, 5, 30)
encounters = np.geomspace(0.1, 1, 10)
print('{} Running Cannibalism simulations for RR'.
      format(datetime.datetime.now()))
initial_pops = ((0,          0, 0),
                (num_larvae, 0, 0),
                (0,          0, 0),
                (0,          0, 0),
                (0,          0, 0))
cannib_rr, prop_rr, rate_rr = Simulator.rho(encounters,
                                            t, 'genotype_resistant',
                                            initial_pops)
print('{} Running Cannibalism simulations for SS'.
      format(datetime.datetime.now()))
initial_pops = ((0, 0, 0),
                (0, 0, num_larvae),
                (0, 0, 0),
                (0, 0, 0),
                (0, 0, 0))
cannib_ss, prop_ss, rate_ss = Simulator.rho(encounters,
                                            t, 'genotype_susceptible',
                                            initial_pops)

cannib_log = plt.figure(plot_width=plot_width,
                        plot_height=plot_height,
                        x_axis_type='log')
cannib_log.title.text = 'Cannibalism Constant, ' \
                        'Number of Trials: {}'.format(trials)
cannib_log.xaxis.axis_label = 'encounter constant'
cannib_log.yaxis.axis_label = 'cannibalism constant'

cannib_log.triangle(encounters, cannib_rr,
                    color=colors[0], size=point_size,
                    legend='Resistant')
cannib_log.circle(encounters, cannib_ss,
                  color=colors[1], size=point_size,
                  legend='Susceptible')
cannib_log.line(encounters, cannib_rr,
                color=colors[0], line_width=line_width,
                legend='Resistant')
cannib_log.line(encounters, cannib_ss,
                color=colors[1], line_width=line_width,
                legend='Susceptible')

cannib_log.title.text_font_size = title_font_size
cannib_log.legend.label_text_font_size = legend_font_size
cannib_log.yaxis.axis_line_width = axis_line_width
cannib_log.xaxis.axis_line_width = axis_line_width
cannib_log.yaxis.axis_label_text_font_size = axis_font_size
cannib_log.xaxis.axis_label_text_font_size = axis_font_size
cannib_log.yaxis.major_label_text_font_size = axis_tick_font_size
cannib_log.xaxis.major_label_text_font_size = axis_tick_font_size
cannib_log.ygrid.grid_line_width = grid_line_width
cannib_log.xgrid.grid_line_width = grid_line_width

cannib_plot = plt.figure(plot_width=plot_width,
                         plot_height=plot_height)
cannib_plot.title.text = 'Cannibalism Constant, Number of Trials: {}'. \
    format(trials)
cannib_plot.xaxis.axis_label = 'encounter constant'
cannib_plot.yaxis.axis_label = 'cannibalism constant'

cannib_plot.triangle(encounters, cannib_rr,
                     color=colors[0], size=point_size,
                     legend='Resistant')
cannib_plot.circle(encounters, cannib_ss,
                   color=colors[1], size=point_size,
                   legend='Susceptible')
cannib_plot.line(encounters, cannib_rr,
                 color=colors[0], line_width=line_width,
                 legend='Resistant')
cannib_plot.line(encounters, cannib_ss,
                 color=colors[1], line_width=line_width,
                 legend='Susceptible')

cannib_plot.title.text_font_size = title_font_size
cannib_plot.legend.label_text_font_size = legend_font_size
cannib_plot.yaxis.axis_line_width = axis_line_width
cannib_plot.xaxis.axis_line_width = axis_line_width
cannib_plot.yaxis.axis_label_text_font_size = axis_font_size
cannib_plot.xaxis.axis_label_text_font_size = axis_font_size
cannib_plot.yaxis.major_label_text_font_size = axis_tick_font_size
cannib_plot.xaxis.major_label_text_font_size = axis_tick_font_size
cannib_plot.ygrid.grid_line_width = grid_line_width
cannib_plot.xgrid.grid_line_width = grid_line_width

prop_log = plt.figure(plot_width=plot_width,
                      plot_height=plot_height,
                      x_axis_type='log')
prop_log.title.text = 'Survival Proportion, ' \
                      'Number of Trials: {}'.format(trials)
prop_log.xaxis.axis_label = 'encounter constant'
prop_log.yaxis.axis_label = 'survival proportion'

prop_log.triangle(encounters, prop_rr,
                  color=colors[0], size=point_size,
                  legend='Resistant')
prop_log.circle(encounters, prop_ss,
                color=colors[1], size=point_size,
                legend='Susceptible')
prop_log.line(encounters, prop_rr,
              color=colors[0], line_width=line_width,
              legend='Resistant')
prop_log.line(encounters, prop_ss,
              color=colors[1], line_width=line_width,
              legend='Susceptible')

prop_log.title.text_font_size = title_font_size
prop_log.legend.label_text_font_size = legend_font_size
prop_log.yaxis.axis_line_width = axis_line_width
prop_log.xaxis.axis_line_width = axis_line_width
prop_log.yaxis.axis_label_text_font_size = axis_font_size
prop_log.xaxis.axis_label_text_font_size = axis_font_size
prop_log.yaxis.major_label_text_font_size = axis_tick_font_size
prop_log.xaxis.major_label_text_font_size = axis_tick_font_size
prop_log.ygrid.grid_line_width = grid_line_width
prop_log.xgrid.grid_line_width = grid_line_width

prop_plot = plt.figure(plot_width=plot_width,
                       plot_height=plot_height)
prop_plot.title.text = 'Survival Proportion, Number of Trials: {}'. \
    format(trials)
prop_plot.xaxis.axis_label = 'encounter constant'
prop_plot.yaxis.axis_label = 'survival proportion'

prop_plot.triangle(encounters, prop_rr,
                   color=colors[0], size=point_size,
                   legend='Resistant')
prop_plot.circle(encounters, prop_ss,
                 color=colors[1], size=point_size,
                 legend='Susceptible')
prop_plot.line(encounters, prop_rr,
               color=colors[0], line_width=line_width,
               legend='Resistant')
prop_plot.line(encounters, prop_ss,
               color=colors[1], line_width=line_width,
               legend='Susceptible')

prop_plot.title.text_font_size = title_font_size
prop_plot.legend.label_text_font_size = legend_font_size
prop_plot.yaxis.axis_line_width = axis_line_width
prop_plot.xaxis.axis_line_width = axis_line_width
prop_plot.yaxis.axis_label_text_font_size = axis_font_size
prop_plot.xaxis.axis_label_text_font_size = axis_font_size
prop_plot.yaxis.major_label_text_font_size = axis_tick_font_size
prop_plot.xaxis.major_label_text_font_size = axis_tick_font_size
prop_plot.ygrid.grid_line_width = grid_line_width
prop_plot.xgrid.grid_line_width = grid_line_width

rate_log = plt.figure(plot_width=plot_width,
                      plot_height=plot_height,
                      x_axis_type='log')
rate_log.title.text = 'Cannibalism Proportion, ' \
                      'Number of Trials: {}'.format(trials)
rate_log.xaxis.axis_label = 'encounter constant'
rate_log.yaxis.axis_label = 'cannibalism proportion'

rate_log.add_layout(raffa_span_high)
rate_log.add_layout(raffa_span_low)

rate_log.triangle(encounters, rate_rr,
                  color=colors[0], size=point_size,
                  legend='Resistant')
rate_log.circle(encounters, rate_ss,
                color=colors[1], size=point_size,
                legend='Susceptible')
rate_log.line(encounters, rate_rr,
              color=colors[0], line_width=line_width,
              legend='Resistant')
rate_log.line(encounters, rate_ss,
              color=colors[1], line_width=line_width,
              legend='Susceptible')

rate_log.title.text_font_size = title_font_size
rate_log.legend.label_text_font_size = legend_font_size
rate_log.yaxis.axis_line_width = axis_line_width
rate_log.xaxis.axis_line_width = axis_line_width
rate_log.yaxis.axis_label_text_font_size = axis_font_size
rate_log.xaxis.axis_label_text_font_size = axis_font_size
rate_log.yaxis.major_label_text_font_size = axis_tick_font_size
rate_log.xaxis.major_label_text_font_size = axis_tick_font_size
rate_log.ygrid.grid_line_width = grid_line_width
rate_log.xgrid.grid_line_width = grid_line_width

rate_plot = plt.figure(plot_width=plot_width,
                       plot_height=plot_height)
rate_plot.title.text = 'Cannibalism Proportion, Number of Trials: {}'. \
    format(trials)
rate_plot.xaxis.axis_label = 'encounter constant'
rate_plot.yaxis.axis_label = 'cannibalism proportion'

rate_plot.add_layout(raffa_span_high)
rate_plot.add_layout(raffa_span_low)

rate_plot.triangle(encounters, rate_rr,
                   color=colors[0], size=point_size,
                   legend='Resistant')
rate_plot.circle(encounters, rate_ss,
                 color=colors[1], size=point_size,
                 legend='Susceptible')
rate_plot.line(encounters, rate_rr,
               color=colors[0], line_width=line_width,
               legend='Resistant')
rate_plot.line(encounters, rate_ss,
               color=colors[1], line_width=line_width,
               legend='Susceptible')

rate_plot.title.text_font_size = title_font_size
rate_plot.legend.label_text_font_size = legend_font_size
rate_plot.yaxis.axis_line_width = axis_line_width
rate_plot.xaxis.axis_line_width = axis_line_width
rate_plot.yaxis.axis_label_text_font_size = axis_font_size
rate_plot.xaxis.axis_label_text_font_size = axis_font_size
rate_plot.yaxis.major_label_text_font_size = axis_tick_font_size
rate_plot.xaxis.major_label_text_font_size = axis_tick_font_size
rate_plot.ygrid.grid_line_width = grid_line_width
rate_plot.xgrid.grid_line_width = grid_line_width

layout = lay.column(cannib_plot, cannib_log,
                    prop_plot, prop_log,
                    rate_plot, rate_log)
plt.show(layout)
