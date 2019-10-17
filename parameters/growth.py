import dataclasses    as dclass
import numpy          as np
import scipy.optimize as opt

import parameters.basic_data   as data
import parameters.init_biomass as init_bio


@dclass.dataclass
class Growth(object):
    """
    Class to fit the biomass parameters to known data:
        Biomass is assumed to be modeled via the West et.al. Mass model
            m^0.25/M = 1 - [1 - m_0^0.25/M]exp(-at/4M)

    Variables:
        m_0: initial mass

        m_m: middle mass
        t_m: middle mass time

        m_f: final mass
        t_f: final mass time

    Methods:
        parameters: return a tuple of parameters
    """

    m_0: float

    m_m_mean: float
    m_m_sem:  float
    t_m_mean: float
    t_m_sem:  float

    m_f_mean: float
    m_f_sem:  float
    t_f_mean: float
    t_f_sem:  float

    m_m: float = None
    t_m: float = None
    m_f: float = None
    t_f: float = None

    def __post_init__(self):
        """Sets the actual values from the mean and sem values"""

        self.m_m = self.m_m_mean + self.m_m_sem
        self.t_m = self.t_m_mean - self.t_m_sem
        self.m_f = self.m_f_mean + self.m_f_sem
        self.t_f = self.t_f_mean - self.t_f_sem

    def _root_fun(self, mass_const: float) -> float:
        """
        Mass constant root finding function
            fun(M) = [(M-m_m^0.25)/(M - m_0^0.25)]^t_f -
                [(M-m_f^0.25)/(M-m_0^0.25)]^t_m

        Args:
            mass_const: mass (M in equation)

        Returns:
            evaluation of above equation fun(M)
        """

        bottom = mass_const - self.m_0**0.25

        top_m = mass_const - self.m_m**0.25
        top_f = mass_const - self.m_f**0.25

        exp_m = top_m/bottom
        exp_f = top_f/bottom

        return exp_m**self.t_f - exp_f**self.t_m

    def _mass_constant(self) -> float:
        """
        Calculate the mass constant M from West et.al. biomass model:
            m^0.25/M = 1 - [1 - m_0^0.25/M]exp(-at/4M)

        Returns:
            the mass constant M
        """

        sol = opt.root(self._root_fun, np.array(4))

        return float(sol.x[0])

    def _alpha(self, mass_const: float) -> float:
        """
        Find the alpha constant in the West et.al. model
            m^0.25/M = 1 - [1 - m_0^0.25/M]exp(-alpha*t/4M)
        where M=m from input

        That is:
            alpha = (-4M/t_m)ln[(M-m_m^0.25)/(M-m_0^0.25)]

        Args:
            mass_const: the mass constant

        Returns:
            the value for alpha
        """

        bottom = mass_const - self.m_0**0.25
        top    = mass_const - self.m_m**0.25

        coeff = -4*mass_const/self.t_m
        ln    = np.log(top/bottom)

        return coeff*ln

    @staticmethod
    def _max_mass(mass_const: float) -> float:
        """
        Find the maximum mass:
            m = max_mass^0.25

        Args:
            mass_const: the mass constant

        Returns:
            the maximum mass
        """

        return mass_const**4

    @staticmethod
    def _beta(alpha:      float,
              mass_const: float) -> float:
        """
        Find the beta West et.al. constant which is given by:
            beta = alpha/mass_const

        Args:
            alpha:      alpha constant
            mass_const: mass constant

        Returns:
            value for beta
        """

        return alpha/mass_const

    def params(self) -> tuple:
        """
        Calculate the parameters from the data

        Returns:
            (alpha, beta, max_mass, mass_const)
        """

        mass_const = self._mass_constant()
        alpha      = self._alpha(mass_const)
        max_mass   = self._max_mass(mass_const)
        beta       = self._beta(alpha, mass_const)

        return alpha, beta, max_mass, mass_const

    @classmethod
    def parameters(cls, mass_0:   float,
                        time:     list,
                        time_sem: list,
                        mass:     list,
                        mass_sem: list) -> tuple:
        """
        Use the growth class to calculate the parameters needed for the growth
            model

        Args:
            mass_0:   initial mass
            time:     time points
            time_sem: sem in each point
            mass:     mass points
            mass_sem: sem in each mass point

        Returns:
            (alpha, beta, max_mass, mass_const)
        """

        t_m_mean = time[0]
        t_f_mean = time[1]
        t_m_sem  = time_sem[0]
        t_f_sem  = time_sem[1]

        m_m_mean = mass[0]
        m_f_mean = mass[1]
        m_m_sem  = mass_sem[0]
        m_f_sem  = mass_sem[1]

        growth = cls(mass_0,
                     m_m_mean, m_m_sem,
                     t_m_mean, t_m_sem,
                     m_f_mean, m_f_sem,
                     t_f_mean, t_f_sem)

        return growth.params()


# Generate the growth parameters
growth_ss = Growth.parameters(init_bio.mu_0_larva_ss,
                              data.growth_times_ss,
                              data.growth_times_sem_ss,
                              data.growth_mass_ss,
                              data.growth_mass_sem_ss)
growth_rr = Growth.parameters(init_bio.mu_0_larva_rr,
                              data.growth_times_rr,
                              data.growth_times_sem_rr,
                              data.growth_mass_rr,
                              data.growth_mass_sem_rr)

alpha_ss    = growth_ss[0]
beta_ss     = growth_ss[1]
max_mass_ss = growth_ss[2]

alpha_rr    = growth_rr[0]
beta_rr     = growth_rr[1]
max_mass_rr = growth_rr[2]
