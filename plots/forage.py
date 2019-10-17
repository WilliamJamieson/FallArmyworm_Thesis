import datetime
import dataclasses       as dclass
import numpy             as np

import bokeh.plotting as plt
import bokeh.models   as mdl
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


# Plotting parameters
dominance  = 0
k_lower    = 2
k_upper    = 6
num_k      = 9

num_steps  = 30
num_eggs   = 10
num_larvae = 1000
save_fig   = True


plot_width  = 800
plot_height = 500

colors    = palettes.Category10[9]
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

    interval = np.linspace(-2, 2, 1000)

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
                                     keyword.consume]}, 24),
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
                    forage.starvation(1,
                                      param.theta_scarce,
                                      param.sig_scarce),
                    forage.egg(param.egg_factor),
                    forage.larva(param.larva_factor),
                    forage.fight(param.fight_slope),
                    forage.radius(param.cannibalism_radius),
                    forage.encounter(param.cannibalism_encounter),
                    forage.loss(param.loss_slope,
                                param.mid,
                                param.egg_factor,
                                param.larva_factor)]
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



k_values = np.linspace(k_lower, k_upper, num_k)
mass_0, output_data = Kokko.run(k_values)

fight_plot = plt.figure(plot_width=plot_width,
                        plot_height=plot_height)
fight_plot.title.text = 'Fight Plots'
fight_plot.xaxis.axis_label = 'm_0 - m_1'
fight_plot.yaxis.axis_label = 'probability m_0 wins'

for index, k_slope in enumerate(k_values):
    fight_data = output_data[k_slope]

    fight_plot.line(mass_0, fight_data,
                    color=colors[index],
                    legend='k = {}'.format(k_slope))

fight_plot.legend.location = 'top_left'

plt.show(fight_plot)



# t            = list(range(num_steps))
# initial_pops = ((num_eggs,   num_eggs,   num_eggs),
#                 (num_larvae, num_larvae, num_larvae),
#                 (0,          0,          0),
#                 (0,          0,          0),
#                 (0,          0,          0))
# print('{} Running Cannibalism Bt simulations'.
#       format(datetime.datetime.now()))
# simulator_bt = Simulator(initial_pops, 1)
# simulator_bt.run(t)
# dataframes_bt = simulator_bt.simulation.agents.dataframes()
# egg_bt   = dataframes_bt['(0, 0)_egg']
# larva_bt = dataframes_bt['(0, 0)_larva']
# print('{} Running Cannibalism Not Bt simulations'.
#       format(datetime.datetime.now()))
# simulator_not_bt = Simulator(initial_pops, 0)
# simulator_not_bt.run(t)
# dataframes_not_bt = simulator_not_bt.simulation.agents.dataframes()
# egg_not_bt   = dataframes_not_bt['(0, 0)_egg']
# larva_not_bt = dataframes_not_bt['(0, 0)_larva']
#
# # Plots
# # Not Bt
# plt.figure()
# egg_not_bt['genotype_resistant'].   plot(color='b', label='Egg Resistant')
# egg_not_bt['genotype_heterozygous'].plot(color='r', label='Egg Heterozygous')
# egg_not_bt['genotype_susceptible']. plot(color='k', label='Egg Susceptible')
#
# larva_not_bt['genotype_resistant'].   plot(color='b', linestyle='--',
#                                            label='Larva Resistant')
# larva_not_bt['genotype_heterozygous'].plot(color='r', linestyle='--',
#                                            label='Larva Heterozygous')
# larva_not_bt['genotype_susceptible']. plot(color='k', linestyle='--',
#                                            label='Larva Susceptible')
# #       Add plot labels
# plt.legend()
# plt.xlabel('time (days)')
# plt.ylabel('population')
# plt.title('Cannibalism on Non-Bt plant')
# #       Show/save plot
# if save_fig:
#     plt.savefig('Cannibalism_not_bt.png')
# plt.show()
# # Not Bt
# plt.figure()
# egg_bt['genotype_resistant'].   plot(color='b', label='Egg Resistant')
# egg_bt['genotype_heterozygous'].plot(color='r', label='Egg Heterozygous')
# egg_bt['genotype_susceptible']. plot(color='k', label='Egg Susceptible')
#
# larva_bt['genotype_resistant'].   plot(color='b', linestyle='--',
#                                        label='Larva Resistant')
# larva_bt['genotype_heterozygous'].plot(color='r', linestyle='--',
#                                        label='Larva Heterozygous')
# larva_bt['genotype_susceptible']. plot(color='k', linestyle='--',
#                                        label='Larva Susceptible')
# #       Add plot labels
# plt.legend()
# plt.xlabel('time (days)')
# plt.ylabel('population')
# plt.title('Cannibalism on Bt plant')
# #       Show/save plot
# if save_fig:
#     plt.savefig('Cannibalism_bt.png')
# plt.show()
