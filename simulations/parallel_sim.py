import datetime
import dataclasses as dclass

import joblib as para

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
base_save     = 'parallel_sim_25_gen_no_bt_only_resist'

num_simulation = 48
num_cpu        = 16


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
    attrs       = {0: input_tracking.genotype_death_attrs}
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
    run_number: int
    data:       tuple = ()
    simulation: hint.simulation = None

    def __post_init__(self):

        save_name = '{}_{}{}'.format(base_save, self.run_number, '.sqlite')
        self.data = (100, save_name)

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

    def run(self, times: list) -> int:
        """
        Run the simulation for each time

        Args:
            times: the times for the simulation

        Returns:
            biomass data
        """

        for time in times[1:]:
            print('     {} Simulation {}, Running step: {}'.
                  format(datetime.datetime.now(), self.run_number, time))
            self.simulation.step()

        self.simulation.database.dump(self.simulation)

        return self.run_number


def run_simulation(sim_number) -> int:
    """
    Setup and run/save simulation

    Args:
        sim_number: number for simulation

    Returns:
        sim_number
    """

    t            = list(range(num_steps))
    initial_pops = ((0,            0,            0),
                    (0,            0,            0),
                    (0,            0,            0),
                    (0,            0,            0),
                    (num_pregnant, 0,            0))

    print('{} Run {} Setting Up Long Time Simulations'.
          format(datetime.datetime.now(), sim_number))
    simulator = Simulator(initial_pops, 0, sim_number)
    print('{} Run {} Running Long Time Simulations'.
          format(datetime.datetime.now(), sim_number))
    simulator.run(t)

    return sim_number


sim_numbers = para.Parallel(n_jobs=num_cpu)(
    para.delayed(run_simulation)(num) for num in range(num_simulation)
)
