import unittest      as ut
import unittest.mock as mk

import dataclasses   as dclass
import scipy.stats   as stats
import scipy.special as spcl
import numpy         as np
import numpy.random  as rnd

import source.keyword as keyword

import source.biomass.models as biomass

import source.forage.models as model

import source.simulation.models as models


class TestPlantBase(ut.TestCase):
    """test the PlantBase mathematical model"""

    def setUp(self):
        """Setup the tests"""

        self.PlantBase = model.PlantBase()

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.PlantBase, models.Model)
        self.assertIsInstance(self.PlantBase, model.PlantBase)

        self.assertEqual(self.PlantBase.model_key, keyword.plant_forage)

        self.assertTrue(dclass.is_dataclass(self.PlantBase))

    def test___call__(self):
        """test call the model"""

        mass     = mk.MagicMock(spec=float)
        plant    = mk.MagicMock(spec=float)
        genotype = mk.MagicMock(spec=str)
        bt       = mk.MagicMock(spec=str)

        self.assertIsNone(self.PlantBase(mass, plant, genotype, bt))


class TestPlantAdLibitum(ut.TestCase):
    """test the PlantAdLibitum mathematical model"""

    def setUp(self):
        """Setup the tests"""

        self.max_gut = mk.MagicMock(spec=biomass.MaxGut)

        self.PlantAdLibitum = model.PlantAdLibitum(self.max_gut)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.PlantAdLibitum, models.Model)
        self.assertIsInstance(self.PlantAdLibitum, model.PlantBase)
        self.assertIsInstance(self.PlantAdLibitum, model.PlantAdLibitum)

        self.assertEqual(self.PlantAdLibitum.max_gut, self.max_gut)

        self.assertEqual(self.PlantAdLibitum.model_key, keyword.plant_forage)

        self.assertTrue(dclass.is_dataclass(self.PlantAdLibitum))

    def test___call__(self):
        """test call the model"""

        mass     = mk.MagicMock(spec=float)
        plant    = mk.MagicMock(spec=float)
        genotype = mk.MagicMock(spec=str)
        bt       = mk.MagicMock(spec=str)

        self.assertEqual(self.PlantAdLibitum(mass, plant, genotype, bt),
                         self.max_gut.return_value.__mul__.return_value)
        self.assertEqual(self.max_gut.return_value.__mul__.call_args_list,
                         [mk.call(5)])
        self.assertEqual(self.max_gut.call_args_list,
                         [mk.call(mass)])
        
        
class TestPlantStarve(ut.TestCase):
    """test PlantStarve mathematical model"""

    def setUp(self):
        """Setup the tests"""

        self.mu      = mk.MagicMock(spec=float)
        self.sigma   = mk.MagicMock(spec=float)
        self.max_gut = mk.MagicMock(spec=biomass.MaxGut)

        self.PlantStarve = model.PlantStarve(self.mu,
                                             self.sigma,
                                             self.max_gut)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.PlantStarve, models.Model)
        self.assertIsInstance(self.PlantStarve, model.PlantBase)
        self.assertIsInstance(self.PlantStarve, model.PlantStarve)

        self.assertEqual(self.PlantStarve.mu,      self.mu)
        self.assertEqual(self.PlantStarve.sigma,   self.sigma)
        self.assertEqual(self.PlantStarve.max_gut, self.max_gut)

        self.assertEqual(self.PlantStarve.model_key, keyword.plant_forage)

        self.assertTrue(dclass.is_dataclass(self.PlantStarve))

    def test__lower(self):
        """test get the lower bound"""

        self.assertEqual(self.PlantStarve._lower(),
                         self.mu.__neg__.return_value.__truediv__.return_value)
        self.assertEqual(self.mu.__neg__.return_value.
                            __truediv__.call_args_list,
                         [mk.call(self.sigma)])
        self.assertEqual(self.mu.__neg__.call_args_list,
                         [mk.call()])

    def test__upper(self):
        """test get the upper bound"""

        self.assertEqual(self.PlantStarve._upper(),
                         self.mu.__rsub__.return_value.__truediv__.return_value)
        self.assertEqual(self.mu.__rsub__.return_value.
                            __truediv__.call_args_list,
                         [mk.call(self.sigma)])
        self.assertEqual(self.mu.__rsub__.call_args_list,
                         [mk.call(1)])

    def test__sample(self):
        """test sample the distribution"""

        with mk.patch.object(model.PlantStarve, '_lower',
                             autospec=True) as mkLower:
            with mk.patch.object(model.PlantStarve, '_upper',
                                 autospec=True) as mkUpper:
                with mk.patch.object(stats.truncnorm, 'rvs',
                                     autospec=True) as mkRVS:
                    self.assertEqual(self.PlantStarve._sample(),
                                     mkRVS.return_value)
                    self.assertEqual(mkRVS.call_args_list,
                                     [mk.call(mkLower.return_value,
                                              mkUpper.return_value,
                                              loc=self.mu,
                                              scale=self.sigma)])
                    self.assertEqual(mkLower.call_args_list,
                                     [mk.call(self.PlantStarve)])
                    self.assertEqual(mkUpper.call_args_list,
                                     [mk.call(self.PlantStarve)])

    def test___call__(self):
        """test call the model"""

        mass     = mk.MagicMock(spec=float)
        plant    = mk.MagicMock(spec=float)
        genotype = mk.MagicMock(spec=str)
        bt       = mk.MagicMock(spec=str)

        gut_mass = mk.MagicMock(spec=float)
        self.max_gut.return_value = gut_mass

        gut_mass.__le__.side_effect = [True, False]

        with mk.patch.object(model.PlantStarve, '_sample',
                             autospec=True) as mkSample:
            with mk.patch.object(model, 'float') as mkFloat:
                # Test return gut mass
                self.assertEqual(self.PlantStarve(mass, plant, genotype, bt),
                                 mkFloat.return_value)
                self.assertEqual(mkFloat.call_args_list,
                                 [mk.call(mkSample.return_value.
                                            __mul__.return_value)])
                self.assertEqual(mkSample.return_value.__mul__.call_args_list,
                                 [mk.call(gut_mass)])
                self.assertEqual(mkSample.call_args_list,
                                 [mk.call(self.PlantStarve)])
                self.assertEqual(self.max_gut.call_args_list,
                                 [mk.call(mass)])
                self.assertEqual(gut_mass.__le__.call_args_list,
                                 [mk.call(plant)])

                mkFloat.reset_mock()
                mkSample.reset_mock()
                self.max_gut.reset_mock()
                # Test return plant
                self.assertEqual(self.PlantStarve(mass, plant, genotype, bt),
                                 mkFloat.return_value)
                self.assertEqual(mkFloat.call_args_list,
                                 [mk.call(mkSample.return_value.
                                          __mul__.return_value)])
                self.assertEqual(mkSample.return_value.__mul__.call_args_list,
                                 [mk.call(plant)])
                self.assertEqual(mkSample.call_args_list,
                                 [mk.call(self.PlantStarve)])
                self.assertEqual(self.max_gut.call_args_list,
                                 [mk.call(mass)])
                self.assertEqual(gut_mass.__le__.call_args_list,
                                 [mk.call(plant)])


class TestEgg(ut.TestCase):
    """test Egg forage mathematical model"""

    def setUp(self):
        """Setup the tests"""

        self.factor = mk.MagicMock(spec=float)

        self.Egg = model.Egg(self.factor)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.Egg, models.Model)
        self.assertIsInstance(self.Egg, model.Egg)

        self.assertEqual(self.Egg.factor, self.factor)

        self.assertEqual(self.Egg.model_key, keyword.egg_forage)

        self.assertTrue(dclass.is_dataclass(self.Egg))

    def test___call__(self):
        """test call the class"""

        egg_mass = mk.MagicMock(spec=float)
        mass     = mk.MagicMock(spec=float)
        genotype = mk.MagicMock(spec=str)

        self.assertEqual(self.Egg(egg_mass, mass, genotype),
                         self.factor.__mul__.return_value)
        self.assertEqual(self.factor.__mul__.call_args_list,
                         [mk.call(egg_mass)])


class TestLarva(ut.TestCase):
    """test Larva forage mathematical model"""

    def setUp(self):
        """Setup the tests"""

        self.factor = mk.MagicMock(spec=float)

        self.Larva = model.Larva(self.factor)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.Larva, models.Model)
        self.assertIsInstance(self.Larva, model.Larva)

        self.assertEqual(self.Larva.factor, self.factor)

        self.assertEqual(self.Larva.model_key, keyword.larva_forage)

        self.assertTrue(dclass.is_dataclass(self.Larva))

    def test___call__(self):
        """test call the class"""

        target_mass = mk.MagicMock(spec=float)
        mass        = mk.MagicMock(spec=float)
        genotype    = mk.MagicMock(spec=str)

        self.assertEqual(self.Larva(target_mass, mass, genotype),
                         self.factor.__mul__.return_value)
        self.assertEqual(self.factor.__mul__.call_args_list,
                         [mk.call(target_mass)])


class TestLoss(ut.TestCase):
    """test target Loss mathematical model"""

    def setUp(self):
        """Setup the tests"""

        self.slope = mk.MagicMock(spec=dict)
        self.mid   = mk.MagicMock(spec=dict)

        self.max_gut      = mk.MagicMock(spec=biomass.MaxGut)
        self.forage_egg   = mk.MagicMock(spec=model.Egg)
        self.forage_larva = mk.MagicMock(spec=model.Larva)

        self.Loss = model.Loss(self.slope,
                               self.mid,
                               self.max_gut,
                               self.forage_egg,
                               self.forage_larva)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.Loss, models.Model)
        self.assertIsInstance(self.Loss, model.Loss)

        self.assertEqual(self.Loss.slope,        self.slope)
        self.assertEqual(self.Loss.mid,          self.mid)
        self.assertEqual(self.Loss.max_gut,      self.max_gut)
        self.assertEqual(self.Loss.forage_egg,   self.forage_egg)
        self.assertEqual(self.Loss.forage_larva, self.forage_larva)

        self.assertEqual(self.Loss.model_key, keyword.loss)

        self.assertTrue(dclass.is_dataclass(self.Loss))
        
    def test__diff(self):
        """test find the difference in food and gut"""

        mass        = mk.MagicMock(spec=float)
        target_mass = mk.MagicMock(spec=float)
        genotype    = mk.MagicMock(spec=str)

        # Is egg mass
        self.assertEqual(self.Loss._diff(mass, target_mass, genotype,
                                         keyword.egg_mass),
                         self.forage_egg.return_value.__sub__.return_value)
        self.assertEqual(self.forage_egg.return_value.__sub__.call_args_list,
                         [mk.call(self.max_gut.return_value)])
        self.assertEqual(self.forage_egg.call_args_list,
                         [mk.call(target_mass, mass, genotype)])
        self.assertEqual(self.max_gut.call_args_list,
                         [mk.call(mass)])
        self.assertEqual(self.forage_larva.call_args_list, [])

        self.forage_egg.reset_mock()
        self.max_gut.reset_mock()
        # Is larva
        self.assertEqual(self.Loss._diff(mass, target_mass, genotype,
                                         keyword.larva),
                         self.forage_larva.return_value.__sub__.return_value)
        self.assertEqual(self.forage_larva.return_value.__sub__.call_args_list,
                         [mk.call(self.max_gut.return_value)])
        self.assertEqual(self.forage_larva.call_args_list,
                         [mk.call(target_mass, mass, genotype)])
        self.assertEqual(self.max_gut.call_args_list,
                         [mk.call(mass)])
        self.assertEqual(self.forage_egg.call_args_list, [])

    def test__prob(self):
        """test find the probability"""

        mass        = mk.MagicMock(spec=float)
        target_mass = mk.MagicMock(spec=float)
        genotype    = mk.MagicMock(spec=str)
        target_key  = mk.MagicMock(spec=str)

        with mk.patch.object(model.Loss, '_diff', autospec=True) as mkDiff:
            with mk.patch.object(np, 'exp') as mkExp:
                self.assertEqual(self.Loss._prob(mass, target_mass,
                                                 genotype, target_key),
                                 self.mid.__getitem__.return_value.
                                    __mul__.return_value.
                                    __add__.return_value.
                                    __rtruediv__.return_value)
                self.assertEqual(self.mid.__getitem__.return_value.
                                    __mul__.return_value.
                                    __add__.return_value.
                                    __rtruediv__.call_args_list,
                                  [mk.call(1)])
                self.assertEqual(self.mid.__getitem__.return_value.
                                    __mul__.return_value.
                                    __add__.call_args_list,
                                 [mk.call(1)])
                self.assertEqual(self.mid.__getitem__.return_value.
                                    __mul__.call_args_list,
                                 [mk.call(mkExp.return_value)])
                self.assertEqual(self.mid.__getitem__.call_args_list,
                                 [mk.call(target_key)])
                self.assertEqual(mkExp.call_args_list,
                                 [mk.call(self.slope.__getitem__.return_value.
                                            __neg__.return_value.
                                            __mul__.return_value)])
                self.assertEqual(self.slope.__getitem__.return_value.
                                    __neg__.return_value.
                                    __mul__.call_args_list,
                                 [mk.call(mkDiff.return_value)])
                self.assertEqual(self.slope.__getitem__.return_value.
                                    __neg__.call_args_list,
                                 [mk.call()])
                self.assertEqual(self.slope.__getitem__.call_args_list,
                                 [mk.call(target_key)])
                self.assertEqual(mkDiff.call_args_list,
                                 [mk.call(self.Loss, mass, target_mass,
                                          genotype, target_key)])

    def test___call__(self):
        """test call the model"""

        mass        = mk.MagicMock(spec=float)
        target_mass = mk.MagicMock(spec=float)
        genotype    = mk.MagicMock(spec=str)
        target_key  = mk.MagicMock(spec=str)

        with mk.patch.object(model.Loss, '_prob', autospec=True) as mkProb:
            with mk.patch.object(rnd, 'random') as mkRND:
                mkRND.return_value.__le__.side_effect = [True, False]

                # test true
                self.assertTrue(self.Loss(mass, target_mass, genotype, target_key))
                self.assertEqual(mkRND.return_value.__le__.call_args_list,
                                 [mk.call(mkProb.return_value)])
                self.assertEqual(mkRND.call_args_list,
                                 [mk.call()])
                self.assertEqual(mkProb.call_args_list,
                                 [mk.call(self.Loss, mass, target_mass,
                                          genotype, target_key)])

                mkRND.reset_mock()
                mkProb.reset_mock()
                # test false
                self.assertFalse(self.Loss(mass, target_mass, genotype, target_key))
                self.assertEqual(mkRND.return_value.__le__.call_args_list,
                                 [mk.call(mkProb.return_value)])
                self.assertEqual(mkRND.call_args_list,
                                 [mk.call()])
                self.assertEqual(mkProb.call_args_list,
                                 [mk.call(self.Loss, mass, target_mass,
                                          genotype, target_key)])


class TestFight(ut.TestCase):
    """test Fight mathematical model"""

    def setUp(self):
        """Setup the tests"""

        self.slope = mk.MagicMock(spec=float)

        self.Fight = model.Fight(self.slope)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.Fight, models.Model)
        self.assertIsInstance(self.Fight, model.Fight)

        self.assertEqual(self.Fight.slope, self.slope)

        self.assertEqual(self.Fight.model_key, keyword.fight)

        self.assertTrue(dclass.is_dataclass(self.Fight))

    def test__prob(self):
        """test get the probability"""

        mass0 = mk.MagicMock(spec=float)
        mass1 = mk.MagicMock(spec=float)

        with mk.patch.object(spcl, 'expit', autospec=True) as mkExpit:
            self.assertEqual(self.Fight._prob(mass0, mass1),
                             mkExpit.return_value)
            self.assertEqual(mkExpit.call_args_list,
                             [mk.call(self.slope.__mul__.return_value)])
            self.assertEqual(self.slope.__mul__.call_args_list,
                             [mk.call(mass0.__sub__.return_value)])
            self.assertEqual(mass0.__sub__.call_args_list,
                             [mk.call(mass1)])

    def test___call__(self):
        """test __call__ the model"""

        mass0 = mk.MagicMock(spec=float)
        mass1 = mk.MagicMock(spec=float)

        with mk.patch.object(model.Fight, '_prob', autospec=True) as mkProb:
            with mk.patch.object(rnd, 'random') as mkRND:
                mkRND.return_value.__le__.side_effect = [True, False]

                # Test True
                self.assertTrue(self.Fight(mass0, mass1))
                self.assertEqual(mkRND.return_value.__le__.call_args_list,
                                 [mk.call(mkProb.return_value)])
                self.assertEqual(mkRND.call_args_list,
                                 [mk.call()])
                self.assertEqual(mkProb.call_args_list,
                                 [mk.call(self.Fight, mass0, mass1)])

                mkRND.reset_mock()
                mkProb.reset_mock()
                # Test False
                self.assertFalse(self.Fight(mass0, mass1))
                self.assertEqual(mkRND.return_value.__le__.call_args_list,
                                 [mk.call(mkProb.return_value)])
                self.assertEqual(mkRND.call_args_list,
                                 [mk.call()])
                self.assertEqual(mkProb.call_args_list,
                                 [mk.call(self.Fight, mass0, mass1)])


class TestEncounter(ut.TestCase):
    """test Encounter mathematical model"""

    def setUp(self):
        """Setup the tests"""

        self.factor = mk.MagicMock(spec=float)

        self.Encounter = model.Encounter(self.factor)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.Encounter, models.Model)
        self.assertIsInstance(self.Encounter, model.Encounter)

        self.assertEqual(self.Encounter.factor, self.factor)

        self.assertEqual(self.Encounter.model_key, keyword.encounter)

        self.assertTrue(dclass.is_dataclass(self.Encounter))

    def test__prob(self):
        """test get probability"""

        number = mk.MagicMock(spec=int)

        with mk.patch.object(np, 'exp', autospec=True) as mkExp:
            self.assertEqual(self.Encounter._prob(number),
                             mkExp.return_value.__rsub__.return_value)
            self.assertEqual(mkExp.return_value.__rsub__.call_args_list,
                             [mk.call(1)])
            self.assertEqual(mkExp.call_args_list,
                             [mk.call(self.factor.__neg__.return_value.
                                        __mul__.return_value)])
            self.assertEqual(self.factor.__neg__.return_value.
                                __mul__.call_args_list,
                             [mk.call(number)])
            self.assertEqual(self.factor.__neg__.call_args_list,
                             [mk.call()])

    def test___call__(self):
        """test call the model"""

        number   = mk.MagicMock(spec=int)
        mass     = mk.MagicMock(spec=float)
        genotype = mk.MagicMock(spec=str)

        with mk.patch.object(model.Encounter, '_prob', autospec=True) as mkProb:
            with mk.patch.object(rnd, 'random') as mkRND:
                mkRND.return_value.__le__.side_effect = [True, False]

                # Test True
                self.assertTrue(self.Encounter(number, mass, genotype))
                self.assertEqual(mkRND.return_value.__le__.call_args_list,
                                 [mk.call(mkProb.return_value)])
                self.assertEqual(mkRND.call_args_list,
                                 [mk.call()])
                self.assertEqual(mkProb.call_args_list,
                                 [mk.call(self.Encounter, number)])

                mkRND.reset_mock()
                mkProb.reset_mock()
                # Test False
                self.assertFalse(self.Encounter(number, mass, genotype))
                self.assertEqual(mkRND.return_value.__le__.call_args_list,
                                 [mk.call(mkProb.return_value)])
                self.assertEqual(mkRND.call_args_list,
                                 [mk.call()])
                self.assertEqual(mkProb.call_args_list,
                                 [mk.call(self.Encounter, number)])


class TestRadius(ut.TestCase):
    """test Radius mathematical model"""

    def setUp(self):
        """Setup the tests"""

        self.radius = mk.MagicMock(spec=int)

        self.Radius = model.Radius(self.radius)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.Radius, models.Model)
        self.assertIsInstance(self.Radius, model.Radius)

        self.assertEqual(self.Radius.radius, self.radius)

        self.assertEqual(self.Radius.model_key, keyword.radius)

        self.assertTrue(dclass.is_dataclass(self.Radius))

    def test___call__(self):
        """test call the model"""

        mass     = mk.MagicMock(spec=float)
        genotype = mk.MagicMock(spec=str)

        self.assertEqual(self.Radius(mass, genotype), self.radius)
