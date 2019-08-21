import unittest      as ut
import unittest.mock as mk

import dataclasses as dclass

import source.keyword as keyword

import source.agents.larva as agent_larva

import source.biomass.gut as gut


class LarvaTest(agent_larva.Larva):
    """Class to add dynamic values for tests"""

    mass      = mk.MagicMock(spec=float)
    plant_gut = mk.MagicMock(spec=float)
    egg_gut   = mk.MagicMock(spec=float)
    larva_gut = mk.MagicMock(spec=float)


class TestGut(ut.TestCase):
    """test the Gut system class"""

    def setUp(self):
        """Setup the tests"""

        self.max_gut = mk.MagicMock(spec=callable)

        self.Gut = gut.Gut(self.max_gut)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.Gut, gut.Gut)

        self.assertEqual(self.Gut.max_gut, self.max_gut)

        self.assertTrue(dclass.is_dataclass(self.Gut))

    def test__volume(self):
        """test get the volume of the larva"""

        larva = mk.create_autospec(LarvaTest, spec_set=True)

        self.assertEqual(self.Gut._volume(larva),
                         larva.plant_gut.__add__.return_value.
                            __add__.return_value)
        self.assertEqual(larva.plant_gut.__add__.return_value.
                            __add__.call_args_list,
                         [mk.call(larva.larva_gut)])
        self.assertEqual(larva.plant_gut.__add__.call_args_list,
                         [mk.call(larva.egg_gut)])

    def test__remaining(self):
        """test get the remaining gut volume for the larva"""

        larva = mk.create_autospec(LarvaTest, spec_set=True)

        with mk.patch.object(gut.Gut, '_volume', autospec=True) as mkVolume:
            self.assertEqual(self.Gut._remaining(larva),
                             self.max_gut.return_value.__sub__.return_value)
            self.assertEqual(self.max_gut.return_value.__sub__.call_args_list,
                             [mk.call(mkVolume.return_value)])
            self.assertEqual(self.max_gut.call_args_list,
                             [mk.call(larva.mass)])
            self.assertEqual(mkVolume.call_args_list,
                             [mk.call(larva)])

    def test_amount(self):
        """test get the amount of mass to remove"""

        larva     = mk.create_autospec(LarvaTest, spec_set=True)
        available = mk.MagicMock(spec=float)

        available.__ge__.side_effect = [True, False]

        with mk.patch.object(gut.Gut, '_remaining',
                             autospec=True) as mkRemaining:
            # Test if available is too much
            self.assertEqual(self.Gut.amount(larva, available),
                             (mkRemaining.return_value, True))
            self.assertEqual(available.__ge__.call_args_list,
                             [mk.call(mkRemaining.return_value)])
            self.assertEqual(mkRemaining.call_args_list,
                             [mk.call(self.Gut, larva)])

            available.reset_mock()
            mkRemaining.reset_mock()
            # Test if available not enough
            self.assertEqual(self.Gut.amount(larva, available),
                             (available, False))
            self.assertEqual(available.__ge__.call_args_list,
                             [mk.call(mkRemaining.return_value)])
            self.assertEqual(mkRemaining.call_args_list,
                             [mk.call(self.Gut, larva)])

    def test_setup(self):
        """test setup the class"""

        kwargs = {keyword.max_gut: self.max_gut}

        self.Gut = gut.Gut.setup(**kwargs)
        self.assertIsInstance(self.Gut, gut.Gut)
        self.assertEqual(self.Gut.max_gut, self.max_gut)
