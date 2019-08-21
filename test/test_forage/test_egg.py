import unittest      as ut
import unittest.mock as mk

import dataclasses as dclass

import source.keyword as keyword

import source.agents.egg_mass as agent_egg_mass
import source.agents.larva    as agent_larva

import source.forage.egg as forage


class LarvaTest(agent_larva.Larva):
    """Class to add dynamic values for tests"""

    mass     = mk.MagicMock(spec=float)
    genotype = mk.MagicMock(spec=str)


class EggMassTest(agent_egg_mass.EggMass):
    """Class to add dynamic values for tests"""

    agent_key = keyword.egg_mass


class TestEgg(ut.TestCase):
    """test the Egg forage class"""

    def setUp(self):
        """Setup the tests"""

        self.forage = mk.MagicMock(spec=callable)

        self.Egg = forage.Egg(self.forage)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.Egg, forage.Egg)

        self.assertEqual(self.Egg.forage, self.forage)

        self.assertEqual(self.Egg.behavior, keyword.forage_egg)

        self.assertTrue(dclass.is_dataclass(self.Egg))

    def test__use_forage(self):
        """test if we use the forage system"""

        self.assertTrue(self.Egg._use_forage)

        self.Egg.forage = None
        self.assertFalse(self.Egg._use_forage)

    def test__available(self):
        """test get the available amount of mass"""

        larva    = mk.create_autospec(LarvaTest, spec_set=True)
        egg_mass = mk.create_autospec(EggMassTest, spec_set=True)

        self.assertEqual(self.Egg._available(larva, egg_mass),
                         self.forage.return_value)
        self.assertEqual(self.forage.call_args_list,
                         [mk.call(egg_mass.mass, larva.mass, larva.genotype)])
        
    def test__consume(self):
        """test consume the egg"""

        larva    = mk.create_autospec(LarvaTest, spec_set=True)
        egg_mass = mk.create_autospec(EggMassTest, spec_set=True)

        with mk.patch.object(forage.Egg, '_available',
                             autospec=True) as mkAvailable:
            self.Egg._consume(larva, egg_mass)
            self.assertEqual(egg_mass.feed.call_args_list,
                             [mk.call(larva.add_egg.return_value)])
            self.assertEqual(larva.add_egg.call_args_list,
                             [mk.call(mkAvailable.return_value)])
            self.assertEqual(mkAvailable.call_args_list,
                             [mk.call(self.Egg, larva, egg_mass)])

    def test_consume(self):
        """test consume the larva"""

        larva    = mk.create_autospec(LarvaTest, spec_set=True)
        egg_mass = mk.create_autospec(EggMassTest, spec_set=True)

        with mk.patch.object(forage.Egg, '_use_forage', autospec=True) as mkUse:
            with mk.patch.object(forage.Egg, '_consume',
                                 autospec=True) as mkConsume:
                mkUse.__get__ = mk.MagicMock(side_effect=[False, True])

                # No forage model is given
                self.Egg.consume(larva, egg_mass)
                self.assertEqual(mkConsume.call_args_list, [])

                # Forage model is given
                self.Egg.consume(larva, egg_mass)
                self.assertEqual(mkConsume.call_args_list,
                                 [mk.call(self.Egg, larva, egg_mass)])

    def test_setup(self):
        """test setup the class"""

        # Test if have the model
        kwargs = {keyword.egg_forage: self.forage}
        self.Egg = forage.Egg.setup(**kwargs)
        self.assertIsInstance(self.Egg, forage.Egg)
        self.assertEqual(self.Egg.forage, self.forage)
        self.assertEqual(self.Egg.behavior, keyword.forage_egg)

        # Test if have the model
        kwargs = {}
        self.Egg = forage.Egg.setup(**kwargs)
        self.assertIsInstance(self.Egg, forage.Egg)
        self.assertEqual(self.Egg.forage, None)
        self.assertEqual(self.Egg.behavior, keyword.forage_egg)
