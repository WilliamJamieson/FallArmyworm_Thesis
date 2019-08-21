import unittest      as ut
import unittest.mock as mk

import dataclasses   as dclass
import numpy         as np
import numpy.random  as rnd

import source.keyword as keyword

import source.simulation.models as models

import source.survival.models as model


class TestLarva(ut.TestCase):
    """test the Larva survival mathematical model class"""

    def setUp(self):
        """Setup the tests"""

        self.minimum = mk.MagicMock(spec=dict)
        self.maximum = mk.MagicMock(spec=dict)

        self.inflection = mk.MagicMock(spec=dict)
        self.steepness  = mk.MagicMock(spec=dict)

        self.Larva = model.Larva(self.minimum,
                                 self.maximum,
                                 self.inflection,
                                 self.steepness)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.Larva, models.Model)
        self.assertIsInstance(self.Larva, model.Larva)

        self.assertEqual(self.Larva.minimum,    self.minimum)
        self.assertEqual(self.Larva.maximum,    self.maximum)
        self.assertEqual(self.Larva.inflection, self.inflection)
        self.assertEqual(self.Larva.steepness,  self.steepness)

        self.assertEqual(self.Larva.model_key, keyword.larva_survival)

        self.assertTrue(dclass.is_dataclass(self.Larva))

    def test__logistic(self):
        """test evaluate the logistic probability"""

        mass     = mk.MagicMock(spec=float)
        genotype = mk.MagicMock(spec=str)
        bt       = mk.MagicMock(spec=str)

        lower = mk.MagicMock(spec=float)
        upper = mk.MagicMock(spec=float)
        m0    = mk.MagicMock(spec=float)
        k     = mk.MagicMock(spec=float)

        self.minimum.__getitem__.return_value = mk.MagicMock(spec=dict)
        self.maximum.__getitem__.return_value = mk.MagicMock(spec=dict)
        self.minimum.__getitem__.return_value.__getitem__.return_value = lower
        self.maximum.__getitem__.return_value.__getitem__.return_value = upper

        self.inflection.__getitem__.return_value = m0
        self.steepness. __getitem__.return_value = k

        with mk.patch.object(np, 'exp', autospec=True) as mkExp:
            self.assertEqual(self.Larva._logistic(mass, genotype, bt),
                             lower.__add__.return_value)
            self.assertEqual(lower.__add__.call_args_list,
                             [mk.call(upper.__sub__.return_value.
                                        __truediv__.return_value)])
            self.assertEqual(upper.__sub__.return_value.
                                __truediv__.call_args_list,
                             [mk.call(mkExp.return_value.__add__.return_value)])
            self.assertEqual(upper.__sub__.call_args_list,
                             [mk.call(lower)])
            self.assertEqual(mkExp.return_value.__add__.call_args_list,
                             [mk.call(1)])
            self.assertEqual(mkExp.call_args_list,
                             [mk.call(k.__neg__.return_value.
                                        __mul__.return_value)])
            self.assertEqual(k.__neg__.return_value.__mul__.call_args_list,
                             [mk.call(mass.__sub__.return_value)])
            self.assertEqual(k.__neg__.call_args_list,
                             [mk.call()])
            self.assertEqual(mass.__sub__.call_args_list,
                             [mk.call(m0)])

            self.assertEqual(self.minimum.__getitem__.return_value.
                                __getitem__.call_args_list,
                             [mk.call(genotype)])
            self.assertEqual(self.minimum.__getitem__.call_args_list,
                             [mk.call(bt)])
            self.assertEqual(self.maximum.__getitem__.return_value.
                             __getitem__.call_args_list,
                             [mk.call(genotype)])
            self.assertEqual(self.maximum.__getitem__.call_args_list,
                             [mk.call(bt)])
            self.assertEqual(self.inflection.__getitem__.call_args_list,
                             [mk.call(genotype)])
            self.assertEqual(self.steepness.__getitem__.call_args_list,
                             [mk.call(genotype)])

    def test___call__(self):
        """test call the model"""

        mass     = mk.MagicMock(spec=float)
        genotype = mk.MagicMock(spec=str)
        bt       = mk.MagicMock(spec=str)

        with mk.patch.object(model.Larva, '_logistic',
                             autospec=True) as mkLogistic:
            with mk.patch.object(rnd, 'random') as mkRND:
                mkRND.return_value.__le__.side_effect = [True, False]

                # Test is true
                self.assertTrue(self.Larva(mass, genotype, bt))
                self.assertEqual(mkRND.return_value.__le__.call_args_list,
                                 [mk.call(mkLogistic.return_value)])
                self.assertEqual(mkRND.call_args_list,
                                 [mk.call()])
                self.assertEqual(mkLogistic.call_args_list,
                                 [mk.call(self.Larva, mass, genotype, bt)])

                mkLogistic.reset_mock()
                mkRND.reset_mock()
                # Test is false
                self.assertFalse(self.Larva(mass, genotype, bt))
                self.assertEqual(mkRND.return_value.__le__.call_args_list,
                                 [mk.call(mkLogistic.return_value)])
                self.assertEqual(mkRND.call_args_list,
                                 [mk.call()])
                self.assertEqual(mkLogistic.call_args_list,
                                 [mk.call(self.Larva, mass, genotype, bt)])
                

class TestFixed(ut.TestCase):
    """test the Fixed survival mathematical model class"""

    def setUp(self):
        """Setup the tests"""

        self.prob = mk.MagicMock(spec=float)

        self.Fixed = model.Fixed(self.prob)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.Fixed, models.Model)
        self.assertIsInstance(self.Fixed, model.Fixed)

        self.assertEqual(self.Fixed.prob, self.prob)

        self.assertEqual(self.Fixed.model_key, None)

        self.assertTrue(dclass.is_dataclass(self.Fixed))

    def test___call__(self):
        """test call the model"""

        mass = mk.MagicMock(spec=float)
        args = (mk.MagicMock(), mk.MagicMock())

        with mk.patch.object(rnd, 'random') as mkRND:
            mkRND.return_value.__le__.side_effect = [True, False]

            # Test is true
            self.assertTrue(self.Fixed(mass, *args))
            self.assertEqual(mkRND.return_value.__le__.call_args_list,
                             [mk.call(self.prob)])
            self.assertEqual(mkRND.call_args_list,
                             [mk.call()])

            mkRND.reset_mock()
            # Test is false
            self.assertFalse(self.Fixed(mass, *args))
            self.assertEqual(mkRND.return_value.__le__.call_args_list,
                             [mk.call(self.prob)])
            self.assertEqual(mkRND.call_args_list,
                             [mk.call()])


class TestEgg(ut.TestCase):
    """test the Egg survival mathematical model class"""

    def setUp(self):
        """Setup the tests"""

        self.prob = mk.MagicMock(spec=float)

        self.Egg = model.Egg(self.prob)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.Egg, models.Model)
        self.assertIsInstance(self.Egg, model.Fixed)
        self.assertIsInstance(self.Egg, model.Egg)

        self.assertEqual(self.Egg.prob, self.prob)

        self.assertEqual(self.Egg.model_key, keyword.egg_survival)

        self.assertTrue(dclass.is_dataclass(self.Egg))


class TestPupa(ut.TestCase):
    """test the Pupa survival mathematical model class"""

    def setUp(self):
        """Setup the tests"""

        self.prob = mk.MagicMock(spec=float)

        self.Pupa = model.Pupa(self.prob)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.Pupa, models.Model)
        self.assertIsInstance(self.Pupa, model.Fixed)
        self.assertIsInstance(self.Pupa, model.Pupa)

        self.assertEqual(self.Pupa.prob, self.prob)

        self.assertEqual(self.Pupa.model_key, keyword.pupa_survival)

        self.assertTrue(dclass.is_dataclass(self.Pupa))


class TestAdult(ut.TestCase):
    """test the Adult survival mathematical model class"""

    def setUp(self):
        """Setup the tests"""

        self.prob = mk.MagicMock(spec=float)

        self.Adult = model.Adult(self.prob)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.Adult, models.Model)
        self.assertIsInstance(self.Adult, model.Fixed)
        self.assertIsInstance(self.Adult, model.Adult)

        self.assertEqual(self.Adult.prob, self.prob)

        self.assertEqual(self.Adult.model_key, keyword.adult_survival)

        self.assertTrue(dclass.is_dataclass(self.Adult))
