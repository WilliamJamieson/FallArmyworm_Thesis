import unittest      as ut
import unittest.mock as mk

import dataclasses as dclass

import source.keyword as keyword

import source.agents.larva as agent_larva

import source.survival.larva as survival


class LarvaTest(agent_larva.Larva):
    """Class to add dynamic values for tests"""

    alive    = mk.MagicMock(spec=bool)
    mass     = mk.MagicMock(spec=float)
    genotype = mk.MagicMock(spec=str)
    starve   = mk.MagicMock(spec=bool)


class TestLarva(ut.TestCase):
    """test the Larva survival class"""

    def setUp(self):
        """Setup the tests"""

        self.survival = mk.MagicMock(spec=callable)

        self.Larva = survival.Larva(self.survival)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.Larva, survival.Larva)

        self.assertEqual(self.Larva.survival, self.survival)

        self.assertTrue(dclass.is_dataclass(self.Larva))

    def test__use_survival(self):
        """test if we use the survival system"""

        self.assertTrue(self.Larva._use_survival)

        self.Larva.survival = None
        self.assertFalse(self.Larva._use_survival)

    def test_starve(self):
        """test if the larva starves"""

        larva = mk.create_autospec(LarvaTest, spec_set=True)

        # Not starve
        larva.starve = False
        self.Larva._starve(larva)
        self.assertEqual(larva.die.call_args_list, [])

        # starve
        larva.starve = True
        self.Larva._starve(larva)
        self.assertEqual(larva.die.call_args_list,
                         [mk.call(keyword.starve)])

    def test__survive(self):
        """test determine if larva survives"""

        larva = mk.create_autospec(LarvaTest, spec_set=True)

        with mk.patch.object(survival.Larva, '_use_survival',
                             autospec=True) as mkUse:
            mkUse.__get__ = mk.MagicMock(side_effect=[False, True, True])

            # Test when we don't have a model
            self.assertTrue(self.Larva._survive(larva))
            self.assertEqual(self.survival.call_args_list, [])

            # Test when have a model and are dead
            larva.alive = False
            self.assertTrue(self.Larva._survive(larva))
            self.assertEqual(self.survival.call_args_list, [])

            # Test when have a model and are alive
            larva.alive = True
            self.assertEqual(self.Larva._survive(larva),
                             self.survival.return_value)
            self.assertEqual(self.survival.call_args_list,
                             [mk.call(larva.mass, larva.genotype, larva.bt)])

    def test_survive(self):
        """test run the behavior"""

        larva = mk.create_autospec(LarvaTest, spec_set=True)

        with mk.patch.object(survival.Larva, '_survive',
                             autospec=True) as mkSurvive:
            with mk.patch.object(survival.Larva, '_starve',
                                 autospec=True) as mkStarve:
                mkSurvive.side_effect = [True, False]

                # Test if survives
                self.Larva.survive(larva)
                self.assertEqual(larva.die.call_args_list, [])
                self.assertEqual(mkSurvive.call_args_list,
                                 [mk.call(self.Larva, larva)])
                self.assertEqual(mkStarve.call_args_list,
                                 [mk.call(larva)])

                mkSurvive.reset_mock()
                mkStarve.reset_mock()
                # Test if not survives
                self.Larva.survive(larva)
                self.assertEqual(larva.die.call_args_list,
                                 [mk.call(keyword.survival)])
                self.assertEqual(mkSurvive.call_args_list,
                                 [mk.call(self.Larva, larva)])
                self.assertEqual(mkStarve.call_args_list,
                                 [mk.call(larva)])

    def test_setup(self):
        """test setup the class"""

        # Test if have the model
        kwargs = {keyword.larva_survival: self.survival}
        self.Larva = survival.Larva.setup(**kwargs)
        self.assertIsInstance(self.Larva, survival.Larva)
        self.assertEqual(self.Larva.survival, self.survival)

        # Test if have the model
        kwargs = {}
        self.Larva = survival.Larva.setup(**kwargs)
        self.assertIsInstance(self.Larva, survival.Larva)
        self.assertEqual(self.Larva.survival, None)
