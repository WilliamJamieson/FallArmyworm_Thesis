import unittest      as ut
import unittest.mock as mk

import dataclasses as dclass

import source.keyword as keyword

import source.agents.larva as agent_larva

import source.forage.plant as forage


class LarvaTest(agent_larva.Larva):
    """Class to add dynamic values for tests"""

    mass     = mk.MagicMock(spec=float)
    genotype = mk.MagicMock(spec=str)


class TestPlant(ut.TestCase):
    """test the Plant forage class"""

    def setUp(self):
        """Setup the tests"""

        self.forage = mk.MagicMock(spec=callable)

        self.Plant = forage.Plant(self.forage)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.Plant, forage.Plant)

        self.assertEqual(self.Plant.forage, self.forage)

        self.assertEqual(self.Plant.behavior, keyword.forage_plant)

        self.assertTrue(dclass.is_dataclass(self.Plant))

    def test__use_forage(self):
        """test if we use the forage system"""

        self.assertTrue(self.Plant._use_forage)

        self.Plant.forage = None
        self.assertFalse(self.Plant._use_forage)

    def test__available(self):
        """test get the available amount of mass"""

        larva = mk.create_autospec(LarvaTest, spec_set=True)

        self.assertEqual(self.Plant._available(larva),
                         self.forage.return_value)
        self.assertEqual(self.forage.call_args_list,
                         [mk.call(larva.mass, larva.plant,
                                  larva.genotype, larva.bt)])
        
    def test__consume(self):
        """test run consume """

        larva = mk.create_autospec(LarvaTest, spec_set=True)

        with mk.patch.object(forage.Plant, '_available',
                             autospec=True) as mkAvailable:
            self.Plant._consume(larva)
            self.assertEqual(larva.add_plant.call_args_list,
                             [mk.call(mkAvailable.return_value)])
            self.assertEqual(mkAvailable.call_args_list,
                             [mk.call(self.Plant, larva)])

    def test_consume(self):
        """test consume the larva"""

        larva = mk.create_autospec(LarvaTest, spec_set=True)

        with mk.patch.object(forage.Plant, '_use_forage', autospec=True) as mkUse:
            with mk.patch.object(forage.Plant, '_consume',
                                 autospec=True) as mkConsume:
                mkUse.__get__ = mk.MagicMock(side_effect=[False, True])

                # No forage model is given
                self.Plant.consume(larva)
                self.assertEqual(mkConsume.call_args_list, [])

                # Forage model is given
                self.Plant.consume(larva)
                self.assertEqual(mkConsume.call_args_list,
                                 [mk.call(self.Plant, larva)])

    def test_setup(self):
        """test setup the class"""

        # Test if have the model
        kwargs = {keyword.plant_forage: self.forage}
        self.Plant = forage.Plant.setup(**kwargs)
        self.assertIsInstance(self.Plant, forage.Plant)
        self.assertEqual(self.Plant.forage, self.forage)
        self.assertEqual(self.Plant.behavior, keyword.forage_plant)

        # Test if have the model
        kwargs = {}
        self.Plant = forage.Plant.setup(**kwargs)
        self.assertIsInstance(self.Plant, forage.Plant)
        self.assertEqual(self.Plant.forage, None)
        self.assertEqual(self.Plant.behavior, keyword.forage_plant)
