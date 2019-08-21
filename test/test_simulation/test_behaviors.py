import unittest      as ut
import unittest.mock as mk

import dataclasses as dclass

import source.keyword as keyword

import source.biomass.gut  as agent_gut
import source.biomass.mass as agent_mass

import source.development.egg   as agent_develop_egg
import source.development.larva as agent_develop_larva
import source.development.pupa  as agent_develop_pupa

import source.forage.cannibalism as agent_cannibalism
import source.forage.egg         as agent_forage_egg
import source.forage.larva       as agent_forage_larva
import source.forage.plant       as agent_forage_plant

import source.movement.adult as agent_move_adult
import source.movement.larva as agent_move_larva

import source.reproduction.lay  as agent_lay
import source.reproduction.mate as agent_mate

import source.simulation.behaviors as behaviors

import source.survival.adult as agent_survive_adult
import source.survival.egg   as agent_survive_egg
import source.survival.larva as agent_survive_larva
import source.survival.pupa  as agent_survive_pupa


class TestBehaviors(ut.TestCase):
    """test the Behaviors class"""

    def setUp(self):
        """Setup the tests"""

        self.gut  = mk.create_autospec(agent_gut.Gut, spec_set=True)
        self.mass = mk.create_autospec(agent_mass.Mass, spec_set=True)

        self.develop_egg   = mk.create_autospec(agent_develop_egg.Egg,
                                                spec_set=True)
        self.develop_larva = mk.create_autospec(agent_develop_larva.Larva,
                                                spec_set=True)
        self.develop_pupa  = mk.create_autospec(agent_develop_pupa.Pupa,
                                                spec_set=True)

        self.cannibalism  = mk.create_autospec(agent_cannibalism.Cannibalism,
                                               spec_set=True)
        self.forage_egg   = mk.create_autospec(agent_forage_egg.Egg,
                                               spec_set=True)
        self.forage_larva = mk.create_autospec(agent_forage_larva.Larva,
                                               spec_set=True)
        self.forage_plant = mk.create_autospec(agent_forage_plant.Plant,
                                               spec_set=True)

        self.move_adult = mk.create_autospec(agent_move_adult.Adult,
                                             spec_set=True)
        self.move_larva = mk.create_autospec(agent_move_larva.Larva,
                                             spec_set=True)

        self.lay  = mk.create_autospec(agent_lay.Lay, spec_set=True)
        self.mate = mk.create_autospec(agent_mate.Mate, spec_set=True)

        self.survive_adult = mk.create_autospec(agent_survive_adult.Adult,
                                                spec_set=True)
        self.survive_egg   = mk.create_autospec(agent_survive_egg.Egg,
                                                spec_set=True)
        self.survive_larva = mk.create_autospec(agent_survive_larva.Larva,
                                                spec_set=True)
        self.survive_pupa  = mk.create_autospec(agent_survive_pupa.Pupa,
                                                spec_set=True)

        self.Behavior = behaviors.Behaviors(self.gut,
                                            self.mass,
                                            self.develop_egg,
                                            self.develop_larva,
                                            self.develop_pupa,
                                            self.cannibalism,
                                            self.forage_egg,
                                            self.forage_larva,
                                            self.forage_plant,
                                            self.move_adult,
                                            self.move_larva,
                                            self.lay,
                                            self.mate,
                                            self.survive_adult,
                                            self.survive_egg,
                                            self.survive_larva,
                                            self.survive_pupa)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.Behavior, behaviors.Behaviors)

        self.assertEqual(self.Behavior.gut,  self.gut)
        self.assertEqual(self.Behavior.mass, self.mass)

        self.assertEqual(self.Behavior.develop_egg,   self.develop_egg)
        self.assertEqual(self.Behavior.develop_larva, self.develop_larva)
        self.assertEqual(self.Behavior.develop_pupa,  self.develop_pupa)

        self.assertEqual(self.Behavior.cannibalism,  self.cannibalism)
        self.assertEqual(self.Behavior.forage_egg,   self.forage_egg)
        self.assertEqual(self.Behavior.forage_larva, self.forage_larva)
        self.assertEqual(self.Behavior.forage_plant, self.forage_plant)

        self.assertEqual(self.Behavior.move_adult, self.move_adult)
        self.assertEqual(self.Behavior.move_larva, self.move_larva)

        self.assertEqual(self.Behavior.lay,  self.lay)
        self.assertEqual(self.Behavior.mate, self.mate)

        self.assertEqual(self.Behavior.survive_adult, self.survive_adult)
        self.assertEqual(self.Behavior.survive_egg,   self.survive_egg)
        self.assertEqual(self.Behavior.survive_larva, self.survive_larva)
        self.assertEqual(self.Behavior.survive_pupa,  self.survive_pupa)

        self.assertTrue(dclass.is_dataclass(self.Behavior))

    def test_make_biomass(self):
        """test make the biomass behaviors"""

        kwargs = {keyword.max_gut: mk.MagicMock(spec=callable),
                  keyword.growth:  mk.MagicMock(spec=callable)}

        # Already present
        self.Behavior.make_biomass(**kwargs)
        self.assertEqual(self.Behavior.gut,  self.gut)
        self.assertEqual(self.Behavior.mass, self.mass)

        # Not present
        self.Behavior.gut  = None
        self.Behavior.mass = None
        self.Behavior.make_biomass(**kwargs)

        self.assertIsInstance(self.Behavior.gut, agent_gut.Gut)
        self.assertEqual(self.Behavior.gut.max_gut, kwargs[keyword.max_gut])

        self.assertIsInstance(self.Behavior.mass, agent_mass.Mass)
        self.assertEqual(self.Behavior.mass.max_gut, kwargs[keyword.max_gut])
        self.assertEqual(self.Behavior.mass.growth,  kwargs[keyword.growth])

    def test_make_development(self):
        """test make the development behavior"""

        kwargs = {keyword.egg_development:   mk.MagicMock(spec=callable),
                  keyword.larva_development: mk.MagicMock(spec=callable),
                  keyword.pupa_development:  mk.MagicMock(spec=callable)}

        # Already present
        self.Behavior.make_development(**kwargs)
        self.assertEqual(self.Behavior.develop_egg,   self.develop_egg)
        self.assertEqual(self.Behavior.develop_larva, self.develop_larva)
        self.assertEqual(self.Behavior.develop_pupa,  self.develop_pupa)

        # Not present
        self.Behavior.develop_egg   = None
        self.Behavior.develop_larva = None
        self.Behavior.develop_pupa  = None
        self.Behavior.make_development(**kwargs)

        self.assertIsInstance(self.Behavior.develop_egg,
                              agent_develop_egg.Egg)
        self.assertEqual(self.Behavior.develop_egg.development,
                         kwargs[keyword.egg_development])

        self.assertIsInstance(self.Behavior.develop_larva,
                              agent_develop_larva.Larva)
        self.assertEqual(self.Behavior.develop_larva.development,
                         kwargs[keyword.larva_development])

        self.assertIsInstance(self.Behavior.develop_pupa,
                              agent_develop_pupa.Pupa)
        self.assertEqual(self.Behavior.develop_pupa.development,
                         kwargs[keyword.pupa_development])

    def test_make_forage(self):
        """test make forage behaviors"""

        kwargs = {keyword.fight:        mk.MagicMock(spec=callable),
                  keyword.encounter:    mk.MagicMock(spec=callable),
                  keyword.radius:       mk.MagicMock(spec=callable),
                  keyword.egg_forage:   mk.MagicMock(spec=callable),
                  keyword.larva_forage: mk.MagicMock(spec=callable),
                  keyword.plant_forage: mk.MagicMock(spec=callable)}

        # Already present
        self.Behavior.make_forage(**kwargs)
        self.assertEqual(self.Behavior.cannibalism,  self.cannibalism)
        self.assertEqual(self.Behavior.forage_egg,   self.forage_egg)
        self.assertEqual(self.Behavior.forage_larva, self.forage_larva)
        self.assertEqual(self.Behavior.forage_plant, self.forage_plant)

        # Not present
        self.Behavior.cannibalism  = None
        self.Behavior.forage_egg   = None
        self.Behavior.forage_larva = None
        self.Behavior.forage_plant = None
        self.Behavior.make_forage(**kwargs)

        self.assertIsInstance(self.Behavior.cannibalism,
                              agent_cannibalism.Cannibalism)
        self.assertEqual(self.Behavior.cannibalism.fight,
                         kwargs[keyword.fight])
        self.assertEqual(self.Behavior.cannibalism.encounter,
                         kwargs[keyword.encounter])
        self.assertEqual(self.Behavior.cannibalism.radius,
                         kwargs[keyword.radius])

        self.assertIsInstance(self.Behavior.forage_egg,
                              agent_forage_egg.Egg)
        self.assertEqual(self.Behavior.forage_egg.forage,
                         kwargs[keyword.egg_forage])

        self.assertIsInstance(self.Behavior.forage_larva,
                              agent_forage_larva.Larva)
        self.assertEqual(self.Behavior.forage_larva.forage,
                         kwargs[keyword.larva_forage])

        self.assertIsInstance(self.Behavior.forage_plant,
                              agent_forage_plant.Plant)
        self.assertEqual(self.Behavior.forage_plant.forage,
                         kwargs[keyword.plant_forage])

    def test_make_movement(self):
        """test make movement behaviors"""

        kwargs = {keyword.adult_movement: mk.MagicMock(spec=callable),
                  keyword.larva_movement: mk.MagicMock(spec=callable)}

        # Already present
        self.Behavior.make_movement(**kwargs)
        self.assertEqual(self.Behavior.move_adult, self.move_adult)
        self.assertEqual(self.Behavior.move_larva, self.move_larva)

        # Not present
        self.Behavior.move_adult = None
        self.Behavior.move_larva = None
        self.Behavior.make_movement(**kwargs)

        self.assertIsInstance(self.Behavior.move_adult,
                              agent_move_adult.Adult)
        self.assertEqual(self.Behavior.move_adult.movement,
                         kwargs[keyword.adult_movement])

        self.assertIsInstance(self.Behavior.move_larva,
                              agent_move_larva.Larva)
        self.assertEqual(self.Behavior.move_larva.movement,
                         kwargs[keyword.larva_movement])

    def test_make_reproduction(self):
        """test make reproduction behaviors"""

        kwargs = {keyword.trials:      mk.MagicMock(spec=int),
                  keyword.fecundity:   mk.MagicMock(spec=callable),
                  keyword.density:     mk.MagicMock(spec=callable),
                  keyword.mating:      mk.MagicMock(spec=callable),
                  keyword.mate_radius: mk.MagicMock(spec=callable)}

        # Already present
        self.Behavior.make_reproduction(**kwargs)
        self.assertEqual(self.Behavior.lay,  self.lay)
        self.assertEqual(self.Behavior.mate, self.mate)

        # Not present
        self.Behavior.lay  = None
        self.Behavior.mate = None
        self.Behavior.make_reproduction(**kwargs)

        self.assertIsInstance(self.Behavior.lay, agent_lay.Lay)
        self.assertEqual(self.Behavior.lay.trials,
                         kwargs[keyword.trials])
        self.assertEqual(self.Behavior.lay.fecundity,
                         kwargs[keyword.fecundity])
        self.assertEqual(self.Behavior.lay.density,
                         kwargs[keyword.density])

        self.assertIsInstance(self.Behavior.mate, agent_mate.Mate)
        self.assertEqual(self.Behavior.mate.mating,
                         kwargs[keyword.mating])
        self.assertEqual(self.Behavior.mate.radius,
                         kwargs[keyword.mate_radius])

    def test_make_survival(self):
        """test make survival behaviors"""

        kwargs = {keyword.adult_survival: mk.MagicMock(spec=callable),
                  keyword.egg_survival:   mk.MagicMock(spec=callable),
                  keyword.larva_survival: mk.MagicMock(spec=callable),
                  keyword.pupa_survival:  mk.MagicMock(spec=callable)}

        # Already present
        self.Behavior.make_survival(**kwargs)
        self.assertEqual(self.Behavior.survive_adult, self.survive_adult)
        self.assertEqual(self.Behavior.survive_egg,   self.survive_egg)
        self.assertEqual(self.Behavior.survive_larva, self.survive_larva)
        self.assertEqual(self.Behavior.survive_pupa,  self.survive_pupa)

        # Not present
        self.Behavior.survive_adult = None
        self.Behavior.survive_egg   = None
        self.Behavior.survive_larva = None
        self.Behavior.survive_pupa  = None
        self.Behavior.make_survival(**kwargs)

        self.assertIsInstance(self.Behavior.survive_adult,
                              agent_survive_adult.Adult)
        self.assertEqual(self.Behavior.survive_adult.survival,
                         kwargs[keyword.adult_survival])
        self.assertEqual(self.Behavior.survive_adult.behavior,
                         keyword.survival_adult)

        self.assertIsInstance(self.Behavior.survive_egg,
                              agent_survive_egg.Egg)
        self.assertEqual(self.Behavior.survive_egg.survival,
                         kwargs[keyword.egg_survival])
        self.assertEqual(self.Behavior.survive_egg.behavior,
                         keyword.survival_egg)

        self.assertIsInstance(self.Behavior.survive_larva,
                              agent_survive_larva.Larva)
        self.assertEqual(self.Behavior.survive_larva.survival,
                         kwargs[keyword.larva_survival])
        self.assertEqual(self.Behavior.survive_larva.behavior,
                         keyword.survival_larva)

        self.assertIsInstance(self.Behavior.survive_pupa,
                              agent_survive_pupa.Pupa)
        self.assertEqual(self.Behavior.survive_pupa.survival,
                         kwargs[keyword.pupa_survival])
        self.assertEqual(self.Behavior.survive_pupa.behavior,
                         keyword.survival_pupa)

    def test_setup(self):
        """test setup the class"""

        kwargs = {'test': mk.MagicMock()}

        with mk.patch.object(behaviors.Behaviors, 'make_biomass',
                             autospec=True) as mkBiomass:
            with mk.patch.object(behaviors.Behaviors, 'make_development',
                                 autospec=True) as mkDevelopment:
                with mk.patch.object(behaviors.Behaviors, 'make_forage',
                                     autospec=True) as mkForage:
                    with mk.patch.object(behaviors.Behaviors, 'make_movement',
                                         autospec=True) as mkMovement:
                        with mk.patch.object(behaviors.Behaviors,
                                             'make_reproduction',
                                             autospec=True) as mkReproduction:
                            with mk.patch.object(behaviors.Behaviors,
                                                 'make_survival',
                                                 autospec=True) as mkSurvival:
                                self.Behavior = behaviors.Behaviors.\
                                    setup(**kwargs)

                                self.assertIsInstance(self.Behavior,
                                                      behaviors.Behaviors)

                                self.assertEqual(self.Behavior.gut,  None)
                                self.assertEqual(self.Behavior.mass, None)

                                self.assertEqual(self.Behavior.develop_egg,
                                                 None)
                                self.assertEqual(self.Behavior.develop_larva,
                                                 None)
                                self.assertEqual(self.Behavior.develop_pupa,
                                                 None)

                                self.assertEqual(self.Behavior.cannibalism,
                                                 None)
                                self.assertEqual(self.Behavior.forage_egg,
                                                 None)
                                self.assertEqual(self.Behavior.forage_larva,
                                                 None)
                                self.assertEqual(self.Behavior.forage_plant,
                                                 None)

                                self.assertEqual(self.Behavior.move_adult, None)
                                self.assertEqual(self.Behavior.move_larva, None)

                                self.assertEqual(self.Behavior.lay,  None)
                                self.assertEqual(self.Behavior.mate, None)

                                self.assertEqual(self.Behavior.survive_adult,
                                                 None)
                                self.assertEqual(self.Behavior.survive_egg,
                                                 None)
                                self.assertEqual(self.Behavior.survive_larva,
                                                 None)
                                self.assertEqual(self.Behavior.survive_pupa,
                                                 None)

                                self.assertEqual(mkBiomass.call_args_list,
                                                 [mk.call(self.Behavior,
                                                          **kwargs)])
                                self.assertEqual(mkDevelopment.call_args_list,
                                                 [mk.call(self.Behavior,
                                                          **kwargs)])
                                self.assertEqual(mkForage.call_args_list,
                                                 [mk.call(self.Behavior,
                                                          **kwargs)])
                                self.assertEqual(mkMovement.call_args_list,
                                                 [mk.call(self.Behavior,
                                                          **kwargs)])
                                self.assertEqual(mkReproduction.call_args_list,
                                                 [mk.call(self.Behavior,
                                                          **kwargs)])
                                self.assertEqual(mkSurvival.call_args_list,
                                                 [mk.call(self.Behavior,
                                                          **kwargs)])
