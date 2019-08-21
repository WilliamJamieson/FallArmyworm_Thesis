import unittest      as ut
import unittest.mock as mk

import dataclasses as dclass

import source.keyword as keyword

import source.agents.larva as agent_larva

import source.forage.larva as forage


class LarvaTest(agent_larva.Larva):
    """Class to add dynamic values for tests"""

    mass     = mk.MagicMock(spec=float)
    genotype = mk.MagicMock(spec=str)


class TestLarva(ut.TestCase):
    """test the Larva forage class"""

    def setUp(self):
        """Setup the tests"""

        self.forage = mk.MagicMock(spec=callable)

        self.Larva = forage.Larva(self.forage)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.Larva, forage.Larva)

        self.assertEqual(self.Larva.forage, self.forage)

        self.assertTrue(dclass.is_dataclass(self.Larva))

    def test__use_forage(self):
        """test if we use the forage system"""

        self.assertTrue(self.Larva._use_forage)

        self.Larva.forage = None
        self.assertFalse(self.Larva._use_forage)

    def test__available(self):
        """test get the available amount of mass"""

        larva  = mk.create_autospec(LarvaTest, spec_set=True)
        target = mk.create_autospec(LarvaTest, spec_set=True)

        self.assertEqual(self.Larva._available(larva, target),
                         self.forage.return_value)
        self.assertEqual(self.forage.call_args_list,
                         [mk.call(target.mass, larva.mass, larva.genotype)])

    def test__consume(self):
        """test consume the larva"""

        larva  = mk.create_autospec(LarvaTest, spec_set=True)
        target = mk.create_autospec(LarvaTest, spec_set=True)

        mass = mk.MagicMock(spec=float)
        target.mass = mass

        with mk.patch.object(forage.Larva, '_available',
                             autospec=True) as mkAvailable:
            self.Larva._consume(larva, target)
            self.assertEqual(target.die.call_args_list,
                             [mk.call(keyword.cannibalism)])
            self.assertEqual(target.mass, mass.__sub__.return_value)
            self.assertEqual(mass.__sub__.call_args_list,
                             [mk.call(larva.add_larva.return_value)])
            self.assertEqual(larva.add_larva.call_args_list,
                             [mk.call(mkAvailable.return_value)])
            self.assertEqual(mkAvailable.call_args_list,
                             [mk.call(self.Larva, larva, target)])

    def test_consume(self):
        """test consume the larva"""

        larva  = mk.create_autospec(LarvaTest, spec_set=True)
        target = mk.create_autospec(LarvaTest, spec_set=True)

        with mk.patch.object(forage.Larva, '_use_forage',
                             autospec=True) as mkUse:
            with mk.patch.object(forage.Larva, '_consume',
                                 autospec=True) as mkConsume:
                mkUse.__get__ = mk.MagicMock(side_effect=[False, True])

                # No forage model is given
                self.Larva.consume(larva, target)
                self.assertEqual(mkConsume.call_args_list, [])

                # Forage model is given
                self.Larva.consume(larva, target)
                self.assertEqual(mkConsume.call_args_list,
                                 [mk.call(self.Larva, larva, target)])

    def test_setup(self):
        """test setup the class"""

        # Test if have the model
        kwargs = {keyword.larva_forage: self.forage}
        self.Larva = forage.Larva.setup(**kwargs)
        self.assertIsInstance(self.Larva, forage.Larva)
        self.assertEqual(self.Larva.forage, self.forage)

        # Test if have the model
        kwargs = {}
        self.Larva = forage.Larva.setup(**kwargs)
        self.assertIsInstance(self.Larva, forage.Larva)
        self.assertEqual(self.Larva.forage, None)
