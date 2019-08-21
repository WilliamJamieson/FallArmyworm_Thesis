import unittest      as ut
import unittest.mock as mk

import dataclasses as dclass

import source.keyword as keyword

import source.agents.pupa as agent_pupa

import source.survival.pupa as survival


class PupaTest(agent_pupa.Pupa):
    """Class to add dynamic values for tests"""

    mass     = mk.MagicMock(spec=float)
    genotype = mk.MagicMock(spec=str)


class TestPupa(ut.TestCase):
    """test the Pupa survival class"""

    def setUp(self):
        """Setup the tests"""

        self.survival = mk.MagicMock(spec=callable)

        self.Pupa = survival.Pupa(self.survival)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.Pupa, survival.Pupa)

        self.assertEqual(self.Pupa.survival, self.survival)

        self.assertEqual(self.Pupa.behavior, keyword.survival_pupa)

        self.assertTrue(dclass.is_dataclass(self.Pupa))

    def test__use_survival(self):
        """test if we use the survival system"""

        self.assertTrue(self.Pupa._use_survival)

        self.Pupa.survival = None
        self.assertFalse(self.Pupa._use_survival)

    def test__survive(self):
        """test determine if pupa survives"""

        pupa = mk.create_autospec(PupaTest, spec_set=True)

        with mk.patch.object(survival.Pupa, '_use_survival',
                             autospec=True) as mkUse:
            mkUse.__get__ = mk.MagicMock(side_effect=[False, True])

            # Test when we don't have a model
            self.assertTrue(self.Pupa._survive(pupa))
            self.assertEqual(self.survival.call_args_list, [])

            # Test when have a model
            self.assertEqual(self.Pupa._survive(pupa),
                             self.survival.return_value)
            self.assertEqual(self.survival.call_args_list,
                             [mk.call(pupa.mass, pupa.genotype)])

    def test_survive(self):
        """test run the behavior"""

        pupa = mk.create_autospec(PupaTest, spec_set=True)

        with mk.patch.object(survival.Pupa, '_survive',
                             autospec=True) as mkSurvive:
            mkSurvive.side_effect = [True, False]

            # Test if survives
            self.Pupa.survive(pupa)
            self.assertEqual(pupa.die.call_args_list, [])
            self.assertEqual(mkSurvive.call_args_list,
                             [mk.call(self.Pupa, pupa)])

            mkSurvive.reset_mock()
            # Test if not survives
            self.Pupa.survive(pupa)
            self.assertEqual(pupa.die.call_args_list,
                             [mk.call(keyword.survival)])
            self.assertEqual(mkSurvive.call_args_list,
                             [mk.call(self.Pupa, pupa)])

    def test_setup(self):
        """test setup the class"""

        # Test if have the model
        kwargs = {keyword.pupa_survival: self.survival}
        self.Pupa = survival.Pupa.setup(**kwargs)
        self.assertIsInstance(self.Pupa, survival.Pupa)
        self.assertEqual(self.Pupa.survival, self.survival)
        self.assertEqual(self.Pupa.behavior, keyword.survival_pupa)

        # Test if have the model
        kwargs = {}
        self.Pupa = survival.Pupa.setup(**kwargs)
        self.assertIsInstance(self.Pupa, survival.Pupa)
        self.assertEqual(self.Pupa.survival, None)
        self.assertEqual(self.Pupa.behavior, keyword.survival_pupa)
