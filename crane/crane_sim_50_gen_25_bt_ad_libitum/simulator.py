import datetime

import dataclasses as dclass
import pickle      as pk

import source.hint as hint

import source.simulation.simulation as main_simulation

import crane.crane_sim_50_gen_25_bt_ad_libitum.inputs as inputs


@dclass.dataclass
class Simulator(object):
    """
    Class to setup and run a simulation of only biomass growth:

    Variables:
        nums:   initial population numbers
        forage: the plant forage model
    """

    grid  = inputs.grid
    attrs = inputs.attrs
    steps = inputs.steps

    emigration  = inputs.emigration
    immigration = inputs.immigration

    models    = inputs.models
    variables = inputs.variables
    nums      = inputs.nums
    bt_prop   = inputs.bt_prop
    timesteps = inputs.timesteps
    path_save = inputs.path_save
    base_save = inputs.base_save

    run_number: int
    data:       tuple           = ()
    simulation: hint.simulation = None
    step:       int             = 1

    def __post_init__(self):

        if self.simulation is None:
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
                      *self.models,
                      **self.variables)

    def save(self, step: int):
        """
        Save simulation state for restart

        Args:
            step: step of the save

        Effects:
            write entire simulation to file
        """

        save_name = '{}_{}_step_{}{}'.format(self.base_save,
                                             self.run_number,
                                             step,
                                             '.sim')

        with open(save_name, 'wb') as sim_dump:
            pk.dump(self, sim_dump, protocol=pk.HIGHEST_PROTOCOL)

    def run(self) -> datetime.timedelta:
        """
        Run the simulation for each time

        Returns:
            biomass data
        """

        start_time = datetime.datetime.now()
        # dump_time  = datetime.datetime.now()
        #
        # save_diff = datetime.timedelta(hours=5)
        times     = list(range(self.timesteps))
        run_times = times[self.step:].copy()

        for time in run_times:
            self.step = time
            print('     {} Simulation {}, Running step: {}'.
                  format(datetime.datetime.now(), self.run_number, time))
            self.simulation.step()

            # if (datetime.datetime.now() - dump_time) >= save_diff:
            #     self.save(time)
            #     dump_time = datetime.datetime.now()

        print('     {} Simulation {}, Complete Starting save'.
              format(datetime.datetime.now(), self.run_number))
        self.simulation.database.dump(self.simulation)
        end_time = datetime.datetime.now()

        return end_time - start_time


def run_simulation(sim_number) -> datetime.timedelta:
    """
    Setup and run a simulation

    Args:
        sim_number: simulation number of this run

    Returns:
        time of simulation
    """

    print('{} Run {} Setting Up Long Time Simulations'.
          format(datetime.datetime.now(), sim_number))
    simulator = Simulator(sim_number)
    print('{} Run {} Running Long Time Simulations'.
          format(datetime.datetime.now(), sim_number))
    return simulator.run()
