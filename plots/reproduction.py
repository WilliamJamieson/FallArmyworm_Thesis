import datetime
import dataclasses       as dclass
import numpy             as np
import matplotlib.pyplot as plt

import data.biomass       as input_biomass
import data.data_tracking as input_tracking
import data.graph         as input_graph
import data.movement      as input_move
import data.reproduction  as input_repro

import source.hint    as hint
import source.keyword as keyword

import source.simulation.simulation as main_simulation


# Plotting parameters
num_steps  = 40
num_eggs   = 10
num_larvae = 1000
num_adults = 20
save_fig   = True


@dclass.dataclass
class Simulator(object):
    """
    Class to setup and run a simulation of only biomass growth:

    Variables:
        nums:   initial population numbers
        forage: the plant forage model
    """

    grid        = [input_graph.graph(25),
                   (keyword.hexagon, 1, 1, True)]
    attrs       = {0: input_tracking.genotype_attrs}
    data        = (np.inf,)
    steps       = [({keyword.female: [keyword.move,
                                      keyword.reproduce],
                     keyword.male:   [keyword.move]}, 2),
                   ({keyword.female: [keyword.advance_age,
                                      keyword.reset],
                     keyword.male:   [keyword.advance_age,
                                      keyword.reset]},)]
    emigration  = []
    immigration = []

    input_models = [input_biomass.max_gut,
                    input_biomass.growth,
                    input_biomass.init_num,
                    input_biomass.init_mass,
                    input_biomass.init_juvenile,
                    input_biomass.init_mature,
                    input_biomass.init_plant,
                    input_move.adult_movement,
                    input_repro.mating,
                    input_repro.mate_radius,
                    input_repro.fecundity,
                    input_repro.density,
                    input_repro.init_sex]
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

    def collect(self) -> int:
        """
        Collect the number of egg_masses

        Returns:
            number of egg_masses
        """

        egg_masses = self.simulation.agents.agents(keyword.egg_mass)

        return len(egg_masses)

    def run(self, times: list) -> list:
        """
        Run the simulation for each time

        Args:
            times: the times for the simulation

        Returns:
            biomass data
        """

        data = [self.collect()]
        for time in times[1:]:
            print('     {} Running step: {}'.
                  format(datetime.datetime.now(), time))
            self.simulation.step()
            data.append(self.collect())

        return data


t            = list(range(num_steps))
initial_pops = ((0,          0,          0),
                (0,          0,          0),
                (0,          0,          0),
                (num_adults, num_adults, num_adults),
                (0,          0,          0))
print('{} Running Reproduction Bt simulations'.
      format(datetime.datetime.now()))
simulator_bt = Simulator(initial_pops, 1)
egg_mass_bt   = simulator_bt.run(t)
dataframes_bt = simulator_bt.simulation.agents.dataframes()
egg_bt = dataframes_bt['(0,)_egg']
print('{} Running Reproduction not Bt simulations'.
      format(datetime.datetime.now()))
simulator_not_bt = Simulator(initial_pops, 0)
egg_mass_not_bt   = simulator_not_bt.run(t)
dataframes_not_bt = simulator_not_bt.simulation.agents.dataframes()
egg_not_bt = dataframes_not_bt['(0,)_egg']


# Plot Number of Egg_mass
plt.figure()
#       Plot the numbers
plt.plot(t, egg_mass_bt,     'b', label='Egg Mass on Bt')
plt.plot(t, egg_mass_not_bt, 'k', label='Egg Mass on not Bt')
#       Add plot labels
plt.legend()
plt.xlabel('time (days)')
plt.ylabel('population')
plt.title('Reproduction of Egg Masses')
#       Show/save plot
if save_fig:
    plt.savefig('Egg_Mass_repro.png')
plt.show()

# Plot eggs on Bt
plt.figure()
#       Plot the eggs on bt
egg_bt['genotype_resistant'].   plot(color='b', label='Egg Resistant')
egg_bt['genotype_heterozygous'].plot(color='r', label='Egg Heterozygous')
egg_bt['genotype_susceptible']. plot(color='k', label='Egg Susceptible')
#       Add plot labels
plt.legend()
plt.xlabel('time (days)')
plt.ylabel('population')
plt.title('Reproduction of Egg on Bt')
#       Show/save plot
if save_fig:
    plt.savefig('Egg_on_Bt_repro.png')
plt.show()

# Plot eggs on not Bt
plt.figure()
#       Plot the eggs on not bt
egg_not_bt['genotype_resistant'].   plot(color='b', label='Egg Resistant')
egg_not_bt['genotype_heterozygous'].plot(color='r', label='Egg Heterozygous')
egg_not_bt['genotype_susceptible']. plot(color='k', label='Egg Susceptible')
#       Add plot labels
plt.legend()
plt.xlabel('time (days)')
plt.ylabel('population')
plt.title('Reproduction of Egg on Not Bt')
#       Show/save plot
if save_fig:
    plt.savefig('Egg_on_not_Bt_repro.png')
plt.show()
