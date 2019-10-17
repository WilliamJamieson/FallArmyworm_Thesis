import datetime
import dataclasses       as dclass
# import matplotlib.pyplot as plt
import numpy             as np
import scipy.stats       as stats

import bokeh.plotting     as plt
import bokeh.layouts      as lay
import bokeh.models       as mdl
import bokeh.palettes     as palettes
import bokeh.models.tools as tools

import data.biomass       as input_biomass
import data.data_tracking as input_tracking
import data.forage        as input_forage
import data.reproduction  as input_repro

import source.hint    as hint
import source.keyword as keyword

import source.simulation.simulation as main_simulation


# Plotting parameters
trials    = 1000
num_steps = 40
save_fig  = True

plot_width  = 800
plot_height = 500

colors    = palettes.Set1[3]
save_file = 'biomass_plots.html'

plt.output_file(save_file)


@dclass.dataclass
class West(object):
    """
    Class to handle plotting exact solutions West et.al. mass model:
        m^0.25/M = 1 - [1 - m_0^0.25/M]exp(-at/4M)

        where:
            M   = mass_const
            a   = alpha
            m_0 = init_mass

    Variables:
        alpha:      alpha constant
        mass_const: mass constant
        init_mass:  initial mass
    """

    alpha:      float
    mass_const: float
    init_mass:  float

    def west(self, time: float) -> float:
        """
        Compute the West et.al. model at time (see above) for m
            where t=time

        Args:
            time: time

        Returns:
            evaluation of model at time for m
        """

        coeff = 1 - (self.init_mass**0.25)/self.mass_const
        power = (-self.alpha*time)/(4*self.mass_const)

        lhs = 1 - coeff*np.exp(power)

        return (self.mass_const*lhs)**4

    def run(self, times: list) -> list:
        """
        Compute the West et.al. model at each of the given times for m

        Args:
            times: list of times

        Returns:
            list of values for m from model
        """

        values = []
        for time in times:
            values.append(self.west(time))

        return values


def exact(genotype: str,
          times:   list) -> np.array:
    """
    Run an exact West et.al. model for the phenotype and times given:

    Args:
        genotype: genotype to use
        times:    times to run model at

    Returns:
        list of values for model at times
    """

    alpha      = input_biomass.growth_alpha[ genotype]
    mass_const = input_biomass.mass_constant[genotype]
    mass_0     = input_biomass.mass_0[       genotype]

    west = West(alpha, mass_const, mass_0)

    return np.array(west.run(times))


@dclass.dataclass
class EulerApprox(object):
    """
    Class to simulate the West model with Euler's method:
        equation simulated:
            dm/dt = alpha*m^{3/4} - beta*m

    Variables:
        alpha:     alpha constant
        beta:      beta constant
        init_mass: initial mass
    """

    alpha:     float
    beta:      float
    init_mass: float

    def rhs(self, mass: float) -> float:
        """
        Evaluates the right hand side of the equation

        Args:
            mass: the mass of the larva

        Returns:
            right hand side of the equation given the mass
        """

        rate = self.alpha*(mass**0.75)
        cost = self.beta*mass

        return rate - cost

    def step(self, mass:      float,
                   step_size: float) -> float:
        """
        Get the new mass using Euler's method to step forward by 1 step

        Args:
            mass:      the mass of the larva
            step_size: the step size in time

        Returns:
            the new mass of the larva
        """

        return mass + step_size*self.rhs(mass)

    def run(self, times: list) -> list:
        """
        Evaluate Euler's method for the list of times

        Args:
            times: a list of times

        Returns:
            masses at each time (assumes init_mass is first mass)
        """

        values = [self.init_mass]

        t_current = times[0]
        m_current = self.init_mass

        for t_new in times[1:]:
            step_size = t_new - t_current
            m_new     = self.step(m_current, step_size)

            values.append(m_new)
            t_current = t_new
            m_current = m_new

        return values


def euler(genotype: str,
          times:    list) -> np.array:
    """
    Run an Euler simulation for the West et.al. model

    Args:
        genotype: genotype to use
        times:    times to approximate at

    Returns:
        list of approximate values using Euler's method
    """

    alpha  = input_biomass.growth_alpha[genotype]
    beta   = input_biomass.growth_beta[ genotype]
    mass_0 = input_biomass.mass_0[      genotype]

    euler_method = EulerApprox(alpha, beta, mass_0)

    return np.array(euler_method.run(times))


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
    attrs       = {0: input_tracking.genotype_attrs}
    data        = (np.inf,)
    steps       = [({keyword.larva: [keyword.consume,
                                     keyword.grow,
                                     keyword.reset]},)]
    emigration  = []
    immigration = []

    input_models = [input_biomass.max_gut,
                    input_biomass.growth,
                    input_biomass.init_num,
                    input_biomass.init_mass,
                    input_biomass.init_juvenile,
                    input_biomass.init_mature,
                    input_biomass.init_plant,
                    input_repro.init_sex]
    input_variables = input_repro.values

    nums:       hint.init_pops
    bt_prop:    float
    forage:     hint.forage_plant
    simulation: hint.simulation = None

    def __post_init__(self):
        input_models = self.input_models.copy()
        input_models.append(self.forage)

        inputs = tuple(input_models)

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


fin_time_homo_r = mdl.Span(location=input_biomass.fin_point_r[0],
                           dimension='height',
                           line_color=colors[0],
                           line_dash='dotted')
fin_mass_homo_r = mdl.Span(location=input_biomass.fin_point_r[1],
                           dimension='width',
                           line_color=colors[0],
                           line_dash='dotted')

fin_time_homo_s = mdl.Span(location=input_biomass.fin_point_s[0],
                           dimension='height',
                           line_color=colors[2],
                           line_dash='dotted')
fin_mass_homo_s = mdl.Span(location=input_biomass.fin_point_s[1],
                           dimension='width',
                           line_color=colors[2],
                           line_dash='dotted')

# Generate the ad libitum plots
t            = list(range(num_steps))
print('{} Running Exact simulations'.format(datetime.datetime.now()))
exact_homo_r = exact(keyword.homo_r, t)
exact_hetero = exact(keyword.hetero, t)
exact_homo_s = exact(keyword.homo_s, t)

print('{} Running Euler simulations'.format(datetime.datetime.now()))
euler_homo_r = euler(keyword.homo_r, t)
euler_hetero = euler(keyword.hetero, t)
euler_homo_s = euler(keyword.homo_s, t)

euler_plot = plt.figure(plot_width=plot_width,
                        plot_height=plot_height)
euler_plot.title.text       = 'Simulation of Growth'
euler_plot.yaxis.axis_label = 'biomass (mg)'
euler_plot.xaxis.axis_label = 'time (days)'

euler_plot.add_layout(fin_time_homo_r)
euler_plot.add_layout(fin_mass_homo_r)
euler_plot.add_layout(fin_time_homo_s)
euler_plot.add_layout(fin_mass_homo_s)

euler_plot.line(t, exact_homo_r,
                color=colors[0],
                legend='Exact Resistant')
euler_plot.circle(t, euler_homo_r,
                  color=colors[0],
                  legend='Model Resistant')
euler_plot.line(t, exact_hetero,
                color=colors[1],
                legend='Exact Heterozygous')
euler_plot.circle(t, euler_hetero,
                  color=colors[1],
                  legend='Model Heterozygous')
euler_plot.line(t, exact_homo_s,
                color=colors[2],
                legend='Exact Susceptible')
euler_plot.circle(t, euler_homo_s,
                  color=colors[2],
                  legend='Model Susceptible')

euler_plot.x([input_biomass.fin_point_r[0]],
             [input_biomass.fin_point_r[1]],
             color=colors[0], size=20,
             legend='Resistant Pupation')
euler_plot.x([input_biomass.fin_point_s[0]],
             [input_biomass.fin_point_s[1]],
             color=colors[2], size=20,
             legend='Susceptible Pupation')

euler_plot.legend.location = "bottom_right"


initial_pops = ((0, 0, 0),
                (1, 1, 1),
                (0, 0, 0),
                (0, 0, 0),
                (0, 0, 0))
simulator_bt = Simulator(initial_pops,
                         1,
                         input_forage.ad_libitum)
biomass_bt  = simulator_bt.run(t)
biomass_bt_homo_r = biomass_bt[:, 0]
biomass_bt_hetero = biomass_bt[:, 1]
biomass_bt_homo_s = biomass_bt[:, 2]

rk4_plot = plt.figure(plot_width=plot_width,
                      plot_height=plot_height)
rk4_plot.title.text       = 'Simulation of Growth'
rk4_plot.yaxis.axis_label = 'biomass (mg)'
rk4_plot.xaxis.axis_label = 'time (days)'

rk4_plot.add_layout(fin_time_homo_r)
rk4_plot.add_layout(fin_mass_homo_r)
rk4_plot.add_layout(fin_time_homo_s)
rk4_plot.add_layout(fin_mass_homo_s)

rk4_plot.line(t, exact_homo_r,
              color=colors[0],
              legend='Exact Resistant')
rk4_plot.circle(t, biomass_bt_homo_r,
                color=colors[0],
                legend='Model Resistant')
rk4_plot.line(t, exact_hetero,
              color=colors[1],
              legend='Exact Heterozygous')
rk4_plot.circle(t, biomass_bt_hetero,
                color=colors[1],
                legend='Model Heterozygous')
rk4_plot.line(t, exact_homo_s,
              color=colors[2],
              legend='Exact Susceptible')
rk4_plot.circle(t, biomass_bt_homo_s,
                color=colors[2],
                legend='Model Susceptible')

rk4_plot.x([input_biomass.fin_point_r[0]],
           [input_biomass.fin_point_r[1]],
           color=colors[0], size=20,
           legend='Resistant Pupation')
rk4_plot.x([input_biomass.fin_point_s[0]],
           [input_biomass.fin_point_s[1]],
           color=colors[2], size=20,
           legend='Susceptible Pupation')

rk4_plot.legend.location = "bottom_right"

# Generate the stochastic plots
initial_pops = ((0,      0,      0),
                (trials, trials, trials),
                (0,      0,      0),
                (0,      0,      0),
                (0,      0,      0))
print('{} Running Stochastic ad libitum simulations'.
      format(datetime.datetime.now()))
adlibitum = Simulator(initial_pops, 1, input_forage.ad_libitum)
adlib     = adlibitum.run(t)
adlib_homo_r = adlib[:, :trials]
adlib_hetero = adlib[:, trials: 2*trials]
adlib_homo_s = adlib[:, 2*trials:]
biomass_adlib_homo_r = extract_data(adlib_homo_r)
biomass_adlib_hetero = extract_data(adlib_hetero)
biomass_adlib_homo_s = extract_data(adlib_homo_s)

adlib_plot = plt.figure(plot_width=plot_width,
                        plot_height=plot_height)
adlib_plot.title.text       = 'Simulation of Growth, Number of Trials: {}'. \
    format(trials)
adlib_plot.yaxis.axis_label = 'biomass (mg)'
adlib_plot.xaxis.axis_label = 'time (days)'

adlib_plot.line(t, biomass_adlib_homo_r[0],
                color=colors[0],
                legend='Mean Resistant')
adlib_plot.line(t, biomass_adlib_homo_r[7],
                color=colors[0], line_dash='dashed',
                legend='95% Confidence Resistant')
adlib_plot.line(t, biomass_adlib_homo_r[8],
                color=colors[0], line_dash='dashed')

adlib_plot.line(t, biomass_adlib_hetero[0],
                color=colors[1],
                legend='Mean Heterozygous')
adlib_plot.line(t, biomass_adlib_hetero[7],
                color=colors[1], line_dash='dashed',
                legend='95% Confidence Heterozygous')
adlib_plot.line(t, biomass_adlib_hetero[8],
                color=colors[1], line_dash='dashed')

adlib_plot.line(t, biomass_adlib_homo_s[0],
                color=colors[2],
                legend='Mean Susceptible')
adlib_plot.line(t, biomass_adlib_homo_s[7],
                color=colors[2], line_dash='dashed',
                legend='95% Confidence Susceptible')
adlib_plot.line(t, biomass_adlib_homo_s[8],
                color=colors[2], line_dash='dashed')

adlib_plot.legend.location = "bottom_right"

print('{} Running Stochastic Starvation simulations'.
      format(datetime.datetime.now()))
stochastic = Simulator(initial_pops, 1, input_forage.starve)
starve     = stochastic.run(t)
starve_homo_r = starve[:, :trials]
starve_hetero = starve[:, trials: 2*trials]
starve_homo_s = starve[:, 2*trials:]
biomass_data_homo_r = extract_data(starve_homo_r)
biomass_data_hetero = extract_data(starve_hetero)
biomass_data_homo_s = extract_data(starve_homo_s)

starve_plot = plt.figure(plot_width=plot_width,
                         plot_height=plot_height)
starve_plot.title.text       = 'Simulation of Growth, Number of Trials: {}'.\
    format(trials)
starve_plot.yaxis.axis_label = 'biomass (mg)'
starve_plot.xaxis.axis_label = 'time (days)'

starve_plot.line(t, biomass_data_homo_r[0],
                 color=colors[0],
                 legend='Mean Resistant')
starve_plot.line(t, biomass_data_homo_r[7],
                 color=colors[0], line_dash='dashed',
                 legend='95% Confidence Resistant')
starve_plot.line(t, biomass_data_homo_r[8],
                 color=colors[0], line_dash='dashed')

starve_plot.line(t, biomass_data_hetero[0],
                 color=colors[1],
                 legend='Mean Heterozygous')
starve_plot.line(t, biomass_data_hetero[7],
                 color=colors[1], line_dash='dashed',
                 legend='95% Confidence Heterozygous')
starve_plot.line(t, biomass_data_hetero[8],
                 color=colors[1], line_dash='dashed')

starve_plot.line(t, biomass_data_homo_s[0],
                 color=colors[2],
                 legend='Mean Susceptible')
starve_plot.line(t, biomass_data_homo_s[7],
                 color=colors[2], line_dash='dashed',
                 legend='95% Confidence Susceptible')
starve_plot.line(t, biomass_data_homo_s[8],
                 color=colors[2], line_dash='dashed')

starve_plot.legend.location = "bottom_right"

layout = lay.column(euler_plot, rk4_plot, adlib_plot, starve_plot)

plt.show(layout)

# plt.figure()
# # #       Plot model
# # plt.plot(t, data_homo_r[0], 'b:', label='Model Resistant')
# # plt.plot(t, data_hetero[0], 'r:', label='Model Heterozygous')
# # plt.plot(t, data_homo_s[0], 'k:', label='Model Susceptible')
# #       Plot means
# plt.plot(t, biomass_data_homo_r[0], 'b', label='Mean Resistant')
# plt.plot(t, biomass_data_hetero[0], 'r', label='Mean Heterozygous')
# plt.plot(t, biomass_data_homo_s[0], 'k', label='Mean Susceptible')
# # #       Plot min/max
# # plt.plot(t, biomass_data_homo_r[2], 'b--', label='Min/Max Resistant')
# # plt.plot(t, biomass_data_homo_r[3], 'b--')
# # plt.plot(t, biomass_data_hetero[2], 'r--', label='Min/Max Heterozygous')
# # plt.plot(t, biomass_data_hetero[3], 'r--')
# # plt.plot(t, biomass_data_homo_s[2], 'k--', label='Min/Max Susceptible')
# # plt.plot(t, biomass_data_homo_s[3], 'k--')
# # #       Plot SEM interval
# # plt.plot(t, biomass_data_homo_r[5], 'b--',
# #          label='95% Confidence Resistant')
# # plt.plot(t, biomass_data_homo_r[6], 'b--')
# # plt.plot(t, biomass_data_hetero[5], 'r--',
# #          label='95% Confidence Heterozygous')
# # plt.plot(t, biomass_data_hetero[6], 'r--')
# # plt.plot(t, biomass_data_homo_s[5], 'k--',
# #          label='95% Confidence Susceptible')
# # plt.plot(t, biomass_data_homo_s[6], 'k--')
# #       Plot Quantile interval
# plt.plot(t, biomass_data_homo_r[7], 'b--', label='95% Confidence Resistant')
# plt.plot(t, biomass_data_homo_r[8], 'b--')
# plt.plot(t, biomass_data_hetero[7], 'r--', label='95% Confidence Heterozygous')
# plt.plot(t, biomass_data_hetero[8], 'r--')
# plt.plot(t, biomass_data_homo_s[7], 'k--', label='95% Confidence Susceptible')
# plt.plot(t, biomass_data_homo_s[8], 'k--')
# # #       Plot pupation data
# # plt.axhline(input_biomass.fin_point_r[1], color='b', linestyle=':')
# # plt.axvline(input_biomass.fin_point_r[0], color='b', linestyle=':',
# #             label='Resistant Pupation')
# # plt.axhline(input_biomass.fin_point_s[1], color='k', linestyle=':')
# # plt.axvline(input_biomass.fin_point_s[0], color='k', linestyle=':',
# #             label='Susceptible Pupation')
# #       Add plot labels
# plt.legend()
# plt.xlabel('time (days)')
# plt.ylabel('mass (mg)')
# plt.title('Larva Starvation Growth {} Trials'.format(trials))
# #       Show/save plot
# if save_fig:
#     plt.savefig('Starvation_Growth.png')
# plt.show()
