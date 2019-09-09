import datetime
import dataclasses as dclass

import data.biomass       as input_biomass
import data.data_tracking as input_tracking
import data.development   as input_develop
import data.forage        as input_forage
import data.graph         as input_graph
import data.migration     as input_mig
import data.movement      as input_move
import data.reproduction  as input_repro
import data.survival      as input_survive

import source.hint    as hint
import source.keyword as keyword

import source.simulation.simulation as main_simulation


# Plotting parameters
num_steps     = 1800
num_pregnant  = 100
save_fig      = True


@dclass.dataclass
class Simulator(object):
    """
    Class to setup and run a simulation of only biomass growth:

    Variables:
        nums:   initial population numbers
        forage: the plant forage model
    """

    grid        = [input_graph.graph(25),
                   input_graph.graph(10)]
    attrs       = {0: input_tracking.genotype_attrs}
    data        = (50, 'long_sim_25_gen_no_im_bt_10_no_hetero.sqlite')
    steps       = [({keyword.female:   [keyword.move,
                                        keyword.reproduce],
                     keyword.male:     [keyword.move],
                     keyword.mated:    [keyword.move],
                     keyword.larva:    [keyword.move,
                                        keyword.consume]}, 24, True),
                   ({keyword.female:   [keyword.survive,
                                        keyword.advance_age,
                                        keyword.reset],
                     keyword.male:     [keyword.survive,
                                        keyword.advance_age,
                                        keyword.reset],
                     keyword.mated:    [keyword.survive,
                                        keyword.advance_age,
                                        keyword.reset],
                     keyword.larva:    [keyword.grow,
                                        keyword.survive,
                                        keyword.develop,
                                        keyword.advance_age,
                                        keyword.reset],
                     keyword.pupa:     [keyword.survive,
                                        keyword.develop,
                                        keyword.advance_age],
                     keyword.egg:      [keyword.survive,
                                        keyword.develop,
                                        keyword.advance_age],
                     keyword.egg_mass: [keyword.reset]},)]
    emigration  = [input_mig.emigration_adult]
    # immigration = [input_mig.immigration_adult_homo_r,
    #                input_mig.immigration_adult_homo_s,
    #                input_mig.immigration_adult_hetero]
    immigration  = []

    input_models = [input_biomass.max_gut,
                    input_biomass.growth,
                    input_biomass.init_num,
                    input_biomass.init_mass,
                    input_biomass.init_juvenile,
                    input_biomass.init_mature,
                    input_biomass.init_plant,
                    input_develop.egg_development,
                    input_develop.larva_development,
                    input_develop.pupa_development,
                    input_forage.starve,
                    input_forage.egg_forage,
                    input_forage.larva_forage,
                    input_forage.loss,
                    input_forage.fight,
                    input_forage.encounter,
                    input_forage.radius,
                    input_move.adult_movement,
                    input_move.larva_movement,
                    input_repro.mating,
                    input_repro.mate_radius,
                    input_repro.fecundity,
                    input_repro.density,
                    input_repro.init_sex,
                    input_survive.egg_survival,
                    input_survive.larva_survival,
                    input_survive.pupa_survival,
                    input_survive.adult_survival]
    input_variables = input_repro.values

    nums:       hint.init_pops
    bt_prop:    float
    simulation: hint.simulation = None

    def __post_init__(self):

        self.simulation = main_simulation.Simulation. \
            setup(self.nums,
                  self.grid,
                  self.attrs,
                  self.data,
                  self.bt_prop,
                  self.steps,
                  self.emigration,
                  self.immigration,
                  *self.input_models,
                  **self.input_variables)

    def run(self, times: list) -> None:
        """
        Run the simulation for each time

        Args:
            times: the times for the simulation

        Returns:
            biomass data
        """

        for time in times[1:]:
            print('     {} Running step: {}'.
                  format(datetime.datetime.now(), time))
            self.simulation.step()


t            = list(range(num_steps))
initial_pops = ((0,            0,            0),
                (0,            0,            0),
                (0,            0,            0),
                (0,            0,            0),
                (num_pregnant, 0,            num_pregnant))
print('{} Setting Up Long Time Simulations'.
      format(datetime.datetime.now()))
simulator = Simulator(initial_pops, 0.1)
print('{} Running Long Time Simulations'.
      format(datetime.datetime.now()))
simulator.run(t)
