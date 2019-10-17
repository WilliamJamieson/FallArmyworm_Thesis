import unittest      as ut
import unittest.mock as mk

import dataclasses as dclass
import scipy.stats as stats

import source.keyword as keyword

import source.movement.models as model

import source.simulation.models as models


class TestLevy(ut.TestCase):
    """test the Levy flight mathematical model"""

    def setUp(self):
        """Setup the tests"""

        self.scale = mk.MagicMock(spec=float)
        self.shape = mk.MagicMock(spec=float)

        self.Levy = model.Levy(self.scale,
                               self.shape)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.Levy, models.Model)
        self.assertIsInstance(self.Levy, model.Levy)

        self.assertEqual(self.Levy.scale, self.scale)
        self.assertEqual(self.Levy.shape, self.shape)

        self.assertTrue(dclass.is_dataclass(self.Levy))

    def test___call__(self):
        """test call the model"""

        mass     = mk.MagicMock(spec=float)
        genotype = mk.MagicMock(spec=str)

        with mk.patch.object(stats.pareto, 'rvs', autospec=True) as mkRVS:
            with mk.patch.object(model, 'float') as mkFloat:
                self.assertEqual(self.Levy(mass, genotype),
                                 mkFloat.return_value)
                self.assertEqual(mkFloat.call_args_list,
                                 [mk.call(mkRVS.return_value)])
                self.assertEqual(mkRVS.call_args_list,
                                 [mk.call(self.shape, self.scale)])


class TestLarva(ut.TestCase):
    """test the Larva movement mathematical model"""

    def setUp(self):
        """Setup the tests"""

        self.scale = mk.MagicMock(spec=float)
        self.shape = mk.MagicMock(spec=float)

        self.Larva = model.Larva(self.scale,
                                 self.shape)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.Larva, models.Model)
        self.assertIsInstance(self.Larva, model.Levy)
        self.assertIsInstance(self.Larva, model.Larva)

        self.assertEqual(self.Larva.scale, self.scale)
        self.assertEqual(self.Larva.shape, self.shape)

        self.assertEqual(self.Larva.model_key, keyword.larva_movement)

        self.assertTrue(dclass.is_dataclass(self.Larva))


class TestAdult(ut.TestCase):
    """test the Adult movement mathematical model"""

    def setUp(self):
        """Setup the tests"""

        self.scale = mk.MagicMock(spec=float)
        self.shape = mk.MagicMock(spec=float)

        self.Adult = model.Adult(self.scale,
                                 self.shape)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.Adult, models.Model)
        self.assertIsInstance(self.Adult, model.Levy)
        self.assertIsInstance(self.Adult, model.Adult)

        self.assertEqual(self.Adult.scale, self.scale)
        self.assertEqual(self.Adult.shape, self.shape)

        self.assertEqual(self.Adult.model_key, keyword.adult_movement)

        self.assertTrue(dclass.is_dataclass(self.Adult))
