import unittest      as ut
import unittest.mock as mk

import dataclasses as dclass

import source.keyword as keyword

import source.agents.adult    as agent_adult
import source.agents.egg_mass as egg_mass

import source.reproduction.lay as lay


class AdultTest(agent_adult.Adult):
    """Class to add dynamic values for tests"""

    mass     = mk.MagicMock(spec=float)
    age      = mk.MagicMock(spec=int)
    genotype = mk.MagicMock(spec=str)
    num_eggs = mk.MagicMock(spec=int)


class TestLay(ut.TestCase):
    """test Lay behavior class"""

    def setUp(self):
        """Setup the tests"""

        self.trials    = mk.MagicMock(spec=int)
        self.fecundity = mk.MagicMock(spec=callable)
        self.density   = mk.MagicMock(spec=callable)

        self.Lay = lay.Lay(self.trials,
                           self.fecundity,
                           self.density)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.Lay, lay.Lay)

        self.assertEqual(self.Lay.trials,    self.trials)
        self.assertEqual(self.Lay.fecundity, self.fecundity)
        self.assertEqual(self.Lay.density,   self.density)

        self.assertEqual(self.Lay.behavior, keyword.lay_eggs)

        self.assertTrue(dclass.is_dataclass(self.Lay))

    def test__use_fecundity(self):
        """test if we use the fecundity system"""

        self.assertTrue(self.Lay._use_fecundity)

        self.Lay.fecundity = None
        self.assertFalse(self.Lay._use_fecundity)

    def test__use_density(self):
        """test if we use the density system"""

        self.assertTrue(self.Lay._use_density)

        self.Lay.density = None
        self.assertFalse(self.Lay._use_density)

    def test_reset(self):
        """test reset the num_eggs"""

        adult = mk.create_autospec(AdultTest, spec_set=True)

        with mk.patch.object(lay.Lay, '_use_fecundity', autospec=True) as mkUse:
            mkUse.__get__ = mk.MagicMock(side_effect=[False, True])

            # No fecundity
            self.assertEqual(self.Lay.reset(adult), 0)
            self.assertEqual(self.fecundity.call_args_list, [])

            # Has fecundity
            self.assertEqual(self.Lay.reset(adult),
                             self.fecundity.return_value)
            self.assertEqual(self.fecundity.call_args_list,
                             [mk.call(adult.mass, adult.age, adult.genotype)])

    def test__check_density(self):
        """test the density checker"""

        adult  = mk.create_autospec(AdultTest, spec_set=True)
        number = mk.MagicMock(spec=int)

        with mk.patch.object(lay.Lay, '_use_density', autospec=True) as mkUse:
            mkUse.__get__ = mk.MagicMock(side_effect=[False, True])

            # Test use is false
            self.assertTrue(self.Lay._check_density(adult, number))
            self.assertEqual(self.density.call_args_list, [])

            # Test use is True
            self.assertEqual(self.Lay._check_density(adult, number),
                             self.density.return_value)
            self.assertEqual(self.density.call_args_list,
                             [mk.call(number, adult.mass, adult.genotype)])

    def test__lay_egg_mass(self):
        """test lay an egg_mass"""

        adult  = mk.create_autospec(AdultTest, spec_set=True)
        number = mk.MagicMock(spec=int)

        num_eggs       = mk.MagicMock(spec=int)
        adult.num_eggs = num_eggs

        with mk.patch.object(lay.Lay, '_check_density',
                             autospec=True) as mkCheck:
            with mk.patch.object(egg_mass.EggMass, 'birth',
                                 autospec=True) as mkBirth:
                mkCheck.side_effect = [False, True]

                # Test Fail check
                self.assertEqual(self.Lay._lay_egg_mass(adult, number),
                                 ([], number))
                self.assertEqual(mkCheck.call_args_list,
                                 [mk.call(self.Lay, adult, number)])
                self.assertEqual(mkBirth.call_args_list, [])
                self.assertEqual(adult.num_eggs, num_eggs)
                self.assertEqual(number.__add__.call_args_list, [])
                self.assertEqual(num_eggs.__sub__.call_args_list, [])

                mkCheck.reset_mock()
                # Test pass check
                self.assertEqual(self.Lay._lay_egg_mass(adult, number),
                                 ([mkBirth.return_value],
                                   number.__add__.return_value))
                self.assertEqual(mkCheck.call_args_list,
                                 [mk.call(self.Lay, adult, number)])
                self.assertEqual(mkBirth.call_args_list,
                                 [mk.call(adult)])
                self.assertEqual(adult.num_eggs,
                                 num_eggs.__sub__.return_value)
                self.assertEqual(number.__add__.call_args_list,
                                 [mk.call(1)])
                self.assertEqual(num_eggs.__sub__.call_args_list,
                                 [mk.call(1)])
                
    def test__lay(self):
        """test lay loop"""

        adult = mk.create_autospec(AdultTest, spec_set=True)

        self.Lay.trials = 3
        with mk.patch.object(lay.Lay, '_lay_egg_mass', autospec=True) as mkLay:
            # No Break
            adult.num_eggs.__le__.side_effect = [False, False, False]
            numbers    = []
            effects    = []
            egg_masses = []
            for _ in range(3):
                number = mk.MagicMock(spec=int)
                new    = [mk.create_autospec(egg_mass.EggMass, spec_set=True)
                          for _ in range(3)]
                effects.append((new, number))
                numbers.append(number)
                egg_masses.extend(new)
            mkLay.side_effect = effects
            self.assertEqual(self.Lay._lay(adult), egg_masses)
            self.assertEqual(len(mkLay.call_args_list), 3)
            call = mkLay.call_args_list.pop(0)
            self.assertEqual(call,
                             mk.call(self.Lay,
                                     adult, adult.population.return_value))
            self.assertEqual(adult.population.call_args_list,
                             [mk.call()])
            for index, call in enumerate(mkLay.call_args_list):
                self.assertEqual(call,
                                 mk.call(self.Lay,
                                         adult, numbers[index]))
            self.assertEqual(len(mkLay.call_args_list), 2)
            for call in adult.num_eggs.__le__.call_args_list:
                self.assertEqual(call, mk.call(0))
            self.assertEqual(len(adult.num_eggs.__le__.call_args_list), 3)

            adult.reset_mock()
            adult.num_eggs.__le__.reset_mock()
            mkLay.reset_mock()
            # Break on 3rd round
            adult.num_eggs.__le__.side_effect = [False, False, True]
            numbers    = []
            effects    = []
            egg_masses = []
            for _ in range(2):
                number = mk.MagicMock(spec=int)
                new    = [mk.create_autospec(egg_mass.EggMass, spec_set=True)
                          for _ in range(3)]
                effects.append((new, number))
                numbers.append(number)
                egg_masses.extend(new)
            mkLay.side_effect = effects
            self.assertEqual(self.Lay._lay(adult), egg_masses)
            self.assertEqual(len(mkLay.call_args_list), 2)
            call = mkLay.call_args_list.pop(0)
            self.assertEqual(call,
                             mk.call(self.Lay,
                                     adult, adult.population.return_value))
            self.assertEqual(adult.population.call_args_list,
                             [mk.call()])
            for index, call in enumerate(mkLay.call_args_list):
                self.assertEqual(call,
                                 mk.call(self.Lay,
                                         adult, numbers[index]))
            self.assertEqual(len(mkLay.call_args_list), 1)
            for call in adult.num_eggs.__le__.call_args_list:
                self.assertEqual(call, mk.call(0))
            self.assertEqual(len(adult.num_eggs.__le__.call_args_list), 3)

            adult.reset_mock()
            adult.num_eggs.__le__.reset_mock()
            mkLay.reset_mock()
            # Break on 2nd round
            adult.num_eggs.__le__.side_effect = [False, True]
            numbers    = []
            effects    = []
            egg_masses = []
            for _ in range(1):
                number = mk.MagicMock(spec=int)
                new    = [mk.create_autospec(egg_mass.EggMass, spec_set=True)
                          for _ in range(3)]
                effects.append((new, number))
                numbers.append(number)
                egg_masses.extend(new)
            mkLay.side_effect = effects
            self.assertEqual(self.Lay._lay(adult), egg_masses)
            self.assertEqual(len(mkLay.call_args_list), 1)
            call = mkLay.call_args_list.pop(0)
            self.assertEqual(call,
                             mk.call(self.Lay,
                                     adult, adult.population.return_value))
            self.assertEqual(adult.population.call_args_list,
                             [mk.call()])
            self.assertEqual(len(mkLay.call_args_list), 0)
            for call in adult.num_eggs.__le__.call_args_list:
                self.assertEqual(call, mk.call(0))
            self.assertEqual(len(adult.num_eggs.__le__.call_args_list), 2)

            adult.reset_mock()
            adult.num_eggs.__le__.reset_mock()
            mkLay.reset_mock()
            # Break on 1st round
            adult.num_eggs.__le__.side_effect = [True]
            effects    = []
            egg_masses = []
            mkLay.side_effect = effects
            self.assertEqual(self.Lay._lay(adult), egg_masses)
            self.assertEqual(len(mkLay.call_args_list), 0)
            self.assertEqual(adult.population.call_args_list,
                             [mk.call()])
            for call in adult.num_eggs.__le__.call_args_list:
                self.assertEqual(call, mk.call(0))
            self.assertEqual(len(adult.num_eggs.__le__.call_args_list), 1)

    def test_lay(self):
        """test run the behavior"""

        adult = mk.create_autospec(AdultTest, spec_set=True)

        with mk.patch.object(lay.Lay, '_lay', autospec=True) as mkLay:
            adult.num_eggs.__gt__.side_effect = [False, True]

            # Test num fails
            self.assertEqual(self.Lay.lay(adult), [])
            self.assertEqual(mkLay.call_args_list, [])
            self.assertEqual(adult.num_eggs.__gt__.call_args_list,
                             [mk.call(0)])

            adult.num_eggs.__gt__.reset_mock()
            # Test num is good
            self.assertEqual(self.Lay.lay(adult),
                             mkLay.return_value)
            self.assertEqual(mkLay.call_args_list,
                             [mk.call(self.Lay, adult)])
            self.assertEqual(adult.num_eggs.__gt__.call_args_list,
                             [mk.call(0)])

    def test_setup(self):
        """test setup the class"""

        # Test if have the models
        kwargs = {keyword.trials:    self.trials,
                  keyword.fecundity: self.fecundity,
                  keyword.density:   self.density}
        self.Lay = lay.Lay.setup(**kwargs)
        self.assertIsInstance(self.Lay, lay.Lay)
        self.assertEqual(self.Lay.trials,    self.trials)
        self.assertEqual(self.Lay.fecundity, self.fecundity)
        self.assertEqual(self.Lay.density,   self.density)
        self.assertEqual(self.Lay.behavior, keyword.lay_eggs)

        # Test if have no models
        kwargs = {}
        self.Lay = lay.Lay.setup(**kwargs)
        self.assertIsInstance(self.Lay, lay.Lay)
        self.assertEqual(self.Lay.trials,    0)
        self.assertEqual(self.Lay.fecundity, None)
        self.assertEqual(self.Lay.density,   None)
        self.assertEqual(self.Lay.behavior, keyword.lay_eggs)
