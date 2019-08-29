import datetime
import dataclasses       as dclass
import numpy             as np
import matplotlib.pyplot as plt

import data.biomass       as input_biomass
import data.data_tracking as input_tracking
import data.forage        as input_forage
import data.graph         as input_graph
import data.movement      as input_move
import data.reproduction  as input_repro

import source.hint    as hint
import source.keyword as keyword

import source.simulation.simulation as main_simulation


# Plotting parameters
num_steps  = 30
num_eggs   = 10
num_larvae = 1000
save_fig   = True



@dclass.dataclass
class Simulator(object):
    """
    Class to setup and run a simulation of only biomass growth:

    Variables:
        nums:   initial population numbers
        forage: the plant forage model
    """

    grid        = [(keyword.hexagon, 1, 1, True),
                   input_graph.graph(25)]
    attrs       = {1: input_tracking.genotype_attrs}
    data        = (np.inf,)
    # steps       = [({keyword.larva:  [keyword.move,
    #                                   keyword.consume]}, 1)]
    steps       = [({keyword.larva: [keyword.move,
                                     keyword.consume]}, 24),
                   ({keyword.larva: [keyword.grow,
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
                    input_forage.starve,
                    input_forage.egg_forage,
                    input_forage.larva_forage,
                    input_forage.loss,
                    input_forage.fight,
                    input_forage.encounter,
                    input_forage.radius,
                    input_move.larva_movement,
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
initial_pops = ((num_eggs,   num_eggs,   num_eggs),
                (num_larvae, num_larvae, num_larvae),
                (0,          0,          0),
                (0,          0,          0),
                (0,          0,          0))
print('{} Running Cannibalism Bt simulations'.
      format(datetime.datetime.now()))
simulator_bt = Simulator(initial_pops, 1)
simulator_bt.run(t)
dataframes_bt = simulator_bt.simulation.agents.dataframes()
egg_bt   = dataframes_bt['(0, 0)_egg']
larva_bt = dataframes_bt['(0, 0)_larva']
print('{} Running Cannibalism Not Bt simulations'.
      format(datetime.datetime.now()))
simulator_not_bt = Simulator(initial_pops, 0)
simulator_not_bt.run(t)
dataframes_not_bt = simulator_not_bt.simulation.agents.dataframes()
egg_not_bt   = dataframes_not_bt['(0, 0)_egg']
larva_not_bt = dataframes_not_bt['(0, 0)_larva']

# Plots
# Not Bt
plt.figure()
egg_not_bt['genotype_resistant'].   plot(color='b', label='Egg Resistant')
egg_not_bt['genotype_heterozygous'].plot(color='r', label='Egg Heterozygous')
egg_not_bt['genotype_susceptible']. plot(color='k', label='Egg Susceptible')

larva_not_bt['genotype_resistant'].   plot(color='b', linestyle='--',
                                           label='Larva Resistant')
larva_not_bt['genotype_heterozygous'].plot(color='r', linestyle='--',
                                           label='Larva Heterozygous')
larva_not_bt['genotype_susceptible']. plot(color='k', linestyle='--',
                                           label='Larva Susceptible')
#       Add plot labels
plt.legend()
plt.xlabel('time (days)')
plt.ylabel('population')
plt.title('Cannibalism on Non-Bt plant')
#       Show/save plot
if save_fig:
    plt.savefig('Cannibalism_not_bt.png')
plt.show()
# Not Bt
plt.figure()
egg_bt['genotype_resistant'].   plot(color='b', label='Egg Resistant')
egg_bt['genotype_heterozygous'].plot(color='r', label='Egg Heterozygous')
egg_bt['genotype_susceptible']. plot(color='k', label='Egg Susceptible')

larva_bt['genotype_resistant'].   plot(color='b', linestyle='--',
                                       label='Larva Resistant')
larva_bt['genotype_heterozygous'].plot(color='r', linestyle='--',
                                       label='Larva Heterozygous')
larva_bt['genotype_susceptible']. plot(color='k', linestyle='--',
                                       label='Larva Susceptible')
#       Add plot labels
plt.legend()
plt.xlabel('time (days)')
plt.ylabel('population')
plt.title('Cannibalism on Bt plant')
#       Show/save plot
if save_fig:
    plt.savefig('Cannibalism_bt.png')
plt.show()
