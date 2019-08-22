import unittest      as ut
import unittest.mock as mk

import dataclasses as dclass

import source.space.environment as environment


class TestEnvironment(ut.TestCase):
    """test the Environment class"""

    def setUp(self):
        """Setup the tests"""

        self.bt    = mk.MagicMock(spec=str)
        self.plant = mk.MagicMock(spec=str)

        self.Environment = environment.Environment(self.bt,
                                                   self.plant)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.Environment, environment.Environment)

        self.assertEqual(self.Environment.bt,    self.bt)
        self.assertEqual(self.Environment.plant, self.plant)

        self.assertTrue(dclass.is_dataclass(self.Environment))

    def test_setup(self):
        """test setup the class"""

        init_plant = mk.MagicMock(spec=callable)
        init_plant.return_value = self.plant

        self.Environment = environment.Environment.setup(self.bt, init_plant)
        self.assertIsInstance(self.Environment, environment.Environment)
        self.assertEqual(self.Environment.bt,    self.bt)
        self.assertEqual(self.Environment.plant, self.plant)

        self.assertEqual(init_plant.call_args_list,
                         [mk.call(self.bt)])
