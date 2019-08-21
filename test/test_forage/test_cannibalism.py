import unittest      as ut
import unittest.mock as mk

import dataclasses  as dclass
import numpy.random as rnd

import source.keyword as keyword

import source.agents.egg_mass as agent_egg_mass
import source.agents.larva    as agent_larva

import source.forage.cannibalism as cannibalism


class LarvaTest(agent_larva.Larva):
    """Class to add dynamic values for tests"""

    agent_key = mk.MagicMock(spec=str)
    mass      = mk.MagicMock(spec=float)
    genotype  = mk.MagicMock(spec=str)
    alive     = mk.MagicMock(spec=bool)
    full      = mk.MagicMock(spec=bool)


class EggMassTest(agent_egg_mass.EggMass):
    """Class to add dynamic values for tests"""

    agent_key = keyword.egg_mass
    
    
class TestCannibalism(ut.TestCase):
    """test the Cannibalism behavior class"""

    def setUp(self):
        """Setup the tests"""

        self.fight     = mk.MagicMock(spec=callable)
        self.encounter = mk.MagicMock(spec=callable)
        self.radius    = mk.MagicMock(spec=callable)

        self.Cannibalism = cannibalism.Cannibalism(self.fight,
                                                   self.encounter,
                                                   self.radius)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.Cannibalism, cannibalism.Cannibalism)

        self.assertEqual(self.Cannibalism.fight,     self.fight)
        self.assertEqual(self.Cannibalism.encounter, self.encounter)
        self.assertEqual(self.Cannibalism.radius,    self.radius)

        self.assertEqual(self.Cannibalism.behavior, keyword.cannibal)

        self.assertTrue(dclass.is_dataclass(self.Cannibalism))

    def test__use_fight(self):
        """test if we use the fight system"""

        self.assertTrue(self.Cannibalism._use_fight)

        self.Cannibalism.fight = None
        self.assertFalse(self.Cannibalism._use_fight)

    def test__winner(self):
        """test determine if larva is winner of fight with target"""

        larva  = mk.create_autospec(LarvaTest, spec_set=True)
        target = mk.create_autospec(LarvaTest, spec_set=True)

        self.assertEqual(self.Cannibalism._winner(larva, target),
                         self.fight.return_value)
        self.assertEqual(self.fight.call_args_list,
                         [mk.call(larva.mass, target.mass)])
        
    def test__fight(self):
        """test run fight"""

        larva  = mk.create_autospec(LarvaTest, spec_set=True)
        target = mk.create_autospec(LarvaTest, spec_set=True)

        with mk.patch.object(cannibalism.Cannibalism, '_winner',
                             autospec=True) as mkWinner:
            mkWinner.side_effect = [True, False]

            # Test if larva wins
            self.Cannibalism._fight(larva, target)
            self.assertEqual(larva.consume_larva.call_args_list,
                             [mk.call(target)])
            self.assertEqual(target.consume_larva.call_args_list, [])
            self.assertEqual(mkWinner.call_args_list,
                             [mk.call(self.Cannibalism, larva, target)])

            mkWinner.reset_mock()
            larva.reset_mock()
            # Test if target wins
            self.Cannibalism._fight(larva, target)
            self.assertEqual(target.consume_larva.call_args_list,
                             [mk.call(larva)])
            self.assertEqual(larva.consume_larva.call_args_list, [])
            self.assertEqual(mkWinner.call_args_list,
                             [mk.call(self.Cannibalism, larva, target)])

    def test__contest(self):
        """test run a contest"""

        larva  = mk.create_autospec(LarvaTest, spec_set=True)
        target = mk.create_autospec(LarvaTest, spec_set=True)

        with mk.patch.object(cannibalism.Cannibalism, '_use_fight',
                             autospec=True) as mkUse:
            with mk.patch.object(cannibalism.Cannibalism, '_fight',
                                 autospec=True) as mkFight:
                mkUse.__get__ = mk.MagicMock(side_effect=[False, True])

                # Test if no fight model
                self.Cannibalism._contest(larva, target)
                self.assertEqual(mkFight.call_args_list, [])

                # Test if fight model
                self.Cannibalism._contest(larva, target)
                self.assertEqual(mkFight.call_args_list,
                                 [mk.call(self.Cannibalism, larva, target)])

    def test__use_radius(self):
        """test if we use the radius system"""

        self.assertTrue(self.Cannibalism._use_radius)

        self.Cannibalism.radius = None
        self.assertFalse(self.Cannibalism._use_radius)

    def test__bounds(self):
        """test get the bounds on the radius"""

        larva = mk.create_autospec(LarvaTest, spec_set=True)

        with mk.patch.object(cannibalism.Cannibalism, '_use_radius',
                             autospec=True) as mkUse:
            mkUse.__get__ = mk.MagicMock(side_effect=[False, True])

            # Test if no radius model
            self.assertEqual(self.Cannibalism._bounds(larva),
                             {keyword.upper: 0,
                              keyword.lower: 0})
            self.assertEqual(self.radius.call_args_list, [])

            # Test if radius model
            self.assertEqual(self.Cannibalism._bounds(larva),
                             {keyword.upper: self.radius.return_value,
                              keyword.lower: 0})
            self.assertEqual(self.radius.call_args_list,
                             [mk.call(larva.mass, larva.genotype)])
            
    def test__targets(self):
        """test get list of targets for cannibalism"""

        larva = mk.create_autospec(LarvaTest, spec_set=True)

        bounds = {'test': mk.MagicMock()}

        with mk.patch.object(cannibalism.Cannibalism, '_bounds',
                             autospec=True) as mkBounds:
            mkBounds.return_value = bounds

            self.assertEqual(self.Cannibalism._targets(larva),
                             larva.targets.return_value)
            self.assertEqual(larva.targets.call_args_list,
                             [mk.call(**bounds)])
            self.assertEqual(mkBounds.call_args_list,
                             [mk.call(self.Cannibalism, larva)])

    def test__get_target(self):
        """test get insect to encounter"""

        target  = mk.create_autospec(LarvaTest, spec_set=True)
        targets = mk.MagicMock(spec=list)

        with mk.patch.object(rnd, 'choice') as mkRND:
            mkRND.return_value = target

            self.assertEqual(self.Cannibalism._get_target(targets), target)
            self.assertEqual(targets.remove.call_args_list,
                             [mk.call(target)])
            self.assertEqual(mkRND.call_args_list,
                             [mk.call(targets)])

    def test__can_encounter(self):
        """test if larva can encounter"""

        larva = mk.create_autospec(LarvaTest, spec_set=True)

        # Has encounter, larva is alive, larva is full
        larva.alive = True
        larva.full  = True
        self.assertFalse(self.Cannibalism._can_encounter(larva))

        # Has encounter, larva is alive, larva is not full
        larva.alive = True
        larva.full  = False
        self.assertTrue(self.Cannibalism._can_encounter(larva))

        # Has encounter, larva is  not alive, larva is full
        larva.alive = False
        larva.full  = False
        self.assertFalse(self.Cannibalism._can_encounter(larva))

        # Has no encounter
        self.Cannibalism.encounter = None
        larva.alive = True
        larva.full  = False
        self.assertFalse(self.Cannibalism._can_encounter(larva))

    def test__encounter(self):
        """test determine if encounter occurs"""

        larva   = mk.create_autospec(LarvaTest, spec_set=True)
        targets = mk.MagicMock(spec=list)

        with mk.patch.object(cannibalism.Cannibalism, '_can_encounter',
                             autospec=True) as mkCan:
            with mk.patch.object(cannibalism, 'len') as mkLen:
                mkCan.side_effect = [False, True]

                # Test cannot
                self.assertFalse(self.Cannibalism._encounter(larva, targets))
                self.assertEqual(self.encounter.call_args_list, [])
                self.assertEqual(mkLen.call_args_list, [])
                self.assertEqual(mkCan.call_args_list,
                                 [mk.call(self.Cannibalism, larva)])

                mkCan.reset_mock()
                # Test can
                self.assertEqual(self.Cannibalism._encounter(larva, targets),
                                 self.encounter.return_value)
                self.assertEqual(self.encounter.call_args_list,
                                 [mk.call(mkLen.return_value,
                                          larva.mass, larva.genotype)])
                self.assertEqual(mkLen.call_args_list,
                                 [mk.call(targets)])
                self.assertEqual(mkCan.call_args_list,
                                 [mk.call(self.Cannibalism, larva)])

    def test__cannibalize(self):
        """test perform cannibalism on target"""

        larva   = mk.create_autospec(LarvaTest, spec_set=True)
        targets = mk.MagicMock(spec=list)

        target = mk.create_autospec(LarvaTest, spec_set=True)

        with mk.patch.object(cannibalism.Cannibalism, '_get_target',
                             autospec=True) as mkGet:
            with mk.patch.object(cannibalism.Cannibalism, '_contest',
                                 autospec=True) as mkContest:
                mkGet.return_value = target

                # Test target is larva
                self.Cannibalism._cannibalize(larva, targets)
                self.assertEqual(mkContest.call_args_list,
                                 [mk.call(self.Cannibalism, larva, target)])
                self.assertEqual(larva.consume_egg.call_args_list, [])
                self.assertEqual(mkGet.call_args_list,
                                 [mk.call(targets)])

                mkGet.reset_mock()
                mkContest.reset_mock()
                # Test target is egg
                target.agent_key = keyword.egg_mass
                self.Cannibalism._cannibalize(larva, targets)
                self.assertEqual(mkContest.call_args_list, [])
                self.assertEqual(larva.consume_egg.call_args_list,
                                 [mk.call(target)])
                self.assertEqual(mkGet.call_args_list,
                                 [mk.call(targets)])
                
    def test__cannibalism(self):
        """test run cannibalism step"""

        larva   = mk.create_autospec(LarvaTest, spec_set=True)
        targets = mk.MagicMock(spec=list)

        with mk.patch.object(cannibalism.Cannibalism, '_encounter',
                             autospec=True) as mkEncounter:
            with mk.patch.object(cannibalism.Cannibalism, '_cannibalize',
                                 autospec=True) as mkCannibalize:
                mkEncounter.side_effect = [False, True]

                # Test if no encounter
                self.assertFalse(self.Cannibalism._cannibalism(larva, targets))
                self.assertEqual(mkEncounter.call_args_list,
                                 [mk.call(self.Cannibalism, larva, targets)])
                self.assertEqual(mkCannibalize.call_args_list, [])

                mkEncounter.reset_mock()
                # Test if encounter
                self.assertTrue(self.Cannibalism._cannibalism(larva, targets))
                self.assertEqual(mkEncounter.call_args_list,
                                 [mk.call(self.Cannibalism, larva, targets)])
                self.assertEqual(mkCannibalize.call_args_list,
                                 [mk.call(self.Cannibalism, larva, targets)])

    def test__run_cannibalism(self):
        """test run cannibalism"""

        larva = mk.create_autospec(LarvaTest, spec_set=True)

        with mk.patch.object(cannibalism.Cannibalism, '_cannibalism',
                             autospec=True) as mkCannibalism:
            with mk.patch.object(cannibalism.Cannibalism, '_targets',
                                 autospec=True) as mkTargets:
                # Four time repeat
                mkCannibalism.side_effect = [True, True, True, False]
                self.Cannibalism._run_cannibalism(larva)
                for call in mkCannibalism.call_args_list:
                    self.assertEqual(call,
                                     mk.call(self.Cannibalism,
                                             larva, mkTargets.return_value))
                self.assertEqual(len(mkCannibalism.call_args_list), 4)
                self.assertEqual(mkTargets.call_args_list,
                                 [mk.call(self.Cannibalism, larva)])

                mkTargets.reset_mock()
                mkCannibalism.reset_mock()
                # Three time repeat
                mkCannibalism.side_effect = [True, True, False]
                self.Cannibalism._run_cannibalism(larva)
                for call in mkCannibalism.call_args_list:
                    self.assertEqual(call,
                                     mk.call(self.Cannibalism,
                                             larva, mkTargets.return_value))
                self.assertEqual(len(mkCannibalism.call_args_list), 3)
                self.assertEqual(mkTargets.call_args_list,
                                 [mk.call(self.Cannibalism, larva)])

                mkTargets.reset_mock()
                mkCannibalism.reset_mock()
                # Two time repeat
                mkCannibalism.side_effect = [True, False]
                self.Cannibalism._run_cannibalism(larva)
                for call in mkCannibalism.call_args_list:
                    self.assertEqual(call,
                                     mk.call(self.Cannibalism,
                                             larva, mkTargets.return_value))
                self.assertEqual(len(mkCannibalism.call_args_list), 2)
                self.assertEqual(mkTargets.call_args_list,
                                 [mk.call(self.Cannibalism, larva)])

                mkTargets.reset_mock()
                mkCannibalism.reset_mock()
                # One time repeat
                mkCannibalism.side_effect = [False]
                self.Cannibalism._run_cannibalism(larva)
                for call in mkCannibalism.call_args_list:
                    self.assertEqual(call,
                                     mk.call(self.Cannibalism,
                                             larva, mkTargets.return_value))
                self.assertEqual(len(mkCannibalism.call_args_list), 1)
                self.assertEqual(mkTargets.call_args_list,
                                 [mk.call(self.Cannibalism, larva)])
                
    def test_cannibalism(self):
        """test run cannibalism system"""

        larva = mk.create_autospec(LarvaTest, spec_set=True)

        with mk.patch.object(cannibalism.Cannibalism, '_can_encounter',
                             autospec=True) as mkCan:
            with mk.patch.object(cannibalism.Cannibalism, '_run_cannibalism',
                                 autospec=True) as mkRun:
                mkCan.side_effect = [False, True]

                # Test cannot
                self.Cannibalism.cannibalism(larva)
                self.assertEqual(mkCan.call_args_list,
                                 [mk.call(self.Cannibalism, larva)])
                self.assertEqual(mkRun.call_args_list, [])

                mkCan.reset_mock()
                # Test can
                self.Cannibalism.cannibalism(larva)
                self.assertEqual(mkCan.call_args_list,
                                 [mk.call(self.Cannibalism, larva)])
                self.assertEqual(mkRun.call_args_list,
                                 [mk.call(self.Cannibalism, larva)])

    def test_setup(self):
        """test setup the class"""

        # Test if have the models
        kwargs = {keyword.fight:     self.fight,
                  keyword.encounter: self.encounter,
                  keyword.radius:    self.radius}
        self.Cannibalism = cannibalism.Cannibalism.setup(**kwargs)
        self.assertIsInstance(self.Cannibalism, cannibalism.Cannibalism)
        self.assertEqual(self.Cannibalism.fight,     self.fight)
        self.assertEqual(self.Cannibalism.encounter, self.encounter)
        self.assertEqual(self.Cannibalism.radius,    self.radius)
        self.assertEqual(self.Cannibalism.behavior, keyword.cannibal)

        # Test if have no models
        kwargs = {}
        self.Cannibalism = cannibalism.Cannibalism.setup(**kwargs)
        self.assertIsInstance(self.Cannibalism, cannibalism.Cannibalism)
        self.assertEqual(self.Cannibalism.fight,     None)
        self.assertEqual(self.Cannibalism.encounter, None)
        self.assertEqual(self.Cannibalism.radius,    None)
        self.assertEqual(self.Cannibalism.behavior, keyword.cannibal)
