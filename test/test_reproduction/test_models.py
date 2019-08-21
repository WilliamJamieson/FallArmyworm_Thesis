import unittest      as ut
import unittest.mock as mk

import dataclasses  as dclass
import numpy        as np
import numpy.random as rnd
import scipy.stats  as stats

import source.keyword as keyword

import source.reproduction.models as model

import source.simulation.models as models


class TestInitSex(ut.TestCase):
    """test InitSex mathematical model class"""

    def setUp(self):
        """Setup the tests"""

        self.prob = mk.MagicMock(spec=float)

        self.InitSex = model.InitSex(self.prob)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.InitSex, models.Model)
        self.assertIsInstance(self.InitSex, model.InitSex)

        self.assertEqual(self.InitSex.prob, self.prob)

        self.assertEqual(self.InitSex.model_key, keyword.init_sex)

        self.assertTrue(dclass.is_dataclass(self.InitSex))

    def test___call__(self):
        """test call the model"""

        genotype = mk.MagicMock(spec=str)

        with mk.patch.object(rnd, 'random') as mkRND:
            mkRND.return_value.__le__.side_effect = [True, False]

            # Test is true
            self.assertTrue(self.InitSex(genotype))
            self.assertEqual(mkRND.return_value.__le__.call_args_list,
                             [mk.call(self.prob)])
            self.assertEqual(mkRND.call_args_list,
                             [mk.call()])

            mkRND.reset_mock()
            # Test is false
            self.assertFalse(self.InitSex(genotype))
            self.assertEqual(mkRND.return_value.__le__.call_args_list,
                             [mk.call(self.prob)])
            self.assertEqual(mkRND.call_args_list,
                             [mk.call()])


class TestMating(ut.TestCase):
    """test Mating mathematical model class"""

    def setUp(self):
        """Setup the tests"""

        self.factor = mk.MagicMock(spec=float)

        self.Mating = model.Mating(self.factor)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.Mating, models.Model)
        self.assertIsInstance(self.Mating, model.Mating)

        self.assertEqual(self.Mating.factor, self.factor)

        self.assertEqual(self.Mating.model_key, keyword.mating)

        self.assertTrue(dclass.is_dataclass(self.Mating))

    def test__prob(self):
        """test get the probability"""

        number = mk.MagicMock(spec=int)

        with mk.patch.object(np, 'exp', autospec=True) as mkExp:
            self.assertEqual(self.Mating._prob(number),
                             mkExp.return_value.__rsub__.return_value)
            self.assertEqual(mkExp.return_value.__rsub__.call_args_list,
                             [mk.call(1)])
            self.assertEqual(mkExp.call_args_list,
                             [mk.call(self.factor.__neg__.return_value.
                                        __mul__.return_value)])
            self.assertEqual(self.factor.__neg__.return_value.
                                __mul__.call_args_list,
                             [mk.call(number)])
            self.assertEqual(self.factor.__neg__.call_args_list,
                             [mk.call()])

    def test___call__(self):
        """test call the model"""

        number   = mk.MagicMock(spec=int)
        mass     = mk.MagicMock(spec=float)
        genotype = mk.MagicMock(spec=str)

        with mk.patch.object(model.Mating, '_prob', autospec=True) as mkProb:
            with mk.patch.object(rnd, 'random') as mkRND:
                mkRND.return_value.__le__.side_effect = [True, False]

                # Test True
                self.assertTrue(self.Mating(number, mass, genotype))
                self.assertEqual(mkRND.return_value.__le__.call_args_list,
                                 [mk.call(mkProb.return_value)])
                self.assertEqual(mkRND.call_args_list,
                                 [mk.call()])
                self.assertEqual(mkProb.call_args_list,
                                 [mk.call(self.Mating, number)])

                mkRND.reset_mock()
                mkProb.reset_mock()
                # Test False
                self.assertFalse(self.Mating(number, mass, genotype))
                self.assertEqual(mkRND.return_value.__le__.call_args_list,
                                 [mk.call(mkProb.return_value)])
                self.assertEqual(mkRND.call_args_list,
                                 [mk.call()])
                self.assertEqual(mkProb.call_args_list,
                                 [mk.call(self.Mating, number)])


class TestRadius(ut.TestCase):
    """test Radius mathematical model"""

    def setUp(self):
        """Setup the tests"""

        self.radius = mk.MagicMock(spec=int)

        self.Radius = model.Radius(self.radius)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.Radius, models.Model)
        self.assertIsInstance(self.Radius, model.Radius)

        self.assertEqual(self.Radius.radius, self.radius)

        self.assertEqual(self.Radius.model_key, keyword.mate_radius)

        self.assertTrue(dclass.is_dataclass(self.Radius))

    def test___call__(self):
        """test call the model"""

        mass     = mk.MagicMock(spec=float)
        genotype = mk.MagicMock(spec=str)

        self.assertEqual(self.Radius(mass, genotype), self.radius)


class TestFecundity(ut.TestCase):
    """test Fecundity mathematical model class"""

    def setUp(self):
        """Setup the tests"""

        self.maximum = mk.MagicMock(spec=float)
        self.decay   = mk.MagicMock(spec=float)

        self.Fecundity = model.Fecundity(self.maximum,
                                         self.decay)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.Fecundity, models.Model)
        self.assertIsInstance(self.Fecundity, model.Fecundity)

        self.assertEqual(self.Fecundity.maximum, self.maximum)
        self.assertEqual(self.Fecundity.decay,   self.decay)

        self.assertEqual(self.Fecundity.model_key, keyword.fecundity)

        self.assertTrue(dclass.is_dataclass(self.Fecundity))

    def test__lam(self):
        """test get mean of distribution"""

        time = mk.MagicMock(spec=int)

        with mk.patch.object(np, 'exp', autospec=True) as mkExp:
            self.assertEqual(self.Fecundity._lam(time),
                             self.maximum.__mul__.return_value.
                                __truediv__.return_value)
            self.assertEqual(self.maximum.__mul__.return_value.
                                __truediv__.call_args_list,
                             [mk.call(mkExp.return_value.__add__.return_value)])
            self.assertEqual(self.maximum.__mul__.call_args_list,
                             [mk.call(2)])
            self.assertEqual(mkExp.return_value.__add__.call_args_list,
                             [mk.call(1)])
            self.assertEqual(mkExp.call_args_list,
                             [mk.call(self.decay.__mul__.return_value)])
            self.assertEqual(self.decay.__mul__.call_args_list,
                             [mk.call(time)])

    def test___call__(self):
        """test call the model"""

        age      = mk.MagicMock(spec=int)
        mass     = mk.MagicMock(spec=float)
        genotype = mk.MagicMock(spec=str)

        with mk.patch.object(model.Fecundity, '_lam', autospec=True) as mkLam:
            with mk.patch.object(stats.poisson, 'rvs', autospec=True) as mkRVS:
                with mk.patch.object(model, 'int') as mkInt:
                    self.assertEqual(self.Fecundity(age, mass, genotype),
                                     mkInt.return_value)
                    self.assertEqual(mkInt.call_args_list,
                                     [mk.call(mkRVS.return_value)])
                    self.assertEqual(mkRVS.call_args_list,
                                     [mk.call(mkLam.return_value)])
                    self.assertEqual(mkLam.call_args_list,
                                     [mk.call(self.Fecundity, age)])


class TestDensity(ut.TestCase):
    """test Density mathematical model class"""

    def setUp(self):
        """Setup the tests"""

        self.eta   = mk.MagicMock(spec=float)
        self.gamma = mk.MagicMock(spec=float)

        self.Density = model.Density(self.eta,
                                     self.gamma)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.Density, models.Model)
        self.assertIsInstance(self.Density, model.Density)

        self.assertEqual(self.Density.eta,   self.eta)
        self.assertEqual(self.Density.gamma, self.gamma)

        self.assertEqual(self.Density.model_key, keyword.density)

        self.assertTrue(dclass.is_dataclass(self.Density))

    def test__prob(self):
        """test get the probability"""

        number = mk.MagicMock(spec=int)

        with mk.patch.object(np, 'exp', autospec=True) as mkExp:
            self.assertEqual(self.Density._prob(number),
                             mkExp.return_value)
            self.assertEqual(mkExp.call_args_list,
                             [mk.call(number.__truediv__.return_value.
                                        __pow__.return_value.
                                        __neg__.return_value)])
            self.assertEqual(number.__truediv__.return_value.
                                __pow__.return_value.__neg__.call_args_list,
                             [mk.call()])
            self.assertEqual(number.__truediv__.return_value.
                                __pow__.call_args_list,
                             [mk.call(self.gamma)])
            self.assertEqual(number.__truediv__.call_args_list,
                             [mk.call(self.eta)])

    def test___call__(self):
        """test call the model"""

        number   = mk.MagicMock(spec=int)
        mass     = mk.MagicMock(spec=float)
        genotype = mk.MagicMock(spec=str)

        with mk.patch.object(model.Density, '_prob', autospec=True) as mkProb:
            with mk.patch.object(rnd, 'random') as mkRND:
                mkRND.return_value.__le__.side_effect = [True, False]

                # Test True
                self.assertTrue(self.Density(number, mass, genotype))
                self.assertEqual(mkRND.return_value.__le__.call_args_list,
                                 [mk.call(mkProb.return_value)])
                self.assertEqual(mkRND.call_args_list,
                                 [mk.call()])
                self.assertEqual(mkProb.call_args_list,
                                 [mk.call(self.Density, number)])

                mkRND.reset_mock()
                mkProb.reset_mock()
                # Test False
                self.assertFalse(self.Density(number, mass, genotype))
                self.assertEqual(mkRND.return_value.__le__.call_args_list,
                                 [mk.call(mkProb.return_value)])
                self.assertEqual(mkRND.call_args_list,
                                 [mk.call()])
                self.assertEqual(mkProb.call_args_list,
                                 [mk.call(self.Density, number)])
