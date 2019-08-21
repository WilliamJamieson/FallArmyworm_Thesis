import unittest      as ut
import unittest.mock as mk

import dataclasses as dclass

import source.keyword as keyword

import source.agents.larva as agent_larva

import source.biomass.mass as mass


class LarvaTest(agent_larva.Larva):
    """Class to add dynamic values for tests"""

    genotype  = mk.MagicMock(spec=str)
    mass      = mk.MagicMock(spec=float)
    plant_gut = mk.MagicMock(spec=float)
    egg_gut   = mk.MagicMock(spec=float)
    larva_gut = mk.MagicMock(spec=float)


class TestMass(ut.TestCase):
    """test the mass system class"""

    def setUp(self):
        """Setup the tests"""

        self.max_gut = mk.MagicMock(spec=callable)
        self.growth  = mk.MagicMock(spec=callable)

        self.Mass = mass.Mass(self.max_gut,
                              self.growth)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.Mass, mass.Mass)

        self.assertEqual(self.Mass.max_gut, self.max_gut)
        self.assertEqual(self.Mass.growth,  self.growth)

        self.assertEqual(self.Mass.behavior, keyword.mass)

        self.assertTrue(dclass.is_dataclass(self.Mass))

    def test__volume(self):
        """test get the volume of the larva"""

        larva = mk.create_autospec(LarvaTest, spec_set=True)

        self.assertEqual(self.Mass._volume(larva),
                         larva.plant_gut.__add__.return_value.
                         __add__.return_value)
        self.assertEqual(larva.plant_gut.__add__.return_value.
                         __add__.call_args_list,
                         [mk.call(larva.larva_gut)])
        self.assertEqual(larva.plant_gut.__add__.call_args_list,
                         [mk.call(larva.egg_gut)])

    def test__ratio(self):
        """test get the ratio of gut volume"""

        larva  = mk.create_autospec(LarvaTest, spec_set=True)
        volume = mk.MagicMock(spec=float)

        with mk.patch.object(mass.Mass, '_volume', autospec=True) as mkVolume:
            mkVolume.return_value = volume

            self.assertEqual(self.Mass._ratio(larva),
                             volume.__truediv__.return_value)
            self.assertEqual(volume.__truediv__.call_args_list,
                             [mk.call(self.max_gut.return_value)])
            self.assertEqual(self.max_gut.call_args_list,
                             [mk.call(larva.mass)])
            self.assertEqual(mkVolume.call_args_list,
                             [mk.call(larva)])

    def test__energy(self):
        """test get the energy for the simulation"""

        larva_mass = mk.MagicMock(spec=float)
        ratio      = mk.MagicMock(spec=float)

        self.assertEqual(self.Mass._energy(larva_mass, ratio),
                         ratio.__mul__.return_value)
        self.assertEqual(ratio.__mul__.call_args_list,
                         [mk.call(self.max_gut.return_value)])
        self.assertEqual(self.max_gut.call_args_list,
                         [mk.call(larva_mass)])

    def test__rhs(self):
        """test get the right hand side of the growth for RH4"""

        larva = mk.create_autospec(LarvaTest, spec_set=True)
        ratio = mk.MagicMock(spec=float)
        shift = mk.MagicMock(spec=float)

        with mk.patch.object(mass.Mass, '_energy', autospec=True) as mkEnergy:
            self.assertEqual(self.Mass._rhs(larva, ratio, shift),
                             self.growth.return_value)
            self.assertEqual(self.growth.call_args_list,
                             [mk.call(larva.mass.__add__.return_value,
                                      mkEnergy.return_value,
                                      larva.genotype)])
            self.assertEqual(mkEnergy.call_args_list,
                             [mk.call(self.Mass,
                                      larva.mass.__add__.return_value,
                                      ratio)])
            self.assertEqual(larva.mass.__add__.call_args_list,
                             [mk.call(shift)])

    def test_grow(self):
        """test get the amount we grow"""

        larva = mk.create_autospec(LarvaTest, spec_set=True)

        ratio = mk.MagicMock(spec=float)

        k1 = mk.MagicMock(spec=float)
        k2 = mk.MagicMock(spec=float)
        k3 = mk.MagicMock(spec=float)
        k4 = mk.MagicMock(spec=float)

        effects = [k1, k2, k3, k4]

        with mk.patch.object(mass.Mass, '_ratio', autospec=True) as mkRatio:
            with mk.patch.object(mass.Mass, '_rhs', autospec=True) as mkRhs:
                mkRatio.return_value = ratio
                mkRhs.side_effect    = effects

                self.assertEqual(self.Mass.grow(larva),
                                 k1.__add__.return_value.
                                    __add__.return_value.
                                    __add__.return_value.
                                    __truediv__.return_value)
                self.assertEqual(k1.__add__.return_value.
                                    __add__.return_value.
                                    __add__.return_value.
                                    __truediv__.call_args_list,
                                 [mk.call(6)])
                self.assertEqual(k1.__add__.return_value.
                                    __add__.return_value.
                                    __add__.call_args_list,
                                 [mk.call(k4)])
                self.assertEqual(k1.__add__.return_value.
                                     __add__.call_args_list,
                                 [mk.call(k3.__mul__.return_value)])
                self.assertEqual(k1.__add__.call_args_list,
                                 [mk.call(k2.__mul__.return_value)])
                self.assertEqual(k2.__mul__.call_args_list,
                                 [mk.call(2)])
                self.assertEqual(k3.__mul__.call_args_list,
                                 [mk.call(2)])

                self.assertEqual(mkRhs.call_args_list,
                                 [mk.call(self.Mass, larva, ratio, 0),
                                  mk.call(self.Mass, larva, ratio,
                                          k1.__truediv__.return_value),
                                  mk.call(self.Mass, larva, ratio,
                                          k2.__truediv__.return_value),
                                  mk.call(self.Mass, larva, ratio, k3)])
                self.assertEqual(k1.__truediv__.call_args_list,
                                 [mk.call(2)])
                self.assertEqual(k2.__truediv__.call_args_list,
                                 [mk.call(2)])
                self.assertEqual(mkRatio.call_args_list,
                                 [mk.call(self.Mass, larva)])

    def test_setup(self):
        """test setup the class"""

        kwargs = {keyword.max_gut: self.max_gut,
                  keyword.growth:  self.growth}

        self.Mass = mass.Mass.setup(**kwargs)
        self.assertIsInstance(self.Mass, mass.Mass)
        self.assertEqual(self.Mass.max_gut, self.max_gut)
        self.assertEqual(self.Mass.growth,  self.growth)
        self.assertEqual(self.Mass.behavior, keyword.mass)
