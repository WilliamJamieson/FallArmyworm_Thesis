import datetime
import dataclasses as dclass

import parameters.data_tracking    as tracking
import parameters.model_parameters as param

import models.graph        as graph
import models.migration    as migration

import source.hint    as hint
import source.keyword as keyword

import source.simulation.simulation as main_simulation


@dclass.dataclass
class Simulator(object):
    """
    Class to setup and run a simulation of only biomass growth:

    Variables:
        nums:    initial population numbers
        bt_prop: bt proportion
    """

    grid        = [graph.graph(param.field_grid),
                   graph.graph(param.plant_grid)]
    attrs       = {0: tracking.genotype_attrs}

    steps = [({keyword.female: [keyword.reproduce,
                                keyword.move],
               keyword.male:   [keyword.move],
               keyword.mated:  [keyword.move],
               keyword.larva:  [keyword.consume,
                                keyword.move]}, param.forage_steps, True),
             ({keyword.female: [keyword.survive,
                                keyword.advance_age,
                                keyword.reset],
               keyword.male: [keyword.survive,
                              keyword.advance_age,
                              keyword.reset],
               keyword.mated: [keyword.survive,
                               keyword.advance_age,
                               keyword.reset],
               keyword.larva: [keyword.grow,
                               keyword.survive,
                               keyword.develop,
                               keyword.advance_age,
                               keyword.reset],
               keyword.pupa: [keyword.survive,
                              keyword.develop,
                              keyword.advance_age],
               keyword.egg: [keyword.survive,
                             keyword.develop,
                             keyword.advance_age],
               keyword.egg_mass: [keyword.reset]},)]

    emigration  = [migration.emigration_adult(param.mean_adult,
                                              param.sigma_adult)]
    immigration = []
    input_variables = param.repro_values
    timesteps       = param.timesteps

    run_number:   int
    nums:         hint.init_pops
    bt_prop:      float
    input_models: list

    path_save: str
    base_save: str

    data:       tuple           = ()
    simulation: hint.simulation = None
    step:       int             = 1

    def __post_init__(self):
        save_name = '{}_{}{}'.format(self.base_save,
                                     self.run_number,
                                     '.sqlite')
        self.data = (100, save_name, self.path_save)

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

    def execute(self) -> None:
        """
        Run the simulation

        """

        start_time = datetime.datetime.now()
        times     = list(range(self.timesteps))
        run_times = times[self.step:].copy()

        for time in run_times:
            self.step = time
            print('     {} Simulation {}, Running step: {}'.
                  format(datetime.datetime.now(), self.run_number, time))
            self.simulation.step()

        print('     {} Simulation {}, Complete Starting save'.
              format(datetime.datetime.now(), self.run_number))
        self.simulation.database.dump(self.simulation)
        end_time = datetime.datetime.now()
        print('Total elapsed time: {}'.format(end_time - start_time))

    @classmethod
    def run(cls, run_number:   int,
                 nums:         hint.init_pops,
                 bt_prop:      float,
                 input_models: list,
                 path_save:    str,
                 base_save:    str) -> None:
        """
        Create and tun the simulation

        Args:
            run_number:    the simulation run id
            nums:          initial population
            bt_prop:       proportion of bt
            input_models:  list of input data
            path_save:     path to save the data
            base_save:     base for saving the data

        Effects:
            runs simulation creating data files
        """

        print('{} Run {} Setting Up Long Time Simulations'.
              format(datetime.datetime.now(), run_number))
        sim = cls(run_number, nums, bt_prop, input_models, path_save, base_save)
        print('{} Run {} Running Long Time Simulations'.
              format(datetime.datetime.now(), run_number))
        sim.execute()
