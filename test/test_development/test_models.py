import unittest      as ut
import unittest.mock as mk

import dataclasses  as dclass
import numpy.random as rnd
import scipy.stats  as stats

import source.keyword as keyword

import source.development.models as model

import source.simulation.models as models


class TestBaseTime(ut.TestCase):
    """test the BaseTime development mathematical model"""

    def setUp(self):
        """Setup the tests"""

        self.mu = mk.MagicMock(spec=float)
        self.sigma = mk.MagicMock(spec=float)
        self.minimum = mk.MagicMock(spec=float)

        self.BaseTime = model.BaseTime(self.mu,
                                       self.sigma,
                                       self.minimum)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.BaseTime, models.Model)
        self.assertIsInstance(self.BaseTime, model.BaseTime)

        self.assertEqual(self.BaseTime.mu,      self.mu)
        self.assertEqual(self.BaseTime.sigma,   self.sigma)
        self.assertEqual(self.BaseTime.minimum, self.minimum)

        self.assertEqual(self.BaseTime.model_key, None)

        self.assertTrue(dclass.is_dataclass(self.BaseTime))

    def test__prob(self):
        """test get the probability"""

        age = mk.MagicMock(spec=int)

        self.minimum.__le__.side_effect = [False, True]

        with mk.patch.object(stats.norm, 'cdf', autospec=True) as mkCDF:
            # Test not less
            self.assertEqual(self.BaseTime._prob(age), 0)
            self.assertEqual(mkCDF.call_args_list, [])
            self.assertEqual(self.minimum.__le__.call_args_list,
                             [mk.call(age)])

            self.minimum.reset_mock()
            # Test less
            self.assertEqual(self.BaseTime._prob(age),
                             mkCDF.return_value)
            self.assertEqual(mkCDF.call_args_list,
                             [mk.call(age,
                                      loc=self.mu, scale=self.sigma)])
            self.assertEqual(self.minimum.__le__.call_args_list,
                             [mk.call(age)])

    def test___call__(self):
        """test call the model"""

        mass = mk.MagicMock(spec=float)
        age = mk.MagicMock(spec=int)
        genotype = mk.MagicMock(spec=str)

        with mk.patch.object(model.BaseTime, '_prob', autospec=True) as mkProb:
            with mk.patch.object(rnd, 'random') as mkRND:
                mkRND.return_value.__le__.side_effect = [True, False]

                # Return True
                self.assertTrue(self.BaseTime(mass, age, genotype))
                self.assertEqual(mkRND.return_value.__le__.call_args_list,
                                 [mk.call(mkProb.return_value)])
                self.assertEqual(mkRND.call_args_list,
                                 [mk.call()])
                self.assertEqual(mkProb.call_args_list,
                                 [mk.call(self.BaseTime, age)])

                mkRND.reset_mock()
                mkProb.reset_mock()
                # Return False
                self.assertFalse(self.BaseTime(mass, age, genotype))
                self.assertEqual(mkRND.return_value.__le__.call_args_list,
                                 [mk.call(mkProb.return_value)])
                self.assertEqual(mkRND.call_args_list,
                                 [mk.call()])
                self.assertEqual(mkProb.call_args_list,
                                 [mk.call(self.BaseTime, age)])


class TestEgg(ut.TestCase):
    """test the Egg development mathematical model"""

    def setUp(self):
        """Setup the tests"""

        self.mu      = mk.MagicMock(spec=float)
        self.sigma   = mk.MagicMock(spec=float)
        self.minimum = mk.MagicMock(spec=float)

        self.Egg = model.Egg(self.mu,
                             self.sigma,
                             self.minimum)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.Egg, models.Model)
        self.assertIsInstance(self.Egg, model.BaseTime)
        self.assertIsInstance(self.Egg, model.Egg)

        self.assertEqual(self.Egg.mu,      self.mu)
        self.assertEqual(self.Egg.sigma,   self.sigma)
        self.assertEqual(self.Egg.minimum, self.minimum)
        
        self.assertEqual(self.Egg.model_key, keyword.egg_development)
        
        self.assertTrue(dclass.is_dataclass(self.Egg))


class TestPupa(ut.TestCase):
    """test the Pupa development mathematical model"""

    def setUp(self):
        """Setup the tests"""

        self.mu      = mk.MagicMock(spec=float)
        self.sigma   = mk.MagicMock(spec=float)
        self.minimum = mk.MagicMock(spec=float)

        self.Pupa = model.Pupa(self.mu,
                               self.sigma,
                               self.minimum)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.Pupa, models.Model)
        self.assertIsInstance(self.Pupa, model.BaseTime)
        self.assertIsInstance(self.Pupa, model.Pupa)

        self.assertEqual(self.Pupa.mu,      self.mu)
        self.assertEqual(self.Pupa.sigma,   self.sigma)
        self.assertEqual(self.Pupa.minimum, self.minimum)

        self.assertEqual(self.Pupa.model_key, keyword.pupa_development)

        self.assertTrue(dclass.is_dataclass(self.Pupa))


class TestLarva(ut.TestCase):
    """test the Larva development mathematical model"""

    def setUp(self):
        """Setup the tests"""

        self.mu      = mk.MagicMock(spec=dict)
        self.sigma   = mk.MagicMock(spec=dict)
        self.minimum = mk.MagicMock(spec=dict)

        self.Larva = model.Larva(self.mu,
                                 self.sigma,
                                 self.minimum)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.Larva, models.Model)
        self.assertIsInstance(self.Larva, model.Larva)

        self.assertEqual(self.Larva.mu,      self.mu)
        self.assertEqual(self.Larva.sigma,   self.sigma)
        self.assertEqual(self.Larva.minimum, self.minimum)

        self.assertEqual(self.Larva.model_key, keyword.larva_development)

        self.assertTrue(dclass.is_dataclass(self.Larva))

    def test__prob(self):
        """test get the probability"""

        mass     = mk.MagicMock(spec=float)
        age      = mk.MagicMock(spec=int)
        genotype = mk.MagicMock(spec=str)

        self.minimum.__getitem__.return_value.__le__.side_effect = [False, True]

        with mk.patch.object(stats.norm, 'cdf', autospec=True) as mkCDF:
            # Test not less
            self.assertEqual(self.Larva._prob(mass, age, genotype), 0)
            self.assertEqual(mkCDF.call_args_list, [])
            self.assertEqual(self.minimum.__getitem__.return_value.
                                __le__.call_args_list,
                             [mk.call(age)])
            self.assertEqual(self.minimum.__getitem__.call_args_list,
                             [mk.call(genotype)])
            self.assertEqual(self.mu.__getitem__.call_args_list, [])
            self.assertEqual(self.sigma.__getitem__.call_args_list, [])

            self.minimum.reset_mock()
            # Test less
            self.assertEqual(self.Larva._prob(mass, age, genotype),
                             mkCDF.return_value)
            self.assertEqual(mkCDF.call_args_list,
                             [mk.call(mass,
                                      loc=self.mu.
                                        __getitem__.return_value,
                                      scale=self.sigma.
                                        __getitem__.return_value)])
            self.assertEqual(self.minimum.__getitem__.return_value.
                             __le__.call_args_list,
                             [mk.call(age)])
            self.assertEqual(self.minimum.__getitem__.call_args_list,
                             [mk.call(genotype)])
            self.assertEqual(self.mu.__getitem__.call_args_list,
                             [mk.call(genotype)])
            self.assertEqual(self.sigma.__getitem__.call_args_list,
                             [mk.call(genotype)])

    def test___call__(self):
        """test call the model"""

        mass     = mk.MagicMock(spec=float)
        age      = mk.MagicMock(spec=int)
        genotype = mk.MagicMock(spec=str)

        with mk.patch.object(model.Larva, '_prob', autospec=True) as mkProb:
            with mk.patch.object(rnd, 'random') as mkRND:
                mkRND.return_value.__le__.side_effect = [True, False]

                # Return True
                self.assertTrue(self.Larva(mass, age, genotype))
                self.assertEqual(mkRND.return_value.__le__.call_args_list,
                                 [mk.call(mkProb.return_value)])
                self.assertEqual(mkRND.call_args_list,
                                 [mk.call()])
                self.assertEqual(mkProb.call_args_list,
                                 [mk.call(self.Larva, mass, age, genotype)])

                mkRND.reset_mock()
                mkProb.reset_mock()
                # Return False
                self.assertFalse(self.Larva(mass, age, genotype))
                self.assertEqual(mkRND.return_value.__le__.call_args_list,
                                 [mk.call(mkProb.return_value)])
                self.assertEqual(mkRND.call_args_list,
                                 [mk.call()])
                self.assertEqual(mkProb.call_args_list,
                                 [mk.call(self.Larva, mass, age, genotype)])
