import unittest      as ut
import unittest.mock as mk

import dataclasses as dclass

import source.keyword as keyword

import source.agents.larva   as agent_larva
import source.agents.pupa as agent_pupa

import source.development.larva as development


class LarvaTest(agent_larva.Larva):
    """Class to add dynamic values for tests"""

    mass     = mk.MagicMock(spec=float)
    genotype = mk.MagicMock(spec=str)
    age      = mk.MagicMock(spec=int)


class TestLarva(ut.TestCase):
    """test the Larva development class"""

    def setUp(self):
        """Setup the tests"""

        self.development = mk.MagicMock(spec=callable)

        self.Larva = development.Larva(self.development)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.Larva, development.Larva)

        self.assertEqual(self.Larva.development, self.development)

        self.assertEqual(self.Larva.behavior, keyword.development_larva)

        self.assertTrue(dclass.is_dataclass(self.Larva))

    def test__use_development(self):
        """test if we use the development system"""

        self.assertTrue(self.Larva._use_development)

        self.Larva.development = None
        self.assertFalse(self.Larva._use_development)

    def test__develop(self):
        """test determine if larva develops"""

        larva = mk.create_autospec(LarvaTest, spec_set=True)

        with mk.patch.object(development.Larva, '_use_development',
                             autospec=True) as mkUse:
            mkUse.__get__ = mk.MagicMock(side_effect=[False, True])

            # Test when we don't have a model
            self.assertFalse(self.Larva._develop(larva))
            self.assertEqual(self.development.call_args_list, [])

            # Test when have a model
            self.assertEqual(self.Larva._develop(larva),
                             self.development.return_value)
            self.assertEqual(self.development.call_args_list,
                             [mk.call(larva.mass, larva.age, larva.genotype)])

    def test__make_pupa(self):
        """test make a pupa"""

        larva   = mk.create_autospec(LarvaTest, spec_set=True)
        pupa = mk.create_autospec(agent_pupa.Pupa, spec_set=True)

        with mk.patch.object(agent_pupa.Pupa, 'advance',
                             autospec=True) as mkAdvance:
            mkAdvance.return_value = pupa

            self.Larva._make_pupa(larva)
            self.assertEqual(pupa.activate.call_args_list,
                             [mk.call()])
            self.assertEqual(mkAdvance.call_args_list,
                             [mk.call(larva)])

    def test_develop(self):
        """test run development system"""

        larva = mk.create_autospec(LarvaTest, spec_set=True)

        with mk.patch.object(development.Larva, '_develop',
                             autospec=True) as mkDevelop:
            with mk.patch.object(development.Larva, '_make_pupa',
                                 autospec=True) as mkMake:
                mkDevelop.side_effect = [False, True]
                master = mk.MagicMock()
                master.attach_mock(larva,    'larva')
                master.attach_mock(mkMake, 'make')

                # Does not develop
                self.Larva.develop(larva)
                self.assertEqual(mkDevelop.call_args_list,
                                 [mk.call(self.Larva, larva)])
                self.assertEqual(master.mock_calls, [])

                mkDevelop.reset_mock()
                # Does develop
                self.Larva.develop(larva)
                self.assertEqual(mkDevelop.call_args_list,
                                 [mk.call(self.Larva, larva)])
                self.assertEqual(master.mock_calls,
                                 [mk.call.larva.deactivate(),
                                  mk.call.make(larva)])

    def test_setup(self):
        """test setup the class"""

        # Test if have the model
        kwargs = {keyword.larva_development: self.development}
        self.Larva = development.Larva.setup(**kwargs)
        self.assertIsInstance(self.Larva, development.Larva)
        self.assertEqual(self.Larva.development, self.development)
        self.assertEqual(self.Larva.behavior, keyword.development_larva)

        # Test if have the model
        kwargs = {}
        self.Larva = development.Larva.setup(**kwargs)
        self.assertIsInstance(self.Larva, development.Larva)
        self.assertEqual(self.Larva.development, None)
        self.assertEqual(self.Larva.behavior, keyword.development_larva)
