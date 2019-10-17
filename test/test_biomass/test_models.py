import unittest      as ut
import unittest.mock as mk

import dataclasses as dclass
import numpy       as np
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

        with mk.patch.object(stats.poisson, 'rvs', autospec=True) as mkRVS:
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

        self.mu    = mk.MagicMock(spec=dict)
        self.sigma = mk.MagicMock(spec=dict)

        self.InitMass = model.InitMass(self.mu,
                                       self.sigma)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.InitMass, models.Model)
        self.assertIsInstance(self.InitMass, model.InitMass)

        self.assertEqual(self.InitMass.mu,    self.mu)
        self.assertEqual(self.InitMass.sigma, self.sigma)

        self.assertEqual(self.InitMass.model_key, keyword.init_mass)

        self.assertTrue(dclass.is_dataclass(self.InitMass))

    def test___call__(self):
        """test call the model"""

        genotype = mk.MagicMock(spec=str)

        with mk.patch.object(stats.truncnorm, 'rvs',
                             autospec=True) as mkRVS:
            with mk.patch.object(model, 'float') as mkFloat:
                self.assertEqual(self.InitMass(genotype),
                                 mkFloat.return_value)
                self.assertEqual(mkFloat.call_args_list,
                                 [mk.call(mkRVS.return_value)])
                self.assertEqual(mkRVS.call_args_list,
                                 [mk.call(0,
                                          np.inf,
                                          loc=self.mu.
                                            __getitem__.return_value,
                                          scale=self.sigma.
                                            __getitem__.return_value)])
                self.assertEqual(self.mu.__getitem__.call_args_list,
                                 [mk.call(genotype)])
                self.assertEqual(self.sigma.__getitem__.call_args_list,
                                 [mk.call(genotype)])


class TestInitJuvenile(ut.TestCase):
    """test InitJuvenile mathematical models"""

    def setUp(self):
        """Setup the tests"""

        self.mu    = mk.MagicMock(spec=dict)
        self.sigma = mk.MagicMock(spec=dict)

        self.InitJuvenile = model.InitJuvenile(self.mu,
                                               self.sigma)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.InitJuvenile, models.Model)
        self.assertIsInstance(self.InitJuvenile, model.InitJuvenile)

        self.assertEqual(self.InitJuvenile.mu,    self.mu)
        self.assertEqual(self.InitJuvenile.sigma, self.sigma)

        self.assertEqual(self.InitJuvenile.model_key, keyword.init_juvenile)

        self.assertTrue(dclass.is_dataclass(self.InitJuvenile))

    def test___call__(self):
        """test call the model"""

        genotype = mk.MagicMock(spec=str)

        with mk.patch.object(stats.truncnorm, 'rvs',
                             autospec=True) as mkRVS:
            with mk.patch.object(model, 'float') as mkFloat:
                self.assertEqual(self.InitJuvenile(genotype),
                                 mkFloat.return_value)
                self.assertEqual(mkFloat.call_args_list,
                                 [mk.call(mkRVS.return_value)])
                self.assertEqual(mkRVS.call_args_list,
                                 [mk.call(0,
                                          np.inf,
                                          loc=self.mu.
                                          __getitem__.return_value,
                                          scale=self.sigma.
                                          __getitem__.return_value)])
                self.assertEqual(self.mu.__getitem__.call_args_list,
                                 [mk.call(genotype)])
                self.assertEqual(self.sigma.__getitem__.call_args_list,
                                 [mk.call(genotype)])


class TestInitMature(ut.TestCase):
    """test the InitMature mathematical model"""

    def setUp(self):
        """Setup the tests"""

        self.mu    = mk.MagicMock(spec=dict)
        self.sigma = mk.MagicMock(spec=dict)

        self.InitMature = model.InitMature(self.mu,
                                           self.sigma)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.InitMature, models.Model)
        self.assertIsInstance(self.InitMature, model.InitMature)

        self.assertEqual(self.InitMature.mu,    self.mu)
        self.assertEqual(self.InitMature.sigma, self.sigma)

        self.assertEqual(self.InitMature.model_key, keyword.init_mature)

        self.assertTrue(dclass.is_dataclass(self.InitMature))

    def test___call__(self):
        """test call the model"""

        genotype = mk.MagicMock(spec=str)

        with mk.patch.object(stats.truncnorm, 'rvs',
                             autospec=True) as mkRVS:
            with mk.patch.object(model, 'float') as mkFloat:
                self.assertEqual(self.InitMature(genotype),
                                 mkFloat.return_value)
                self.assertEqual(mkFloat.call_args_list,
                                 [mk.call(mkRVS.return_value)])
                self.assertEqual(mkRVS.call_args_list,
                                 [mk.call(0,
                                          np.inf,
                                          loc=self.mu.
                                          __getitem__.return_value,
                                          scale=self.sigma.
                                          __getitem__.return_value)])
                self.assertEqual(self.mu.__getitem__.call_args_list,
                                 [mk.call(genotype)])
                self.assertEqual(self.sigma.__getitem__.call_args_list,
                                 [mk.call(genotype)])


class TestInitPlant(ut.TestCase):
    """test the InitPlant mathematical model"""

    def setUp(self):
        """Setup the tests"""

        self.mu    = mk.MagicMock(spec=float)
        self.sigma = mk.MagicMock(spec=float)

        self.InitPlant = model.InitPlant(self.mu,
                                         self.sigma)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.InitPlant, models.Model)
        self.assertIsInstance(self.InitPlant, model.InitPlant)

        self.assertEqual(self.InitPlant.mu,    self.mu)
        self.assertEqual(self.InitPlant.sigma, self.sigma)

        self.assertEqual(self.InitPlant.model_key, keyword.init_plant)

        self.assertTrue(dclass.is_dataclass(self.InitPlant))

    def test___call__(self):
        """test call the model"""

        bt = mk.MagicMock(spec=str)

        with mk.patch.object(stats.truncnorm, 'rvs',
                             autospec=True) as mkRVS:
            with mk.patch.object(model, 'float') as mkFloat:
                self.assertEqual(self.InitPlant(bt),
                                 mkFloat.return_value)
                self.assertEqual(mkFloat.call_args_list,
                                 [mk.call(mkRVS.return_value)])
                self.assertEqual(mkRVS.call_args_list,
                                 [mk.call(0, np.inf,
                                          loc=self.mu,
                                          scale=self.sigma)])
