import unittest      as ut
import unittest.mock as mk

import dataclasses as dclass
import scipy.stats as stats

import source.keyword as keyword

import source.biomass.models as model

import source.simulation.models as models


class TestMaxGut(ut.TestCase):
    """test the MaxGut mathematical model"""

    def setUp(self):
        """Setup the tests"""

        self.MaxGut = model.MaxGut()

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.MaxGut, models.Model)
        self.assertIsInstance(self.MaxGut, model.MaxGut)

        self.assertEqual(self.MaxGut.model_key, keyword.max_gut)

        self.assertTrue(dclass.is_dataclass(self.MaxGut))

    def test___call__(self):
        """test call to get maximum gut volume"""

        mass = mk.MagicMock(spec=float)

        self.assertEqual(self.MaxGut(mass),
                         mass.__pow__.return_value)
        self.assertEqual(mass.__pow__.call_args_list,
                         [mk.call(0.75)])


class TestGrowth(ut.TestCase):
    """test the Growth mathematical model"""

    def setUp(self):
        """Setup the tests"""

        self.alpha = mk.MagicMock(spec=dict)
        self.beta  = mk.MagicMock(spec=dict)

        self.Growth = model.Growth(self.alpha,
                                   self.beta)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.Growth, models.Model)
        self.assertIsInstance(self.Growth, model.Growth)

        self.assertEqual(self.Growth.alpha, self.alpha)
        self.assertEqual(self.Growth.beta,  self.beta)

        self.assertEqual(self.Growth.model_key, keyword.growth)

        self.assertTrue(dclass.is_dataclass(self.Growth))

    def test___call__(self):
        """test call the mathematical model"""

        mass     = mk.MagicMock(spec=float)
        energy   = mk.MagicMock(spec=float)
        genotype = mk.MagicMock(spec=str)

        self.assertEqual(self.Growth(mass, energy, genotype),
                         self.alpha.__getitem__.return_value.
                            __mul__.return_value.__sub__.return_value)
        self.assertEqual(self.alpha.__getitem__.return_value.
                             __mul__.return_value.__sub__.call_args_list,
                         [mk.call(self.beta.__getitem__.return_value.
                                        __mul__.return_value)])
        self.assertEqual(self.alpha.__getitem__.return_value.
                            __mul__.call_args_list,
                         [mk.call(energy)])
        self.assertEqual(self.alpha.__getitem__.call_args_list,
                         [mk.call(genotype)])
        self.assertEqual(self.beta.__getitem__.return_value.
                            __mul__.call_args_list,
                         [mk.call(mass)])
        self.assertEqual(self.beta.__getitem__.call_args_list,
                         [mk.call(genotype)])


class TestInitNum(ut.TestCase):
    """test the InitNum mathematical model"""

    def setUp(self):
        """Setup the tests"""

        self.lam = mk.MagicMock(spec=float)

        self.InitNum = model.InitNum(self.lam)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.InitNum, models.Model)
        self.assertIsInstance(self.InitNum, model.InitNum)

        self.assertEqual(self.InitNum.lam, self.lam)

        self.assertEqual(self.InitNum.model_key, keyword.init_num)

        self.assertTrue(dclass.is_dataclass(self.InitNum))

    def test___call__(self):
        """test call the model"""

        genotype = mk.MagicMock(spec=str)

        with mk.patch.object(stats.poisson, 'rvs') as mkRVS:
            with mk.patch.object(model, 'int') as mkInt:
                self.assertEqual(self.InitNum(genotype),
                                 mkInt.return_value)
                self.assertEqual(mkInt.call_args_list,
                                 [mk.call(mkRVS.return_value)])
                self.assertEqual(mkRVS.call_args_list,
                                 [mk.call(self.lam)])


class TestInitMass(ut.TestCase):
    """test the InitMass mathematical model"""

    def setUp(self):
        """Setup the tests"""

        self.mu      = mk.MagicMock(spec=dict)
        self.sigma   = mk.MagicMock(spec=float)
        self.maximum = mk.MagicMock(spec=dict)

        self.InitMass = model.InitMass(self.mu,
                                       self.sigma,
                                       self.maximum)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.InitMass, models.Model)
        self.assertIsInstance(self.InitMass, model.InitMass)

        self.assertEqual(self.InitMass.mu,      self.mu)
        self.assertEqual(self.InitMass.sigma,   self.sigma)
        self.assertEqual(self.InitMass.maximum, self.maximum)

        self.assertEqual(self.InitMass.model_key, keyword.init_mass)

        self.assertTrue(dclass.is_dataclass(self.InitMass))

    def test__lower(self):
        """test get the lower bound on distribution"""

        mu = mk.MagicMock(spec=float)

        self.assertEqual(self.InitMass._lower(mu),
                         mu.__neg__.return_value.__truediv__.return_value)
        self.assertEqual(mu.__neg__.return_value.__truediv__.call_args_list,
                         [mk.call(self.sigma)])
        self.assertEqual(mu.__neg__.call_args_list,
                         [mk.call()])

    def test__upper(self):
        """test get the upper bound on distribution"""

        mu       = mk.MagicMock(spec=float)
        number   = mk.MagicMock(spec=int)
        genotype = mk.MagicMock(spec=str)

        self.assertEqual(self.InitMass._upper(mu, number, genotype),
                         number.__mul__.return_value.__sub__.return_value.
                            __truediv__.return_value)
        self.assertEqual(number.__mul__.return_value.__sub__.return_value.
                            __truediv__.call_args_list,
                         [mk.call(self.sigma)])
        self.assertEqual(number.__mul__.return_value.__sub__.call_args_list,
                         [mk.call(mu)])
        self.assertEqual(number.__mul__.call_args_list,
                         [mk.call(self.maximum.__getitem__.return_value)])
        self.assertEqual(self.maximum.__getitem__.call_args_list,
                         [mk.call(genotype)])

    def test___call__(self):
        """test call the model"""

        number   = mk.MagicMock(spec=int)
        genotype = mk.MagicMock(spec=str)

        with mk.patch.object(model.InitMass, '_lower',
                             autospec=True) as mkLower:
            with mk.patch.object(model.InitMass, '_upper',
                                 autospec=True) as mkUpper:
                with mk.patch.object(stats.truncnorm, 'rvs') as mkRVS:
                    with mk.patch.object(model, 'float') as mkFloat:
                        self.assertEqual(self.InitMass(number, genotype),
                                         mkFloat.return_value)
                        self.assertEqual(mkFloat.call_args_list,
                                         [mk.call(mkRVS.return_value)])
                        self.assertEqual(mkRVS.call_args_list,
                                         [mk.call(mkLower.return_value,
                                                  mkUpper.return_value,
                                                  loc=self.mu.
                                                    __getitem__.return_value,
                                                  scale=self.sigma)])
                        self.assertEqual(mkLower.call_args_list,
                                         [mk.call(self.InitMass,
                                                  self.mu.
                                                    __getitem__.return_value)])
                        self.assertEqual(mkUpper.call_args_list,
                                         [mk.call(self.InitMass,
                                                  self.mu.
                                                    __getitem__.return_value,
                                                  number, genotype)])
                        self.assertEqual(self.mu.__getitem__.call_args_list,
                                         [mk.call(genotype)])
                        

class TestInitJuvenile(ut.TestCase):
    """test InitJuvenile mathematical models"""

    def setUp(self):
        """Setup the tests"""

        self.lam     = mk.MagicMock(spec=float)
        self.mu      = mk.MagicMock(spec=dict)
        self.sigma   = mk.MagicMock(spec=float)
        self.maximum = mk.MagicMock(spec=dict)

        self.InitJuvenile = model.InitJuvenile(self.lam,
                                               self.mu,
                                               self.sigma,
                                               self.maximum)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.InitJuvenile, models.Model)
        self.assertIsInstance(self.InitJuvenile, model.InitJuvenile)

        self.assertEqual(self.InitJuvenile.lam,     self.lam)
        self.assertEqual(self.InitJuvenile.mu,      self.mu)
        self.assertEqual(self.InitJuvenile.sigma,   self.sigma)
        self.assertEqual(self.InitJuvenile.maximum, self.maximum)

        self.assertEqual(self.InitJuvenile.model_key, keyword.init_juvenile)

        self.assertTrue(dclass.is_dataclass(self.InitJuvenile))

    def test__number(self):
        """test get the number of eggs"""

        with mk.patch.object(stats.poisson, 'rvs') as mkRVS:
            self.assertEqual(self.InitJuvenile._number(),
                             mkRVS.return_value)
            self.assertEqual(mkRVS.call_args_list,
                             [mk.call(self.lam)])

    def test__lower(self):
        """test get the lower bound on distribution"""

        mu = mk.MagicMock(spec=float)

        self.assertEqual(self.InitJuvenile._lower(mu),
                         mu.__neg__.return_value.__truediv__.return_value)
        self.assertEqual(mu.__neg__.return_value.__truediv__.call_args_list,
                         [mk.call(self.sigma)])
        self.assertEqual(mu.__neg__.call_args_list,
                         [mk.call()])

    def test__upper(self):
        """test get the upper bound on distribution"""

        mu       = mk.MagicMock(spec=float)
        number   = mk.MagicMock(spec=int)
        genotype = mk.MagicMock(spec=str)

        self.assertEqual(self.InitJuvenile._upper(mu, number, genotype),
                         number.__mul__.return_value.__sub__.return_value.
                         __truediv__.return_value)
        self.assertEqual(number.__mul__.return_value.__sub__.return_value.
                         __truediv__.call_args_list,
                         [mk.call(self.sigma)])
        self.assertEqual(number.__mul__.return_value.__sub__.call_args_list,
                         [mk.call(mu)])
        self.assertEqual(number.__mul__.call_args_list,
                         [mk.call(self.maximum.__getitem__.return_value)])
        self.assertEqual(self.maximum.__getitem__.call_args_list,
                         [mk.call(genotype)])

    def test__total_mass(self):
        """test get total mass of egg_mass"""

        number   = mk.MagicMock(spec=int)
        genotype = mk.MagicMock(spec=str)

        with mk.patch.object(model.InitJuvenile, '_lower',
                             autospec=True) as mkLower:
            with mk.patch.object(model.InitJuvenile, '_upper',
                                 autospec=True) as mkUpper:
                with mk.patch.object(stats.truncnorm, 'rvs') as mkRVS:
                    self.assertEqual(self.InitJuvenile.
                                        _total_mass(number, genotype),
                                     mkRVS.return_value)
                    self.assertEqual(mkRVS.call_args_list,
                                     [mk.call(mkLower.return_value,
                                              mkUpper.return_value,
                                              loc=self.mu.
                                              __getitem__.return_value,
                                              scale=self.sigma)])
                    self.assertEqual(mkLower.call_args_list,
                                     [mk.call(self.InitJuvenile,
                                              self.mu.
                                              __getitem__.return_value)])
                    self.assertEqual(mkUpper.call_args_list,
                                     [mk.call(self.InitJuvenile,
                                              self.mu.
                                              __getitem__.return_value,
                                              number, genotype)])
                    self.assertEqual(self.mu.__getitem__.call_args_list,
                                     [mk.call(genotype)])

    def test___call__(self):
        """test call the model"""

        genotype = mk.MagicMock(spec=str)

        with mk.patch.object(model.InitJuvenile, '_number',
                             autospec=True) as mkNumber:
            with mk.patch.object(model.InitJuvenile, '_total_mass',
                                 autospec=True) as mkMass:
                with mk.patch.object(model, 'float') as mkFloat:
                    self.assertEqual(self.InitJuvenile(genotype),
                                     mkFloat.return_value)
                    self.assertEqual(mkFloat.call_args_list,
                                     [mk.call(mkMass.return_value.
                                                __truediv__.return_value)])
                    self.assertEqual(mkMass.return_value.
                                        __truediv__.call_args_list,
                                     [mk.call(mkNumber.return_value)])
                    self.assertEqual(mkMass.call_args_list,
                                     [mk.call(self.InitJuvenile,
                                              mkNumber.return_value,
                                              genotype)])
                    self.assertEqual(mkNumber.call_args_list,
                                     [mk.call(self.InitJuvenile)])


class TestInitMature(ut.TestCase):
    """test the InitMature mathematical model"""

    def setUp(self):
        """Setup the tests"""

        self.mu      = mk.MagicMock(spec=dict)
        self.sigma   = mk.MagicMock(spec=float)
        self.maximum = mk.MagicMock(spec=dict)

        self.InitMature = model.InitMature(self.mu,
                                           self.sigma,
                                           self.maximum)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.InitMature, models.Model)
        self.assertIsInstance(self.InitMature, model.InitMature)

        self.assertEqual(self.InitMature.mu, self.mu)
        self.assertEqual(self.InitMature.sigma, self.sigma)
        self.assertEqual(self.InitMature.maximum, self.maximum)

        self.assertEqual(self.InitMature.model_key, keyword.init_mature)

        self.assertTrue(dclass.is_dataclass(self.InitMature))

    def test__lower(self):
        """test get the lower bound on distribution"""

        mu = mk.MagicMock(spec=float)

        self.assertEqual(self.InitMature._lower(mu),
                         mu.__neg__.return_value.__truediv__.return_value)
        self.assertEqual(mu.__neg__.return_value.__truediv__.call_args_list,
                         [mk.call(self.sigma)])
        self.assertEqual(mu.__neg__.call_args_list,
                         [mk.call()])

    def test__upper(self):
        """test get the upper bound on distribution"""

        mu       = mk.MagicMock(spec=float)
        genotype = mk.MagicMock(spec=str)

        self.assertEqual(self.InitMature._upper(mu, genotype),
                         self.maximum.__getitem__.return_value.
                            __sub__.return_value.__truediv__.return_value)
        self.assertEqual(self.maximum.__getitem__.return_value.
                            __sub__.return_value.__truediv__.call_args_list,
                         [mk.call(self.sigma)])
        self.assertEqual(self.maximum.__getitem__.return_value.
                            __sub__.call_args_list,
                         [mk.call(mu)])
        self.assertEqual(self.maximum.__getitem__.call_args_list,
                         [mk.call(genotype)])

    def test___call__(self):
        """test call the model"""

        genotype = mk.MagicMock(spec=str)

        with mk.patch.object(model.InitMature, '_lower',
                             autospec=True) as mkLower:
            with mk.patch.object(model.InitMature, '_upper',
                                 autospec=True) as mkUpper:
                with mk.patch.object(stats.truncnorm, 'rvs') as mkRVS:
                    with mk.patch.object(model, 'float') as mkFloat:
                        self.assertEqual(self.InitMature(genotype),
                                         mkFloat.return_value)
                        self.assertEqual(mkFloat.call_args_list,
                                         [mk.call(mkRVS.return_value)])
                        self.assertEqual(mkRVS.call_args_list,
                                         [mk.call(mkLower.return_value,
                                                  mkUpper.return_value,
                                                  loc=self.mu.
                                                    __getitem__.return_value,
                                                  scale=self.sigma)])
                        self.assertEqual(mkLower.call_args_list,
                                         [mk.call(self.InitMature,
                                                  self.mu.
                                                    __getitem__.return_value)])
                        self.assertEqual(mkUpper.call_args_list,
                                         [mk.call(self.InitMature,
                                                  self.mu.
                                                    __getitem__.return_value,
                                                  genotype)])
                        self.assertEqual(self.mu.__getitem__.call_args_list,
                                         [mk.call(genotype)])



class TestInitPlant(ut.TestCase):
    """test the InitPlant mathematical model"""

    def setUp(self):
        """Setup the tests"""

        self.mu      = mk.MagicMock(spec=float)
        self.sigma   = mk.MagicMock(spec=float)
        self.maximum = mk.MagicMock(spec=float)

        self.InitPlant = model.InitPlant(self.mu,
                                         self.sigma,
                                         self.maximum)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.InitPlant, models.Model)
        self.assertIsInstance(self.InitPlant, model.InitPlant)

        self.assertEqual(self.InitPlant.mu, self.mu)
        self.assertEqual(self.InitPlant.sigma, self.sigma)
        self.assertEqual(self.InitPlant.maximum, self.maximum)

        self.assertEqual(self.InitPlant.model_key, keyword.init_plant)

        self.assertTrue(dclass.is_dataclass(self.InitPlant))

    def test__lower(self):
        """test get the lower bound on distribution"""

        self.assertEqual(self.InitPlant._lower(),
                         self.mu.__neg__.return_value.
                            __truediv__.return_value)
        self.assertEqual(self.mu.__neg__.return_value.
                            __truediv__.call_args_list,
                         [mk.call(self.sigma)])
        self.assertEqual(self.mu.__neg__.call_args_list,
                         [mk.call()])

    def test__upper(self):
        """test get the upper bound on distribution"""

        self.assertEqual(self.InitPlant._upper(),
                         self.maximum.__sub__.return_value.
                            __truediv__.return_value)
        self.assertEqual(self.maximum.__sub__.return_value.
                            __truediv__.call_args_list,
                         [mk.call(self.sigma)])
        self.assertEqual(self.maximum.__sub__.call_args_list,
                         [mk.call(self.mu)])

    def test___call__(self):
        """test call the model"""

        bt = mk.MagicMock(spec=str)

        with mk.patch.object(model.InitPlant, '_lower',
                             autospec=True) as mkLower:
            with mk.patch.object(model.InitPlant, '_upper',
                                 autospec=True) as mkUpper:
                with mk.patch.object(stats.truncnorm, 'rvs') as mkRVS:
                    with mk.patch.object(model, 'float') as mkFloat:
                        self.assertEqual(self.InitPlant(bt),
                                         mkFloat.return_value)
                        self.assertEqual(mkFloat.call_args_list,
                                         [mk.call(mkRVS.return_value)])
                        self.assertEqual(mkRVS.call_args_list,
                                         [mk.call(mkLower.return_value,
                                                  mkUpper.return_value,
                                                  loc=self.mu,
                                                  scale=self.sigma)])
                        self.assertEqual(mkLower.call_args_list,
                                         [mk.call(self.InitPlant)])
                        self.assertEqual(mkUpper.call_args_list,
                                         [mk.call(self.InitPlant)])
