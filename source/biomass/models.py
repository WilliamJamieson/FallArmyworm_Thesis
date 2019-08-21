# TODO: UPDATE THESE FOR NEW SYSTEMS

import numpy       as np
import scipy.stats as stats

import source.hints    as hints
import source.keywords as keywords

import source.models.model as model


class MaxGut(model.Model):
    """
    Class to contain a max_gut model:
        max_gut = mass^(3/4)

    Methods:
        __call__: call the model

    Constructors:
        setup: setup the mathematical model
    """

    keyword = keywords.max_gut

    def __call__(self, mass: float) -> float:
        """
        Run the mathematical model:
            max_gut = mass^(3/4)

        Args:
            mass: insect mass

        Returns:
            the result of the above equation (max_gut)
        """

        return mass**0.75

    @classmethod
    def setup(cls, *args, **kwargs) -> 'MaxGut':
        """
        Setup the model

        Args:
            *args:    place holder
            **kwargs: place holder

        Returns:
            the setup model
        """

        return cls()


class Growth(model.Model):
    """
    Class to contain a growth model:
        growth = alpha*energy - beta*mass

    Variables:
        _alpha: energy variable
        _beta:  cost variable

    Methods:
        __call__: call the model

    Constructors:
        setup: setup the mathematical model
    """

    keyword = keywords.growth

    def __init__(self, alpha: hints.variable,
                       beta:  hints.variable):
        self._alpha = alpha
        self._beta  = beta

    def __call__(self, mass:      float,
                       energy:    float,
                       phenotype: str) -> float:
        """
        Run the mathematical model
            growth = alpha*energy - beta*mass

        Args:
            mass:      insect mass
            energy:    insect energy
            phenotype: insect phenotype

        Returns:
            the result of the above equation (growth)
        """

        alpha = self._alpha(phenotype)
        beta  = self._beta( phenotype)

        return alpha*energy - beta*mass

    @classmethod
    def setup(cls, *args, **kwargs) -> 'Growth':
        """
        Setup the model

        Args:
            *args:    arg[0]= value(s) for alpha, arg[2]=value(s) for beta
            **kwargs: other args

        Returns:
            the setup model
        """

        alpha = cls.setup_variable(*args[0], **kwargs)
        beta  = cls.setup_variable(*args[1], **kwargs)

        return cls(alpha, beta)


class Recovery(model.Model):
    """
    Class to contain a growth model:
        growth = alpha*mass^0.75 - beta*mass

    Variables:
        _alpha: energy variable
        _beta:  cost variable

    Methods:
        __call__: call the model

    Constructors:
        setup: setup the mathematical model
    """

    keyword = keywords.recovery

    def __init__(self, alpha: hints.variable,
                       beta:  hints.variable):
        self._alpha = alpha
        self._beta  = beta

    def __call__(self, mass: float,
                       bt:   str) -> float:
        """
        Run the mathematical model
            growth = alpha*energy - beta*mass

        Args:
            mass: leaf mass
            bt:   plant bt

        Returns:
            the result of the above equation (growth)
        """

        alpha  = self._alpha(bt)
        beta   = self._beta( bt)
        energy = mass**0.75

        return alpha*energy - beta*mass

    @classmethod
    def setup(cls, *args, **kwargs) -> 'Recovery':
        """
        Setup the model

        Args:
            *args:    arg[0]= value(s) for alpha, arg[2]=value(s) for beta
            **kwargs: other args

        Returns:
            the setup model
        """

        alpha = cls.setup_variable(*args[0], **kwargs)
        beta  = cls.setup_variable(*args[1], **kwargs)

        return cls(alpha, beta)


class InitMass(model.Model):
    """
    Class to contain a initial mass model:
        Is made of 2 parts:
            1. model for number of eggs in an egg_mass
            2. model for mass of egg_mass

    Variables:
        _lam: average number of eggs in egg_mass

        _mu:    average mass of an egg_mass
        _sigma: standard deviation in egg_mass

        _max_size: maximum allowed size

    Methods:
        __call__: call the model

    Constructors:
        setup: setup the mathematical model
    """

    keyword = keywords.init_mass

    def __init__(self, lam:      hints.variable,
                       mu:       hints.variable,
                       sigma:    hints.variable,
                       max_size: hints.variable):
        self._lam = lam

        self._mu    = mu
        self._sigma = sigma

        self._max_size = max_size
        
    def _egg_num(self, phenotype: str) -> float:
        """
        Get the number of eggs for the egg mass:
            this is poisson distributed with mean=_lam

        Args:
            phenotype: insect phenotype

        Returns:
            number of eggs in an egg mass
        """

        lam = self._lam(phenotype)

        return stats.poisson.rvs(lam)

    @staticmethod
    def _lower(mu:    float,
               sigma: float) -> float:
        """
        Get lower bound for egg mass distribution

        Args:
            mu:    mean
            sigma: standard deviation

        Returns:
            truncnorm lower bound
        """

        eps = np.finfo(float).eps

        return (eps - mu)/sigma

    def _upper(self, mu:        float,
                     sigma:     float,
                     num:       float,
                     phenotype: str) -> float:
        """
        Get upper bound for egg mass distribution

        Args:
            mu:    mean
            sigma: standard deviation

            num:       number of eggs
            phenotype: insect phenotype

        Returns:
            truncnorm upper bound
        """

        upper = self._max_size(phenotype)*num

        return (upper - mu)/sigma

    def _egg_mass(self, num:       float,
                        phenotype: str) -> float:
        """
        Get the mass for the egg mass:
            this is normally distributed with mean=_mu, std_dev=sigma


        Args:
            num:       number of eggs
            phenotype: insect phenotype

        Returns:
            mass of egg mass
        """

        mu    = self._mu(phenotype)
        sigma = self._sigma(phenotype)

        lower = self._lower(mu, sigma)
        upper = self._upper(mu, sigma, num, phenotype)

        return stats.truncnorm.rvs(lower, upper, loc=mu, scale=sigma)

    def __call__(self, phenotype: str) -> float:
        """
        Run complete statistical model:
            egg_mass/egg_num

        Args:
            phenotype: insect phenotype

        Returns:
            initial mass for one egg
        """

        num  = self._egg_num(phenotype)
        mass = self._egg_mass(num, phenotype)

        return mass/num

    @classmethod
    def setup(cls, *args, **kwargs) -> 'InitMass':
        """

        Args:
            *args:    arg[0]=lam, arg[1]=mu, arg[2]=sigma, arg[3]=max_size
            **kwargs: other args

        Returns:
            setup class
        """

        lam      = cls.setup_variable(*args[0], **kwargs)
        mu       = cls.setup_variable(*args[1], **kwargs)
        sigma    = cls.setup_variable(*args[2], **kwargs)
        max_size = cls.setup_variable(*args[3], **kwargs)

        return cls(lam, mu, sigma, max_size)


class InitMature(model.Model):
    """
    Class to model the mass of a mature insect:
        - truncated normal between 0 and max

    Variables:
        _mu:    average mass of mature insect
        _sigma: standard deviation in mass of mature insect

        _max_size: maximum allowed mass

    Methods:
        __call__: call the model

    Constructors:
        setup: setup the mathematical model
    """

    keyword = keywords.init_mature

    def __init__(self, mu: hints.variable,
                       sigma: hints.variable,
                       max_size: hints.variable):
        self._mu    = mu
        self._sigma = sigma

        self._max_size = max_size

    @staticmethod
    def _lower(mu: float,
               sigma: float) -> float:
        """
        Get lower bound for egg mass distribution

        Args:
            mu:    mean
            sigma: standard deviation

        Returns:
            truncnorm lower bound
        """

        eps = np.finfo(float).eps

        return (eps - mu) / sigma

    def _upper(self, mu:        float,
                     sigma:     float,
                     phenotype: str) -> float:
        """
        Get upper bound for egg mass distribution

        Args:
            mu:    mean
            sigma: standard deviation

            phenotype: insect phenotype

        Returns:
            truncnorm upper bound
        """

        upper = self._max_size(phenotype)

        return (upper - mu) / sigma

    def __call__(self, phenotype: str) -> float:
        """
        Get the mass for the egg mass:
            this is normally distributed with mean=_mu, std_dev=sigma


        Args:
            phenotype: insect phenotype

        Returns:
            mass of egg mass
        """

        mu    = self._mu(phenotype)
        sigma = self._sigma(phenotype)

        lower = self._lower(mu, sigma)
        upper = self._upper(mu, sigma, phenotype)

        return stats.truncnorm.rvs(lower, upper, loc=mu, scale=sigma)

    @classmethod
    def setup(cls, *args, **kwargs) -> 'InitMature':
        """

        Args:
            *args:    arg[0]=mu, arg[1]=sigma, arg[2]=max_size
            **kwargs: other args

        Returns:
            setup class
        """

        mu       = cls.setup_variable(*args[0], **kwargs)
        sigma    = cls.setup_variable(*args[1], **kwargs)
        max_size = cls.setup_variable(*args[2], **kwargs)

        return cls(mu, sigma, max_size)


class EggNum(model.Model):
    """
    Class to model initial number of eggs in egg mass:
        draw from Poisson distribution

    Variables:
        _number: average number of eggs in egg mass

    Methods:
        __call__: call the model

    Constructors:
        setup: setup the mathematical model
    """

    keyword = keywords.egg_num

    def __init__(self, number: hints.variable):
        self._number = number

    def __call__(self, *args) -> int:
        """
        Args:
            *args: args[0] = adult phenotype (optional)
                   args[1] = adult mass      (optional),

        Returns:
            number of eggs
        """

        if len(args) > 0:
            lam = self._number(args[0])
        else:
            lam = self._number()

        return int(stats.poisson.rvs(lam))

    @classmethod
    def setup(cls, *args, **kwargs) -> 'EggNum':
        """
        Setup the class

        Args:
            *args:    args[0]=number tuple
            **kwargs: other args

        Returns:
            Fully setup class
        """

        number = cls.setup_variable(*args[0], **kwargs)

        return cls(number)


class EggMass(model.Model):
    """
    Class to model an egg_mass's total mass
        draw from a normal distribution

    Variables:
        _mu:      mean mass
        _sigma:   standard deviation in mass
        _maximum: maximum mass of single egg

    Methods:
        __call__: call the model

    Constructors:
        setup: setup the mathematical model
    """

    keyword = keywords.egg_mass

    def __init__(self, mu:      hints.variable,
                       sigma:   hints.variable,
                       maximum: hints.variable):
        self._mu      = mu
        self._sigma   = sigma
        self._maximum = maximum

    @staticmethod
    def _lower(mu:    float,
               sigma: float) -> float:
        """
        Get lower bound for egg mass distribution

        Args:
            mu:    mean
            sigma: standard deviation

        Returns:
            truncnorm lower bound
        """

        eps = np.finfo(float).eps

        return (eps - mu)/sigma

    def _upper(self, mu:        float,
                     sigma:     float,
                     num:       float,
                     *args) -> float:
        """
        Get upper bound for egg mass distribution

        Args:
            mu:    mean
            sigma: standard deviation

            num:   number of eggs
            *args: args[0] = phenotype (optional

        Returns:
            truncnorm upper bound
        """

        if len(args) > 0:
            upper = self._maximum(args[0])*num
        else:
            upper = self._maximum()*num

        return (upper - mu)/sigma

    def __call__(self, num: float, *args) -> float:
        """
        Get the mass for the egg mass:
            this is normally distributed with mean=_mu, std_dev=sigma


        Args:
            num:   number of eggs
            *args: args[0] = adult phenotype (optional)
                   args[1] = adult mass      (optional),

        Returns:
            mass of egg mass
        """

        if len(args) > 0:
            phenotype = args[0]
            mu    = self._mu(phenotype)
            sigma = self._sigma(phenotype)
            lower = self._lower(mu, sigma)
            upper = self._upper(mu, sigma, num, phenotype)
        else:
            mu    = self._mu()
            sigma = self._sigma()
            lower = self._lower(mu, sigma)
            upper = self._upper(mu, sigma, num)

        return float(stats.truncnorm.rvs(lower, upper, loc=mu, scale=sigma))

    @classmethod
    def setup(cls, *args, **kwargs) -> 'EggMass':
        """
        Setup the class

        Args:
            *args:    args[0]=mu tuple,
                      args[1]=sigma tuple,
                      args[2]=maximum tuple
            **kwargs: other args

        Returns:
            Fully setup class
        """

        mu      = cls.setup_variable(*args[0], **kwargs)
        sigma   = cls.setup_variable(*args[1], **kwargs)
        maximum = cls.setup_variable(*args[2], **kwargs)

        return cls(mu, sigma, maximum)


class InitLeaf(model.Model):
    """
    Class to contain an initial mass model for a leaf:
        draw from a normal distribution

    Variables:
        _mu:      mean mass
        _sigma:   standard deviation in mass
        _maximum: maximum mass

    Methods:
        __call__: call the model

    Constructors:
        setup: setup the mathematical model
    """

    keyword = keywords.init_leaf

    def __init__(self, mu:      hints.variable,
                       sigma:   hints.variable,
                       maximum: hints.variable):
        self._mu      = mu
        self._sigma   = sigma
        self._maximum = maximum

    @staticmethod
    def _lower(mu:    float,
               sigma: float) -> float:
        """
        Get lower bound for leaf mass distribution

        Args:
            mu:    mean
            sigma: standard deviation

        Returns:
            truncnorm lower bound
        """

        eps = np.finfo(float).eps

        return (eps - mu)/sigma

    def _upper(self, mu:        float,
                     sigma:     float,
                     *args) -> float:
        """
        Get upper bound for leaf mass distribution

        Args:
            mu:    mean
            sigma: standard deviation

            *args: args[0] = bt

        Returns:
            truncnorm upper bound
        """

        if len(args) > 0:
            upper = self._maximum(args[0])
        else:
            upper = self._maximum()

        return (upper - mu)/sigma

    def __call__(self, *args) -> float:
        """
        Get the mass for the egg mass:
            this is normally distributed with mean=_mu, std_dev=sigma


        Args:
            *args: args[0] = plant bt      (optional),

        Returns:
            mass of egg mass
        """

        if len(args) > 0:
            bt    = args[0]
            mu    = self._mu(bt)
            sigma = self._sigma(bt)
            lower = self._lower(mu, sigma)
            upper = self._upper(mu, sigma, bt)
        else:
            mu    = self._mu()
            sigma = self._sigma()
            lower = self._lower(mu, sigma)
            upper = self._upper(mu, sigma)

        return float(stats.truncnorm.rvs(lower, upper, loc=mu, scale=sigma))

    @classmethod
    def setup(cls, *args, **kwargs) -> 'InitLeaf':
        """
        Setup the class

        Args:
            *args:    args[0]=mu tuple,
                      args[1]=sigma tuple,
                      args[2]=maximum tuple
            **kwargs: other args

        Returns:
            Fully setup class
        """

        mu      = cls.setup_variable(*args[0], **kwargs)
        sigma   = cls.setup_variable(*args[1], **kwargs)
        maximum = cls.setup_variable(*args[2], **kwargs)

        return cls(mu, sigma, maximum)
