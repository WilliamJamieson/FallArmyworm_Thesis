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

import models.dominance    as dom
import models.forage       as forage
import models.growth       as growth
import models.init_biomass as init_bio
import models.reproduction as repro

import source.hint    as hint
import source.keyword as keyword

import source.simulation.simulation as main_simulation


# Plotting parameters
dominance  = 0
trials     = 1000
num_steps  = 40
use_hetero = False

line_width       = 2
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
save_file = 'biomass_plots.html'

plt.output_file(save_file)

alpha      = dom.dom(param.alpha_ss,
                     param.alpha_rr,
                     dominance)
beta       = dom.dom(param.beta_ss,
                     param.beta_rr,
                     dominance)
max_mass   = dom.dom(param.max_mass_ss,
                     param.max_mass_rr,
                     dominance)
mass_const = dom.dom(param.mass_const_ss,
                     param.mass_const_rr,
                     dominance)
mass_0     = dom.dom(param.mu_0_larva_ss,
                     param.mu_0_larva_rr,
                     dominance)


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

    @classmethod
    def exact(cls, genotype: str,
                   times:    list) -> np.array:
        """
        Run an exact West et.al. model for the phenotype and times given:

        Args:
            genotype: genotype to use
            times:    times to run model at

        Returns:
            list of values for model at times
        """

        a             = alpha[     genotype]
        mass_constant = mass_const[genotype]
        m_0           = mass_0[    genotype]

        west = cls(a, mass_constant, m_0)

        return np.array(west.run(times))


@dclass.dataclass
class Approx(object):
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

    @classmethod
    def euler(cls, genotype: str,
                   times:    list) -> np.array:
        """
        Run an Euler simulation for the West et.al. model

        Args:
            genotype: genotype to use
            times:    times to approximate at

        Returns:
            list of approximate values using Euler's method
        """

        a   = alpha[ genotype]
        b   = beta[  genotype]
        m_0 = mass_0[genotype]

        euler_method = cls(a, b, m_0)

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
    attrs       = {0: tracking.genotype_attrs}
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
                    repro.init_sex(param.female_prob)]
    input_variables = param.repro_values

    nums:       hint.init_pops
    bt_prop:    float
    forage:     hint.forage_plant
    develop:    callable        = None
    steps:      list            = None
    simulation: hint.simulation = None

    def __post_init__(self):
        input_models = self.input_models.copy()
        input_models.append(self.forage)

        inputs = tuple(input_models)

        if self.develop is not None:
            self.input_models.append(self.develop)

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

# Generate the ad libitum plots
t            = list(range(num_steps))
print('{} Running Exact simulations'.format(datetime.datetime.now()))
exact_homo_r = West.exact(keyword.homo_r, t)
exact_hetero = West.exact(keyword.hetero, t)
exact_homo_s = West.exact(keyword.homo_s, t)

print('{} Running Euler simulations'.format(datetime.datetime.now()))
euler_homo_r = Approx.euler(keyword.homo_r, t)
euler_hetero = Approx.euler(keyword.hetero, t)
euler_homo_s = Approx.euler(keyword.homo_s, t)

euler_plot = plt.figure(plot_width=plot_width,
                        plot_height=plot_height)
euler_plot.title.text       = "Simulation of Growth, Euler's Method"
euler_plot.yaxis.axis_label = 'biomass (mg)'
euler_plot.xaxis.axis_label = 'time (days)'

euler_plot.add_layout(fin_time_homo_r)
euler_plot.add_layout(fin_mass_homo_r)
euler_plot.add_layout(fin_time_homo_s)
euler_plot.add_layout(fin_mass_homo_s)

euler_plot.line(t, exact_homo_r,
                color=colors[0], line_width=line_width,
                legend='Exact Resistant')
euler_plot.triangle(t, euler_homo_r,
                    color=colors[0], size=point_size,
                    legend='Model Resistant')
euler_plot.line(t, exact_homo_s,
                color=colors[1], line_width=line_width,
                legend='Exact Susceptible')
euler_plot.circle(t, euler_homo_s,
                  color=colors[1], size=point_size,
                  legend='Model Susceptible')
if use_hetero:
    euler_plot.line(t, exact_hetero,
                    color=colors[2], line_width=line_width,
                    legend='Exact Heterozygous')
    euler_plot.square(t, euler_hetero,
                      color=colors[2], size=point_size,
                      legend='Model Heterozygous')

euler_plot.x([fin_point_rr[0]],
             [fin_point_rr[1]],
             color=colors[0], size=20,
             legend='Resistant Pupation')
euler_plot.x([fin_point_ss[0]],
             [fin_point_ss[1]],
             color=colors[1], size=20,
             legend='Susceptible Pupation')

euler_plot.legend.location = "bottom_right"

euler_plot.title.text_font_size = title_font_size
euler_plot.legend.label_text_font_size = legend_font_size
euler_plot.yaxis.axis_line_width = axis_line_width
euler_plot.xaxis.axis_line_width = axis_line_width
euler_plot.yaxis.axis_label_text_font_size = axis_font_size
euler_plot.xaxis.axis_label_text_font_size = axis_font_size
euler_plot.yaxis.major_label_text_font_size = axis_tick_font_size
euler_plot.xaxis.major_label_text_font_size = axis_tick_font_size
euler_plot.ygrid.grid_line_width = grid_line_width
euler_plot.xgrid.grid_line_width = grid_line_width


initial_pops = ((0, 0, 0),
                (1, 1, 1),
                (0, 0, 0),
                (0, 0, 0),
                (0, 0, 0))
simulator_bt = Simulator(initial_pops,
                         1,
                         forage.adlibitum(1))
biomass_bt  = simulator_bt.run(t)
biomass_bt_homo_r = biomass_bt[:, 0]
biomass_bt_hetero = biomass_bt[:, 1]
biomass_bt_homo_s = biomass_bt[:, 2]

rk4_plot = plt.figure(plot_width=plot_width,
                      plot_height=plot_height)
rk4_plot.title.text       = 'Simulation of Growth, Runge-Kutta 4'
rk4_plot.yaxis.axis_label = 'biomass (mg)'
rk4_plot.xaxis.axis_label = 'time (days)'

rk4_plot.add_layout(fin_time_homo_r)
rk4_plot.add_layout(fin_mass_homo_r)
rk4_plot.add_layout(fin_time_homo_s)
rk4_plot.add_layout(fin_mass_homo_s)

rk4_plot.line(t, exact_homo_r,
              color=colors[0], line_width=line_width,
              legend='Exact Resistant')
rk4_plot.triangle(t, biomass_bt_homo_r,
                  color=colors[0], size=point_size,
                  legend='Model Resistant')
rk4_plot.line(t, exact_homo_s,
              color=colors[1], line_width=line_width,
              legend='Exact Susceptible')
rk4_plot.circle(t, biomass_bt_homo_s,
                color=colors[1], size=point_size,
                legend='Model Susceptible')
if use_hetero:
    rk4_plot.line(t, exact_hetero,
                  color=colors[2], line_width=line_width,
                  legend='Exact Heterozygous')
    rk4_plot.square(t, biomass_bt_hetero,
                    color=colors[2], size=point_size,
                    legend='Model Heterozygous')

rk4_plot.x([fin_point_rr[0]],
           [fin_point_rr[1]],
           color=colors[0], size=20,
           legend='Resistant Pupation')
rk4_plot.x([fin_point_ss[0]],
           [fin_point_ss[1]],
           color=colors[1], size=20,
           legend='Susceptible Pupation')

rk4_plot.legend.location = "bottom_right"

rk4_plot.title.text_font_size = title_font_size
rk4_plot.legend.label_text_font_size = legend_font_size
rk4_plot.yaxis.axis_line_width = axis_line_width
rk4_plot.xaxis.axis_line_width = axis_line_width
rk4_plot.yaxis.axis_label_text_font_size = axis_font_size
rk4_plot.xaxis.axis_label_text_font_size = axis_font_size
rk4_plot.yaxis.major_label_text_font_size = axis_tick_font_size
rk4_plot.xaxis.major_label_text_font_size = axis_tick_font_size
rk4_plot.ygrid.grid_line_width = grid_line_width
rk4_plot.xgrid.grid_line_width = grid_line_width


# Generate the stochastic plots
initial_pops = ((0,      0,      0),
                (trials, trials, trials),
                (0,      0,      0),
                (0,      0,      0),
                (0,      0,      0))
print('{} Running Stochastic ad libitum simulations'.
      format(datetime.datetime.now()))
adlibitum = Simulator(initial_pops, 1,
                      forage.starvation(1,
                                        param.theta_adlibitum,
                                        param.sig_scarce))
adlib     = adlibitum.run(t)
adlib_homo_r = adlib[:, :trials]
adlib_hetero = adlib[:, trials: 2*trials]
adlib_homo_s = adlib[:, 2*trials:]
biomass_adlib_homo_r = extract_data(adlib_homo_r)
biomass_adlib_hetero = extract_data(adlib_hetero)
biomass_adlib_homo_s = extract_data(adlib_homo_s)

adlib_plot = plt.figure(plot_width=plot_width,
                        plot_height=plot_height)
adlib_plot.title.text       = 'Simulation of 95% Ad Libitum Growth, ' \
                              'Number of Trials: {}'.format(trials)
adlib_plot.yaxis.axis_label = 'biomass (mg)'
adlib_plot.xaxis.axis_label = 'time (days)'

adlib_plot.add_layout(fin_time_homo_r)
adlib_plot.add_layout(fin_mass_homo_r)
adlib_plot.add_layout(fin_time_homo_s)
adlib_plot.add_layout(fin_mass_homo_s)

adlib_plot.line(t, biomass_adlib_homo_r[0],
                color=colors[0], line_width=line_width,
                legend='Mean Resistant')
adlib_plot.line(t, biomass_adlib_homo_r[7],
                color=colors[0], line_dash='dashed', line_width=line_width,
                legend='95% Confidence Resistant')
adlib_plot.line(t, biomass_adlib_homo_r[8],
                color=colors[0], line_dash='dashed', line_width=line_width)

adlib_plot.line(t, biomass_adlib_homo_s[0],
                color=colors[1], line_width=line_width,
                legend='Mean Susceptible')
adlib_plot.line(t, biomass_adlib_homo_s[7],
                color=colors[1], line_dash='dashed', line_width=line_width,
                legend='95% Confidence Susceptible')
adlib_plot.line(t, biomass_adlib_homo_s[8],
                color=colors[1], line_dash='dashed', line_width=line_width)

if use_hetero:
    adlib_plot.line(t, biomass_adlib_hetero[0],
                    color=colors[2], line_width=line_width,
                    legend='Mean Heterozygous')
    adlib_plot.line(t, biomass_adlib_hetero[7],
                    color=colors[2], line_dash='dashed', line_width=line_width,
                    legend='95% Confidence Heterozygous')
    adlib_plot.line(t, biomass_adlib_hetero[8],
                    color=colors[2], line_dash='dashed', line_width=line_width)

adlib_plot.x([fin_point_rr[0]],
             [fin_point_rr[1]],
             color=colors[0], size=20,
             legend='Resistant Pupation')
adlib_plot.x([fin_point_ss[0]],
             [fin_point_ss[1]],
             color=colors[1], size=20,
             legend='Susceptible Pupation')

adlib_plot.legend.location = "bottom_right"

adlib_plot.title.text_font_size = title_font_size
adlib_plot.legend.label_text_font_size = legend_font_size
adlib_plot.yaxis.axis_line_width = axis_line_width
adlib_plot.xaxis.axis_line_width = axis_line_width
adlib_plot.yaxis.axis_label_text_font_size = axis_font_size
adlib_plot.xaxis.axis_label_text_font_size = axis_font_size
adlib_plot.yaxis.major_label_text_font_size = axis_tick_font_size
adlib_plot.xaxis.major_label_text_font_size = axis_tick_font_size
adlib_plot.ygrid.grid_line_width = grid_line_width
adlib_plot.xgrid.grid_line_width = grid_line_width


adlib_box = plt.figure(plot_width=plot_width,
                        plot_height=plot_height)
adlib_box.title.text       = 'Simulation of 95% Ad Libitum Growth Box Plot, ' \
                              'Number of Trials: {}'.format(trials)
adlib_box.yaxis.axis_label = 'biomass (mg)'
adlib_box.xaxis.axis_label = 'time (days)'

adlib_box = plt.figure(plot_width=plot_width,
                       plot_height=plot_height)
adlib_box.title.text       = 'Simulation of 95% Ad Libitum Growth Plot, ' \
                             'Number of Trials: {}'.format(trials)
adlib_box.yaxis.axis_label = 'biomass (mg)'
adlib_box.xaxis.axis_label = 'time (days)'

adlib_box.add_layout(fin_time_homo_r)
adlib_box.add_layout(fin_mass_homo_r)
adlib_box.add_layout(fin_time_homo_s)
adlib_box.add_layout(fin_mass_homo_s)

adlib_box.triangle(t, biomass_adlib_homo_r[0],
                    color=colors[0], size=point_size_stoch,
                    legend='Mean Resistant')
adlib_box.line(t, biomass_adlib_homo_r[0],
                color=colors[0], line_width=line_width,
                legend='Mean Resistant')
adlib_box.segment(x0=t, y0=biomass_adlib_homo_r[7],
                   x1=t, y1=biomass_adlib_homo_r[8],
                   line_color=colors[0], line_width=line_width/2,
                   line_cap='square')
adlib_box.rect(t, biomass_adlib_homo_r[7], 0.5, 0.1,
                line_color=colors[0])
adlib_box.rect(t, biomass_adlib_homo_r[8], 0.5, 0.1,
                line_color=colors[0])

adlib_box.circle(t, biomass_adlib_homo_s[0],
                  color=colors[1], size=point_size/2,
                  legend='Mean Susceptible')
adlib_box.line(t, biomass_adlib_homo_s[0],
                color=colors[1], line_width=line_width,
                legend='Mean Susceptible')
adlib_box.segment(x0=t, y0=biomass_adlib_homo_s[7],
                   x1=t, y1=biomass_adlib_homo_s[8],
                   line_color=colors[1], line_width=line_width/2,
                   line_cap='square')
adlib_box.rect(t, biomass_adlib_homo_s[7], 0.5, 0.1,
                line_color=colors[1])
adlib_box.rect(t, biomass_adlib_homo_s[8], 0.5, 0.1,
                line_color=colors[1])

adlib_box.x([fin_point_rr[0]],
             [fin_point_rr[1]],
             color=colors[0], size=20,
             legend='Resistant Pupation')
adlib_box.x([fin_point_ss[0]],
             [fin_point_ss[1]],
             color=colors[1], size=20,
             legend='Susceptible Pupation')

adlib_box.legend.location = "bottom_right"

adlib_box.title.text_font_size = title_font_size
adlib_box.legend.label_text_font_size = legend_font_size
adlib_box.yaxis.axis_line_width = axis_line_width
adlib_box.xaxis.axis_line_width = axis_line_width
adlib_box.yaxis.axis_label_text_font_size = axis_font_size
adlib_box.xaxis.axis_label_text_font_size = axis_font_size
adlib_box.yaxis.major_label_text_font_size = axis_tick_font_size
adlib_box.xaxis.major_label_text_font_size = axis_tick_font_size
adlib_box.ygrid.grid_line_width = grid_line_width
adlib_box.xgrid.grid_line_width = grid_line_width


print('{} Running Stochastic Starvation simulations'.
      format(datetime.datetime.now()))
stochastic = Simulator(initial_pops, 1,
                       forage.starvation(1,
                                         param.theta_scarce,
                                         param.sig_scarce))
starve        = stochastic.run(t)
starve_homo_r = starve[:, :trials]
starve_hetero = starve[:, trials: 2*trials]
starve_homo_s = starve[:, 2*trials:]
biomass_data_homo_r = extract_data(starve_homo_r)
biomass_data_hetero = extract_data(starve_hetero)
biomass_data_homo_s = extract_data(starve_homo_s)

starve_plot = plt.figure(plot_width=plot_width,
                         plot_height=plot_height)
starve_plot.title.text       = 'Simulation of 80% Ad Libitum Growth, ' \
                               'Number of Trials: {}'.format(trials)
starve_plot.yaxis.axis_label = 'biomass (mg)'
starve_plot.xaxis.axis_label = 'time (days)'

starve_plot.add_layout(fin_time_homo_r)
starve_plot.add_layout(fin_mass_homo_r)
starve_plot.add_layout(fin_time_homo_s)
starve_plot.add_layout(fin_mass_homo_s)

starve_plot.line(t, biomass_data_homo_r[0],
                 color=colors[0], line_width=line_width,
                 legend='Mean Resistant')
starve_plot.line(t, biomass_data_homo_r[7],
                 color=colors[0], line_dash='dashed', line_width=line_width,
                 legend='95% Confidence Resistant')
starve_plot.line(t, biomass_data_homo_r[8], line_width=line_width,
                 color=colors[0], line_dash='dashed')

starve_plot.line(t, biomass_data_homo_s[0],
                 color=colors[1], line_width=line_width,
                 legend='Mean Susceptible')
starve_plot.line(t, biomass_data_homo_s[7], line_width=line_width,
                 color=colors[1], line_dash='dashed',
                 legend='95% Confidence Susceptible')
starve_plot.line(t, biomass_data_homo_s[8], line_width=line_width,
                 color=colors[1], line_dash='dashed')

if use_hetero:
    starve_plot.line(t, biomass_data_hetero[0],
                     color=colors[2],
                     legend='Mean Heterozygous')
    starve_plot.line(t, biomass_data_hetero[7],
                     color=colors[2], line_dash='dashed', line_width=line_width,
                     legend='95% Confidence Heterozygous')
    starve_plot.line(t, biomass_data_hetero[8], line_width=line_width,
                     color=colors[2], line_dash='dashed')

starve_plot.x([fin_point_rr[0]],
              [fin_point_rr[1]],
              color=colors[0], size=20,
              legend='Resistant Pupation')
starve_plot.x([fin_point_ss[0]],
              [fin_point_ss[1]],
              color=colors[1], size=20,
              legend='Susceptible Pupation')

starve_plot.legend.location = "bottom_right"

starve_plot.title.text_font_size = title_font_size
starve_plot.legend.label_text_font_size = legend_font_size
starve_plot.yaxis.axis_line_width = axis_line_width
starve_plot.xaxis.axis_line_width = axis_line_width
starve_plot.yaxis.axis_label_text_font_size = axis_font_size
starve_plot.xaxis.axis_label_text_font_size = axis_font_size
starve_plot.yaxis.major_label_text_font_size = axis_tick_font_size
starve_plot.xaxis.major_label_text_font_size = axis_tick_font_size
starve_plot.ygrid.grid_line_width = grid_line_width
starve_plot.xgrid.grid_line_width = grid_line_width


starve_box = plt.figure(plot_width=plot_width,
                        plot_height=plot_height)
starve_box.title.text       = 'Simulation of 95% Ad Libitum Growth Plot, ' \
                             'Number of Trials: {}'.format(trials)
starve_box.yaxis.axis_label = 'biomass (mg)'
starve_box.xaxis.axis_label = 'time (days)'

starve_box.add_layout(fin_time_homo_r)
starve_box.add_layout(fin_mass_homo_r)
starve_box.add_layout(fin_time_homo_s)
starve_box.add_layout(fin_mass_homo_s)

starve_box.triangle(t, biomass_data_homo_r[0],
                     color=colors[0], size=point_size_stoch,
                     legend='Mean Resistant')
starve_box.line(t, biomass_data_homo_r[0],
                color=colors[0], line_width=line_width,
                legend='Mean Resistant')
starve_box.segment(x0=t, y0=biomass_data_homo_r[7],
                   x1=t, y1=biomass_data_homo_r[8],
                   line_color=colors[0], line_width=line_width/2,
                   line_cap='square')
starve_box.rect(t, biomass_data_homo_r[7], 0.5, 0.1,
                line_color=colors[0])
starve_box.rect(t, biomass_data_homo_r[8], 0.5, 0.1,
                line_color=colors[0])

starve_box.circle(t, biomass_data_homo_s[0],
                  color=colors[1], size=point_size_stoch,
                  legend='Mean Susceptible')
starve_box.line(t, biomass_data_homo_s[0],
                color=colors[1], line_width=line_width,
                legend='Mean Susceptible')
starve_box.segment(x0=t, y0=biomass_data_homo_s[7],
                   x1=t, y1=biomass_data_homo_s[8],
                   line_color=colors[1], line_width=line_width/2,
                   line_cap='square')
starve_box.rect(t, biomass_data_homo_s[7], 0.5, 0.1,
                line_color=colors[1])
starve_box.rect(t, biomass_data_homo_s[8], 0.5, 0.1,
                line_color=colors[1])

starve_box.x([fin_point_rr[0]],
             [fin_point_rr[1]],
             color=colors[0], size=20,
             legend='Resistant Pupation')
starve_box.x([fin_point_ss[0]],
             [fin_point_ss[1]],
             color=colors[1], size=20,
             legend='Susceptible Pupation')

starve_box.legend.location = "bottom_right"

starve_box.title.text_font_size = title_font_size
starve_box.legend.label_text_font_size = legend_font_size
starve_box.yaxis.axis_line_width = axis_line_width
starve_box.xaxis.axis_line_width = axis_line_width
starve_box.yaxis.axis_label_text_font_size = axis_font_size
starve_box.xaxis.axis_label_text_font_size = axis_font_size
starve_box.yaxis.major_label_text_font_size = axis_tick_font_size
starve_box.xaxis.major_label_text_font_size = axis_tick_font_size
starve_box.ygrid.grid_line_width = grid_line_width
starve_box.xgrid.grid_line_width = grid_line_width


digits       = 3
instar_steps = 8
instar_trials = 1000
hist_density  = False
hist_bins     = 30
# Third In-star
t            = list(range(instar_steps))
initial_pops = ((0,      0,      0),
                (instar_trials, instar_trials, instar_trials),
                (0,      0,      0),
                (0,      0,      0),
                (0,      0,      0))
print('{} Running Instar simulations'.
      format(datetime.datetime.now()))
instar_3 = Simulator(initial_pops, 1,
                     forage.starvation(1,
                                       param.theta_adlibitum,
                                       param.sig_scarce))
instar        = instar_3.run(t)
instar_homo_r = instar[-1, :instar_trials]
instar_hetero = instar[-1, instar_trials: 2*instar_trials]
instar_homo_s = instar[-1, 2*instar_trials:]

hist_homo_r, edges_homo_r = np.histogram(instar_homo_r,
                                         density=hist_density,
                                         bins=hist_bins)
hist_hetero, edges_hetero = np.histogram(instar_hetero,
                                         density=hist_density,
                                         bins=hist_bins)
hist_homo_s, edges_homo_s = np.histogram(instar_homo_s,
                                         density=hist_density,
                                         bins=hist_bins)

mean_homo_r = np.mean(instar_homo_r)
std_homo_r  = np.std( instar_homo_r)

mean_hetero = np.mean(instar_hetero)
std_hetero  = np.std( instar_hetero)

mean_homo_s = np.mean(instar_homo_s)
std_homo_s  = np.std( instar_homo_s)

hist_plot_homo_r = plt.figure(plot_width=plot_width,
                              plot_height=plot_height)
hist_plot_homo_r.title.text = 'Third Instar Biomass Histogram, Resistant'
hist_plot_homo_r.yaxis.axis_label = 'larva per biomass'
hist_plot_homo_r.xaxis.axis_label = 'biomass (mg)'

hist_plot_homo_r.quad(top=hist_homo_r, bottom=0,
                      left=edges_homo_r[:-1],
                      right=edges_homo_r[1:],
                      fill_color=colors[0],
                      legend='μ={}, σ={}'.
                      format(np.round(mean_homo_r, digits),
                             np.round(std_homo_r, digits)))

hist_plot_homo_r.legend.location = 'top_left'

hist_plot_homo_r.title.text_font_size = title_font_size
hist_plot_homo_r.legend.label_text_font_size = legend_font_size
hist_plot_homo_r.yaxis.axis_line_width = axis_line_width
hist_plot_homo_r.xaxis.axis_line_width = axis_line_width
hist_plot_homo_r.yaxis.axis_label_text_font_size = axis_font_size
hist_plot_homo_r.xaxis.axis_label_text_font_size = axis_font_size
hist_plot_homo_r.yaxis.major_label_text_font_size = axis_tick_font_size
hist_plot_homo_r.xaxis.major_label_text_font_size = axis_tick_font_size
hist_plot_homo_r.ygrid.grid_line_width = grid_line_width
hist_plot_homo_r.xgrid.grid_line_width = grid_line_width

hist_plot_homo_s = plt.figure(plot_width=plot_width,
                              plot_height=plot_height)
hist_plot_homo_s.title.text = 'Third Instar Biomass Histogram, Susceptible'
hist_plot_homo_s.yaxis.axis_label = 'larva per biomass'
hist_plot_homo_s.xaxis.axis_label = 'biomass (mg)'

hist_plot_homo_s.quad(top=hist_homo_s, bottom=0,
                      left=edges_homo_s[:-1],
                      right=edges_homo_s[1:],
                      fill_color=colors[1],
                      legend='μ={}, σ={}'.
                      format(np.round(mean_homo_s, digits),
                             np.round(std_homo_s, digits)))

hist_plot_homo_s.legend.location = 'top_left'

hist_plot_homo_s.title.text_font_size = title_font_size
hist_plot_homo_s.legend.label_text_font_size = legend_font_size
hist_plot_homo_s.yaxis.axis_line_width = axis_line_width
hist_plot_homo_s.xaxis.axis_line_width = axis_line_width
hist_plot_homo_s.yaxis.axis_label_text_font_size = axis_font_size
hist_plot_homo_s.xaxis.axis_label_text_font_size = axis_font_size
hist_plot_homo_s.yaxis.major_label_text_font_size = axis_tick_font_size
hist_plot_homo_s.xaxis.major_label_text_font_size = axis_tick_font_size
hist_plot_homo_s.ygrid.grid_line_width = grid_line_width
hist_plot_homo_s.xgrid.grid_line_width = grid_line_width

hist_plot = plt.figure(plot_width=plot_width,
                              plot_height=plot_height)
hist_plot.title.text = 'Third Instar Biomass Histogram'
hist_plot.yaxis.axis_label = 'larva per biomass'
hist_plot.xaxis.axis_label = 'biomass (mg)'

hist_plot.quad(top=hist_homo_r, bottom=0,
               left=edges_homo_r[:-1],
               right=edges_homo_r[1:],
               fill_color=colors[0],
               legend='Resistant, (μ={}, σ={})'.
               format(np.round(mean_homo_r, digits),
                      np.round(std_homo_r, digits)))

hist_plot.quad(top=hist_homo_s, bottom=0,
               left=edges_homo_s[:-1],
               right=edges_homo_s[1:],
               fill_color=colors[1],
               legend='Susceptible, (μ={}, σ={})'.
               format(np.round(mean_homo_s, digits),
                      np.round(std_homo_s, digits)))


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

print('RR pupation: {}'.format(fin_point_rr))
print('SS pupation: {}'.format(fin_point_ss))

layout = lay.column(euler_plot, rk4_plot, adlib_plot, starve_plot,
                    adlib_box, starve_box,
                    hist_plot_homo_r, hist_plot_homo_s, hist_plot)
plt.show(layout)
