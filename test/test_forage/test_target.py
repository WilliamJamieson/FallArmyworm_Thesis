import unittest      as ut
import unittest.mock as mk

import dataclasses as dclass

import source.keyword as keyword

import source.agents.egg_mass as agent_egg_mass
import source.agents.larva    as agent_larva

import source.forage.target as forage


class LarvaTest(agent_larva.Larva):
    """Class to add dynamic values for tests"""


    agent_key = keyword.larva
    mass      = mk.MagicMock(spec=float)
    genotype  = mk.MagicMock(spec=str)
    target    = mk.MagicMock()


class EggMassTest(agent_egg_mass.EggMass):
    """Class to add dynamic values for tests"""

    agent_key = keyword.egg_mass


class TestTarget(ut.TestCase):
    """test Target foraging class"""

    def setUp(self):
        """Setup the tests"""

        self.loss = mk.MagicMock(spec=callable)

        self.Target = forage.Target(self.loss)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.Target, forage.Target)

        self.assertEqual(self.Target.loss, self.loss)

        self.assertTrue(dclass.is_dataclass(self.Target))

    def test__use_loss(self):
        """test if we use the loss system"""

        self.assertTrue(self.Target._use_loss)

        self.Target.loss = None
        self.assertFalse(self.Target._use_loss)

    def test__keep_target(self):
        """test if we loose the target"""

        larva = mk.create_autospec(LarvaTest, spec_set=True)

        with mk.patch.object(forage.Target, '_use_loss',
                             autospec=True) as mkUse:
            mkUse.__get__ = mk.MagicMock(side_effect=[False, True, True])

            # Test no loss function
            self.assertFalse(self.Target._keep_target(larva, larva))
            self.assertEqual(self.loss.call_args_list, [])

            # Test target is egg_mass
            target = mk.create_autospec(EggMassTest, spec_set=True)
            self.assertEqual(self.Target._keep_target(larva, target),
                             self.loss.return_value)
            self.assertEqual(self.loss.call_args_list,
                             [mk.call(larva.mass, target.mass,
                                      larva.genotype, target.agent_key)])

            self.loss.reset_mock()
            # Test target is larva
            target = mk.create_autospec(LarvaTest, spec_set=True)
            self.assertEqual(self.Target._keep_target(larva, target),
                             self.loss.return_value)
            self.assertEqual(self.loss.call_args_list,
                             [mk.call(larva.mass, target.mass,
                                      larva.genotype, target.agent_key)])

    def test__consume_target(self):
        """test consume the target larva"""

        larva = mk.create_autospec(LarvaTest, spec_set=True)

        # Target is egg_mass
        target = mk.create_autospec(EggMassTest, spec_set=True)
        target.agent_key = keyword.egg_mass
        self.Target._consume_target(larva, target)
        self.assertEqual(larva.consume_egg.call_args_list,
                         [mk.call(target)])
        self.assertEqual(larva.consume_larva.call_args_list, [])

        larva.reset_mock()
        # Target is egg_mass
        target = mk.create_autospec(LarvaTest, spec_set=True)
        target.agent_key = keyword.larva
        self.Target._consume_target(larva, target)
        self.assertEqual(larva.consume_egg.call_args_list, [])
        self.assertEqual(larva.consume_larva.call_args_list,
                         [mk.call(target)])

    def test_consume(self):
        """test consume the target"""

        larva  = mk.create_autospec(LarvaTest, spec_set=True)
        target = mk.MagicMock()

        larva.target = target

        with mk.patch.object(forage.Target, '_keep_target',
                             autospec=True) as mkKeep:
            with mk.patch.object(forage.Target, '_consume_target',
                                 autospec=True) as mkConsume:
                mkKeep.side_effect = [True, False]

                # Consume target
                self.Target.consume(larva)
                self.assertEqual(larva.target, target)
                self.assertEqual(mkKeep.call_args_list,
                                 [mk.call(self.Target, larva, target)])
                self.assertEqual(mkConsume.call_args_list,
                                 [mk.call(larva, target)])

                mkKeep.reset_mock()
                mkConsume.reset_mock()
                # Keep target
                self.Target.consume(larva)
                self.assertEqual(larva.target, None)
                self.assertEqual(mkKeep.call_args_list,
                                 [mk.call(self.Target, larva, target)])
                self.assertEqual(mkConsume.call_args_list, [])

    def test_setup(self):
        """test setup the class"""

        # Test if have the model
        kwargs = {keyword.loss: self.loss}
        self.Target = forage.Target.setup(**kwargs)
        self.assertIsInstance(self.Target, forage.Target)
        self.assertEqual(self.Target.loss, self.loss)

        # Test if have the model
        kwargs = {}
        self.Target = forage.Target.setup(**kwargs)
        self.assertIsInstance(self.Target, forage.Target)
        self.assertEqual(self.Target.loss, None)
