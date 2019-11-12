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
trials    = 100

age_max        = 12
num_steps_mate = 8

num_eggs   = 10
num_larvae = 1000
num_adults = 500
save_fig   = True

field_grid = 50


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

    def collect(self) -> tuple:
        """
        Collect the number of egg_masses

        Returns:
            number of egg_masses
        """

        females = self.simulation.agents.agents(keyword.female)

        mated = []
        for female in females:
            if female.mate is not None:
                mated.append(female)

        return len(females), len(mated)

    def run(self, times: list) -> tuple:
        """
        Run the simulation for each time

        Args:
            times: the times for the simulation

        Returns:
            num egg_mass, densities
        """

        females, mated = self.collect()

        data_females = [females]
        data_mated   = [mated]
        data_prop    = [mated/females]
        for time in times[1:]:
            print('        {} Running step: {}'.
                  format(datetime.datetime.now(), time))
            self.simulation.step()
            females, mated = self.collect()

            data_females.append(females)
            data_mated.  append(mated)
            data_prop.   append(mated/females)

        return data_females, data_mated, data_prop


t            = list(range(num_steps_mate))
initial_pops = ((0,          0,          0),
                (0,          0,          0),
                (0,          0,          0),
                (num_adults, num_adults, num_adults),
                (0,          0,          0))

print('{} Running Mating simulations'.
      format(datetime.datetime.now()))
female_data = []
mate_data   = []
prop_data   = []
for num in range(trials):
    print('    {} Running Trial: {}'.format(datetime.datetime.now(), num))
    simulator = Simulator(initial_pops, 1)
    f_data, m_data, p_data = simulator.run(t)

    female_data.append(f_data)
    mate_data.  append(m_data)
    prop_data.  append(p_data)

prop_mean = np.mean(prop_data, axis=0)

prop_plot = plt.figure(plot_width=plot_width,
                       plot_height=plot_height)
prop_plot.title.text = 'Proportion of Mated Females, Number of Trials: {}'. \
    format(trials)
prop_plot.xaxis.axis_label = 'time (days'
prop_plot.yaxis.axis_label = 'mated proportion'

prop_plot.line(t, prop_mean,
               color=colors[0], line_width=line_width)

prop_plot.title.text_font_size = title_font_size
prop_plot.yaxis.axis_line_width = axis_line_width
prop_plot.xaxis.axis_line_width = axis_line_width
prop_plot.yaxis.axis_label_text_font_size = axis_font_size
prop_plot.xaxis.axis_label_text_font_size = axis_font_size
prop_plot.yaxis.major_label_text_font_size = axis_tick_font_size
prop_plot.xaxis.major_label_text_font_size = axis_tick_font_size
prop_plot.ygrid.grid_line_width = grid_line_width
prop_plot.xgrid.grid_line_width = grid_line_width

plt.show(prop_plot)
