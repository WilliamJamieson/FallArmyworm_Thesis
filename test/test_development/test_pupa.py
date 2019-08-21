import unittest      as ut
import unittest.mock as mk

import dataclasses as dclass

import source.keyword as keyword

import source.agents.pupa   as agent_pupa
import source.agents.adult as agent_adult

import source.development.pupa as development


class PupaTest(agent_pupa.Pupa):
    """Class to add dynamic values for tests"""

    mass     = mk.MagicMock(spec=float)
    genotype = mk.MagicMock(spec=str)
    age      = mk.MagicMock(spec=int)


class TestPupa(ut.TestCase):
    """test the Pupa development class"""

    def setUp(self):
        """Setup the tests"""

        self.development = mk.MagicMock(spec=callable)

        self.Pupa = development.Pupa(self.development)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.Pupa, development.Pupa)

        self.assertEqual(self.Pupa.development, self.development)

        self.assertTrue(dclass.is_dataclass(self.Pupa))

    def test__use_development(self):
        """test if we use the development system"""

        self.assertTrue(self.Pupa._use_development)

        self.Pupa.development = None
        self.assertFalse(self.Pupa._use_development)

    def test__develop(self):
        """test determine if pupa develops"""

        pupa = mk.create_autospec(PupaTest, spec_set=True)

        with mk.patch.object(development.Pupa, '_use_development',
                             autospec=True) as mkUse:
            mkUse.__get__ = mk.MagicMock(side_effect=[False, True])

            # Test when we don't have a model
            self.assertFalse(self.Pupa._develop(pupa))
            self.assertEqual(self.development.call_args_list, [])

            # Test when have a model
            self.assertEqual(self.Pupa._develop(pupa),
                             self.development.return_value)
            self.assertEqual(self.development.call_args_list,
                             [mk.call(pupa.mass, pupa.age, pupa.genotype)])

    def test__make_adult(self):
        """test make a adult"""

        pupa   = mk.create_autospec(PupaTest, spec_set=True)
        adult = mk.create_autospec(agent_adult.Adult, spec_set=True)

        with mk.patch.object(agent_adult.Adult, 'advance',
                             autospec=True) as mkAdvance:
            mkAdvance.return_value = adult

            self.Pupa._make_adult(pupa)
            self.assertEqual(adult.activate.call_args_list,
                             [mk.call()])
            self.assertEqual(mkAdvance.call_args_list,
                             [mk.call(pupa)])

    def test_develop(self):
        """test run development system"""

        pupa = mk.create_autospec(PupaTest, spec_set=True)

        with mk.patch.object(development.Pupa, '_develop',
                             autospec=True) as mkDevelop:
            with mk.patch.object(development.Pupa, '_make_adult',
                                 autospec=True) as mkMake:
                mkDevelop.side_effect = [False, True]
                master = mk.MagicMock()
                master.attach_mock(pupa,    'pupa')
                master.attach_mock(mkMake, 'make')

                # Does not develop
                self.Pupa.develop(pupa)
                self.assertEqual(mkDevelop.call_args_list,
                                 [mk.call(self.Pupa, pupa)])
                self.assertEqual(master.mock_calls, [])

                mkDevelop.reset_mock()
                # Does develop
                self.Pupa.develop(pupa)
                self.assertEqual(mkDevelop.call_args_list,
                                 [mk.call(self.Pupa, pupa)])
                self.assertEqual(master.mock_calls,
                                 [mk.call.pupa.deactivate(),
                                  mk.call.make(pupa)])

    def test_setup(self):
        """test setup the class"""

        # Test if have the model
        kwargs = {keyword.pupa_development: self.development}
        self.Pupa = development.Pupa.setup(**kwargs)
        self.assertIsInstance(self.Pupa, development.Pupa)
        self.assertEqual(self.Pupa.development, self.development)

        # Test if have the model
        kwargs = {}
        self.Pupa = development.Pupa.setup(**kwargs)
        self.assertIsInstance(self.Pupa, development.Pupa)
        self.assertEqual(self.Pupa.development, None)
