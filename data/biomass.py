import numpy             as np
import scipy.optimize    as opt

import data.input_data as input_data

import source.keyword as keyword

import source.biomass.models as models


class EggMass(object):
    """
    Class to find the parameters for the egg_mass models from data:

    Variables:
        number: list of samples of egg_mass egg counts
        mass:   list of samples of egg_mass total mass
    """

    def __init__(self, number: list,
                 mass: list):
        self.number = number
        self.mass   = mass

    def _mean_number(self) -> float:
        """
        Get the average number of eggs in an egg_mass

        Returns:
            mean of number
        """

        return float(np.mean(self.number))

    def _mean_mass(self) -> float:
        """
        Get the average total mass of an egg_mass

        Returns:
            mean of mass
        """

        return float(np.mean(self.mass))

    def _std_mass(self) -> float:
        """
        Get the standard deviation in total mass of egg_mass

        Returns:
            std of mass
        """

        return float(np.std(self.mass))

    @staticmethod
    def _start_mass(mass:   float,
                    number: float) -> float:
        """
        Get the mass of a single egg (initial mass)

        Args:
            mass:   total mass of egg_mass
            number: number of eggs in egg_mass

        Returns:
            mass/number
        """

        return mass/number

    def parameters(self) -> tuple:
        """
        Get the parameters from the data

        Returns:
            (mean_number, mean_mass, std_mass, init_mass)
        """

        mean_number = self._mean_number()
        mean_mass   = self._mean_mass()
        std_mass    = self._std_mass()
        start_mass  = self._start_mass(mean_mass, mean_number)

        return mean_number, mean_mass, std_mass, start_mass


def egg_mass(number: list,
             mass:   list) -> tuple:
    """
    Calculate the parameters for egg_mass

    Args:
        number: samples of numbers of eggs in egg_mass
        mass:   samples of total mass of egg_mass

    Returns:
        (mean_number, mean_mass, std_mass, init_mass)
    """

    return EggMass(number, mass).parameters()


class Biomass(object):
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

    def __init__(self, m_0: float,
                 m_m: float,
                 t_m: float,
                 m_f: float,
                 t_f: float):
        self.m_0 = m_0

        self.m_m = m_m
        self.t_m = t_m

        self.m_f = m_f
        self.t_f = t_f

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

    def parameters(self) -> tuple:
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


def biomass(start_mass: float,
            mid_mass:   float,
            mid_time:   float,
            fin_mass:   float,
            fin_time:   float) -> tuple:
    """
    Calculate the biomass system parameters

    Args:
        start_mass: initial_mass
        mid_mass:   middle mass
        mid_time:   middle mass time
        fin_mass:   final mass
        fin_time:   final mass time

    Returns:
        (alpha, beta, max_mass, mass_const)
    """

    return Biomass(start_mass,
                   mid_mass,
                   mid_time,
                   fin_mass,
                   fin_time).parameters()


# Find the fit data
#       Egg fit data
egg_mass_data = egg_mass(input_data.egg_mass_number,
                         input_data.egg_mass_samples)
init_mass_homo_s = egg_mass_data[3]
init_mass_homo_r = egg_mass_data[3] * input_data.homo_r_mass_factor

#       Biomass fit data
biomass_data_homo_r = biomass(init_mass_homo_r,
                              input_data.mass_middle_r,
                              input_data.time_middle_r,
                              input_data.mass_final_r,
                              input_data.time_final_r)
biomass_data_homo_s = biomass(init_mass_homo_s,
                              input_data.mass_middle_r,
                              input_data.time_middle_r,
                              input_data.mass_final_r,
                              input_data.time_final_r)


# Create the data points
mid_point_r = (input_data.time_middle_r, input_data.mass_middle_r)
mid_point_s = (input_data.time_middle_s, input_data.mass_middle_s)
fin_point_r = (input_data.time_final_r,  input_data.mass_final_r)
fin_point_s = (input_data.time_final_s,  input_data.mass_final_s)


# Generate the input models
#       max_gut
max_gut = models.MaxGut()
#       growth
growth_alpha_homo_s = biomass_data_homo_s[0]
growth_alpha_homo_r = biomass_data_homo_r[0]
growth_alpha_hetero = input_data.hetero(growth_alpha_homo_s,
                                        growth_alpha_homo_r)
growth_alpha        = {keyword.homo_s:  growth_alpha_homo_s,
                       keyword.homo_r:  growth_alpha_homo_r,
                       keyword.hetero:  growth_alpha_hetero}
growth_beta_homo_s  = biomass_data_homo_s[1]
growth_beta_homo_r  = biomass_data_homo_r[1]
growth_beta_hetero  = input_data.hetero(growth_beta_homo_s,
                                        growth_beta_homo_r)
growth_beta         = {keyword.homo_s:  growth_beta_homo_s,
                       keyword.homo_r:  growth_beta_homo_r,
                       keyword.hetero:  growth_beta_hetero}

growth = models.Growth(growth_alpha,
                       growth_beta)
#       init_num
init_num_lam = egg_mass_data[0]

init_num     = models.InitNum(init_num_lam)
#       init_mass
init_mass_mu_homo_s  = egg_mass_data[1]
init_mass_mu_homo_r  = egg_mass_data[1] * input_data.homo_r_mass_factor
init_mass_mu_hetero  = input_data.hetero(init_mass_mu_homo_s,
                                         init_mass_mu_homo_r)
init_mass_mu         = {keyword.homo_s:  init_mass_mu_homo_s,
                        keyword.homo_r:  init_mass_mu_homo_r,
                        keyword.hetero:  init_mass_mu_hetero}
init_mass_sigma      = egg_mass_data[2]
init_mass_max_homo_s = biomass_data_homo_s[2]
init_mass_max_homo_r = biomass_data_homo_r[2]
init_mass_max_hetero = input_data.hetero(init_mass_max_homo_s,
                                         init_mass_max_homo_r)
init_mass_maximum    = {keyword.homo_s:  init_mass_max_homo_s,
                        keyword.homo_r:  init_mass_max_homo_r,
                        keyword.hetero:  init_mass_max_hetero}

init_mass = models.InitMass(init_mass_mu,
                            init_mass_sigma,
                            init_mass_maximum)
#       init_juvenile
init_juvenile_lam     = init_num_lam
init_juvenile_mu      = init_mass_mu
init_juvenile_sigma   = init_mass_sigma
init_juvenile_maximum = init_mass_maximum

init_juvenile = models.InitJuvenile(init_juvenile_lam,
                                    init_juvenile_mu,
                                    init_juvenile_sigma,
                                    init_juvenile_maximum)
#       init_mature
init_mature_mu_homo_s = input_data.mass_final_s
init_mature_mu_homo_r = input_data.mass_final_r
init_mature_mu_hetero = input_data.hetero(init_mature_mu_homo_s,
                                          init_mature_mu_homo_r)
init_mature_mu        = {keyword.homo_s:  init_mature_mu_homo_s,
                         keyword.homo_r:  init_mature_mu_homo_r,
                         keyword.hetero:  init_mature_mu_hetero}
init_mature_sigma     = input_data.mass_sigma
init_mature_maximum   = init_mass_maximum

init_mature = models.InitMature(init_mature_mu,
                                init_mature_sigma,
                                init_mature_maximum)
#       init_plant
init_plant_mu      = input_data.leaf_mass_mu
init_plant_sigma   = input_data.leaf_mass_sigma
init_plant_maximum = input_data.leaf_mass_max

init_plant = models.InitPlant(init_plant_mu,
                              init_plant_sigma,
                              init_plant_maximum)
