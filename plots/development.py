import datetime
import dataclasses       as dclass
import numpy             as np
import matplotlib.pyplot as plt

import data.biomass       as input_biomass
import data.data_tracking as input_tracking
import data.development   as input_develop
import data.forage        as input_forage
import data.reproduction  as input_repro

import source.hint    as hint
import source.keyword as keyword

import source.simulation.simulation as main_simulation


# Plotting parameters
num_steps  = 60
num_eggs   = 10
num_larvae = 1000
num_pupae  = 1000
save_fig   = True


sex_model = input_repro.init_sex
sex_model.prob = 1.0


@dclass.dataclass
class Simulator(object):
    """
    Class to setup and run a simulation of only biomass growth:

    Variables:
        nums:   initial population numbers
        forage: the plant forage model
    """

    grid        = [(keyword.hexagon, 1, 1, True),
                   (keyword.hexagon, 1, 1, True)]
    attrs       = {1: input_tracking.genotype_attrs}
    data        = (np.inf,)
    # steps       = [({keyword.larva:  [keyword.consume,
    #                                   keyword.grow,
    #                                   keyword.develop,
    #                                   keyword.reset],
    #                  keyword.egg:    [keyword.develop],
    #                  keyword.pupa:   [keyword.develop]},)]
    emigration  = []
    immigration = []

    input_models = [input_biomass.max_gut,
                    input_biomass.growth,
                    input_biomass.init_num,
                    input_biomass.init_mass,
                    input_biomass.init_juvenile,
                    input_biomass.init_mature,
                    input_biomass.init_plant,
                    input_forage.ad_libitum,
                    sex_model,
                    input_develop.egg_development,
                    input_develop.larva_development,
                    input_develop.pupa_development]
    input_variables = input_repro.values

    nums:       hint.init_pops
    bt_prop:    float
    steps:      hint.step_tuples
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
                (0,          0,          0),
                (0,          0,          0),
                (0,          0,          0),
                (0,          0,          0))
steps_egg = [({keyword.egg: [keyword.develop,
                             keyword.advance_age]},)]
print('{} Running Development Egg Bt simulations'.
      format(datetime.datetime.now()))
simulator_egg_bt = Simulator(initial_pops, 1, steps_egg)
simulator_egg_bt.run(t)
dataframes_egg_bt = simulator_egg_bt.simulation.agents.dataframes()
egg_egg_bt   = dataframes_egg_bt['(0, 0)_egg']
egg_larva_bt = dataframes_egg_bt['(0, 0)_larva']
print('{} Running Development Egg Not Bt simulations'.
      format(datetime.datetime.now()))
simulator_egg_not_bt = Simulator(initial_pops, 0, steps_egg)
simulator_egg_not_bt.run(t)
dataframes_egg_not_bt = simulator_egg_not_bt.simulation.agents.dataframes()
egg_egg_not_bt   = dataframes_egg_not_bt['(0, 0)_egg']
egg_larva_not_bt = dataframes_egg_not_bt['(0, 0)_larva']

#   Plot Egg on Not Bt
plt.figure()
#       Plot data
egg_egg_not_bt['genotype_resistant'].   plot(color='b',
                                             label='Egg Resistant')
egg_egg_not_bt['genotype_heterozygous'].plot(color='r',
                                             label='Egg Heterozygous')
egg_egg_not_bt['genotype_susceptible']. plot(color='k',
                                             label='Egg Susceptible')

egg_larva_not_bt['genotype_resistant'].   plot(color='b', linestyle='--',
                                               label='Larva Resistant')
egg_larva_not_bt['genotype_heterozygous'].plot(color='r', linestyle='--',
                                               label='Larva Heterozygous')
egg_larva_not_bt['genotype_susceptible']. plot(color='k', linestyle='--',
                                               label='Larva Susceptible')
#       Add plot labels
plt.legend()
plt.xlabel('time (days)')
plt.ylabel('population')
plt.title('Egg Development on Non-Bt plant')
#       Show/save plot
if save_fig:
    plt.savefig('Egg_not_Bt_develop.png')
plt.show()
#   Plot Egg on Bt
plt.figure()
#       Plot data
egg_egg_bt['genotype_resistant'].   plot(color='b',
                                         label='Egg Resistant')
egg_egg_bt['genotype_heterozygous'].plot(color='r',
                                         label='Egg Heterozygous')
egg_egg_bt['genotype_susceptible']. plot(color='k',
                                         label='Egg Susceptible')

egg_larva_bt['genotype_resistant'].   plot(color='b', linestyle='--',
                                           label='Larva Resistant')
egg_larva_bt['genotype_heterozygous'].plot(color='r', linestyle='--',
                                           label='Larva Heterozygous')
egg_larva_bt['genotype_susceptible']. plot(color='k', linestyle='--',
                                           label='Larva Susceptible')
#       Add plot labels
plt.legend()
plt.xlabel('time (days)')
plt.ylabel('population')
plt.title('Egg Development on Bt plant')
#       Show/save plot
if save_fig:
    plt.savefig('Egg_Bt_survive.png')
plt.show()

initial_pops = ((0,          0,          0),
                (num_larvae, num_larvae, num_larvae),
                (0,          0,          0),
                (0,          0,          0),
                (0,          0,          0))
steps_larva = [({keyword.larva:  [keyword.consume,
                                  keyword.grow,
                                  keyword.develop,
                                  keyword.advance_age,
                                  keyword.reset]},)]
print('{} Running Development Larva Bt simulations'.
      format(datetime.datetime.now()))
simulator_larva_bt = Simulator(initial_pops, 1, steps_larva)
simulator_larva_bt.run(t)
dataframes_larva_bt = simulator_larva_bt.simulation.agents.dataframes()
larva_larva_bt = dataframes_larva_bt['(0, 0)_larva']
larva_pupa_bt  = dataframes_larva_bt['(0, 0)_pupa']
print('{} Running Development Larva Not Bt simulations'.
      format(datetime.datetime.now()))
simulator_larva_not_bt = Simulator(initial_pops, 0, steps_larva)
simulator_larva_not_bt.run(t)
dataframes_larva_not_bt = simulator_larva_not_bt.simulation.agents.dataframes()
larva_larva_not_bt = dataframes_larva_not_bt['(0, 0)_larva']
larva_pupa_not_bt  = dataframes_larva_not_bt['(0, 0)_pupa']

#   Plot Larva on Not Bt
plt.figure()
#       Plot data
larva_larva_not_bt['genotype_resistant'].   plot(color='b',
                                                 label='Larva Resistant')
larva_larva_not_bt['genotype_heterozygous'].plot(color='r',
                                                 label='Larva Heterozygous')
larva_larva_not_bt['genotype_susceptible']. plot(color='k',
                                                 label='Larva Susceptible')

larva_pupa_not_bt['genotype_resistant'].   plot(color='b', linestyle='--',
                                                label='Pupa Resistant')
larva_pupa_not_bt['genotype_heterozygous'].plot(color='r', linestyle='--',
                                                label='Pupa Heterozygous')
larva_pupa_not_bt['genotype_susceptible']. plot(color='k', linestyle='--',
                                                label='Pupa Susceptible')
#       Add plot labels
plt.legend()
plt.xlabel('time (days)')
plt.ylabel('population')
plt.title('Larva Development on Non-Bt plant')
#       Show/save plot
if save_fig:
    plt.savefig('Larva_not_Bt_develop.png')
plt.show()
#   Plot Larva on Bt
plt.figure()
#       Plot data
larva_larva_bt['genotype_resistant'].   plot(color='b',
                                             label='Larva Resistant')
larva_larva_bt['genotype_heterozygous'].plot(color='r',
                                             label='Larva Heterozygous')
larva_larva_bt['genotype_susceptible']. plot(color='k',
                                             label='Larva Susceptible')

larva_pupa_bt['genotype_resistant'].   plot(color='b', linestyle='--',
                                            label='Pupa Resistant')
larva_pupa_bt['genotype_heterozygous'].plot(color='r', linestyle='--',
                                            label='Pupa Heterozygous')
larva_pupa_bt['genotype_susceptible']. plot(color='k', linestyle='--',
                                            label='Pupa Susceptible')
#       Add plot labels
plt.legend()
plt.xlabel('time (days)')
plt.ylabel('population')
plt.title('Larva Development on Bt plant')
#       Show/save plot
if save_fig:
    plt.savefig('Larva_Bt_survive.png')
plt.show()

initial_pops = ((0,          0,          0),
                (0,          0,          0),
                (num_pupae, num_pupae, num_pupae),
                (0,          0,          0),
                (0,          0,          0))
steps_pupa = [({keyword.pupa:  [keyword.develop,
                                keyword.advance_age]},)]
print('{} Running Development Pupa Bt simulations'.
      format(datetime.datetime.now()))
simulator_pupa_bt = Simulator(initial_pops, 1, steps_pupa)
simulator_pupa_bt.run(t)
dataframes_pupa_bt = simulator_pupa_bt.simulation.agents.dataframes()
pupa_pupa_bt  = dataframes_pupa_bt['(0, 0)_pupa']
pupa_adult_bt = dataframes_pupa_bt['(0, 0)_female']
print('{} Running Development Pupa Not Bt simulations'.
      format(datetime.datetime.now()))
simulator_pupa_not_bt = Simulator(initial_pops, 0, steps_pupa)
simulator_pupa_not_bt.run(t)
dataframes_pupa_not_bt = simulator_pupa_not_bt.simulation.agents.dataframes()
pupa_pupa_not_bt  = dataframes_pupa_not_bt['(0, 0)_pupa']
pupa_adult_not_bt = dataframes_pupa_not_bt['(0, 0)_female']

#   Plot Pupa on Not Bt
plt.figure()
#       Plot data
pupa_pupa_not_bt['genotype_resistant'].   plot(color='b',
                                                 label='Pupa Resistant')
pupa_pupa_not_bt['genotype_heterozygous'].plot(color='r',
                                                 label='Pupa Heterozygous')
pupa_pupa_not_bt['genotype_susceptible']. plot(color='k',
                                                 label='Pupa Susceptible')

pupa_adult_not_bt['genotype_resistant'].   plot(color='b', linestyle='--',
                                                label='Adult Resistant')
pupa_adult_not_bt['genotype_heterozygous'].plot(color='r', linestyle='--',
                                                label='Adult Heterozygous')
pupa_adult_not_bt['genotype_susceptible']. plot(color='k', linestyle='--',
                                                label='Adult Susceptible')
#       Add plot labels
plt.legend()
plt.xlabel('time (days)')
plt.ylabel('population')
plt.title('Pupa Development on Non-Bt plant')
#       Show/save plot
if save_fig:
    plt.savefig('Pupa_not_Bt_develop.png')
plt.show()
#   Plot Pupa on Bt
plt.figure()
#       Plot data
pupa_pupa_bt['genotype_resistant'].   plot(color='b',
                                             label='Pupa Resistant')
pupa_pupa_bt['genotype_heterozygous'].plot(color='r',
                                             label='Pupa Heterozygous')
pupa_pupa_bt['genotype_susceptible']. plot(color='k',
                                             label='Pupa Susceptible')

pupa_adult_bt['genotype_resistant'].   plot(color='b', linestyle='--',
                                            label='Adult Resistant')
pupa_adult_bt['genotype_heterozygous'].plot(color='r', linestyle='--',
                                            label='Adult Heterozygous')
pupa_adult_bt['genotype_susceptible']. plot(color='k', linestyle='--',
                                            label='Adult Susceptible')
#       Add plot labels
plt.legend()
plt.xlabel('time (days)')
plt.ylabel('population')
plt.title('Pupa Development on Bt plant')
#       Show/save plot
if save_fig:
    plt.savefig('Pupa_Bt_survive.png')
plt.show()

initial_pops = ((num_eggs,   num_eggs,   num_eggs),
                (0,          0,          0),
                (0,          0,          0),
                (0,          0,          0),
                (0,          0,          0))
steps_full = [({keyword.egg:   [keyword.develop,
                                keyword.advance_age],
                keyword.larva: [keyword.consume,
                                keyword.grow,
                                keyword.develop,
                                keyword.advance_age,
                                keyword.reset],
                keyword.pupa:  [keyword.develop,
                                keyword.advance_age]},)]
print('{} Running Development Full Bt simulations'.
      format(datetime.datetime.now()))
simulator_full_bt = Simulator(initial_pops, 1, steps_full)
start = datetime.datetime.now()
simulator_full_bt.run(t)
end = datetime.datetime.now()
bt_time = end - start
print('Elapsed time: {}'.format(bt_time))
dataframes_full_bt = simulator_full_bt.simulation.agents.dataframes()
full_egg_bt   = dataframes_full_bt['(0, 0)_egg']
full_larva_bt = dataframes_full_bt['(0, 0)_larva']
full_pupa_bt  = dataframes_full_bt['(0, 0)_pupa']
full_adult_bt = dataframes_full_bt['(0, 0)_female']
print('{} Running Development Full Not Bt simulations'.
      format(datetime.datetime.now()))
simulator_full_not_bt = Simulator(initial_pops, 0, steps_full)
start = datetime.datetime.now()
simulator_full_not_bt.run(t)
end = datetime.datetime.now()
not_bt_time = end - start
print('Elapsed time: {}'.format(not_bt_time))
dataframes_full_not_bt = simulator_full_not_bt.simulation.agents.dataframes()
full_egg_not_bt   = dataframes_full_not_bt['(0, 0)_egg']
full_larva_not_bt = dataframes_full_not_bt['(0, 0)_larva']
full_pupa_not_bt  = dataframes_full_not_bt['(0, 0)_pupa']
full_adult_not_bt = dataframes_full_not_bt['(0, 0)_female']

#   Plot Pupa on Not Bt
plt.figure()
#       Plot data
full_egg_not_bt['genotype_resistant'].   plot(color='b',
                                              label='Egg Resistant')
full_egg_not_bt['genotype_heterozygous'].plot(color='r',
                                              label='Egg Heterozygous')
full_egg_not_bt['genotype_susceptible']. plot(color='k',
                                              label='Egg Susceptible')

full_larva_not_bt['genotype_resistant'].   plot(color='b', linestyle='dotted',
                                                label='Larva Resistant')
full_larva_not_bt['genotype_heterozygous'].plot(color='r', linestyle='dotted',
                                                label='Larva Heterozygous')
full_larva_not_bt['genotype_susceptible']. plot(color='k', linestyle='dotted',
                                                label='Larva Susceptible')

full_pupa_not_bt['genotype_resistant'].   plot(color='b', linestyle='dashed',
                                               label='Pupa Resistant')
full_pupa_not_bt['genotype_heterozygous'].plot(color='r', linestyle='dashed',
                                               label='Pupa Heterozygous')
full_pupa_not_bt['genotype_susceptible']. plot(color='k', linestyle='dashed',
                                               label='Pupa Susceptible')

full_adult_not_bt['genotype_resistant'].   plot(color='b', linestyle='dashdot',
                                                label='Adult Resistant')
full_adult_not_bt['genotype_heterozygous'].plot(color='r', linestyle='dashdot',
                                                label='Adult Heterozygous')
full_adult_not_bt['genotype_susceptible']. plot(color='k', linestyle='dashdot',
                                                label='Adult Susceptible')
#       Add plot labels
plt.legend()
plt.xlabel('time (days)')
plt.ylabel('population')
plt.title('Full Development on Non-Bt plant')
#       Show/save plot
if save_fig:
    plt.savefig('Full_not_Bt_develop.png')
plt.show()

#   Plot Pupa on Bt
plt.figure()
#       Plot data
full_egg_bt['genotype_resistant'].   plot(color='b',
                                          label='Egg Resistant')
full_egg_bt['genotype_heterozygous'].plot(color='r',
                                          label='Egg Heterozygous')
full_egg_bt['genotype_susceptible']. plot(color='k',
                                          label='Egg Susceptible')

full_larva_bt['genotype_resistant'].   plot(color='b', linestyle='dotted',
                                            label='Larva Resistant')
full_larva_bt['genotype_heterozygous'].plot(color='r', linestyle='dotted',
                                            label='Larva Heterozygous')
full_larva_bt['genotype_susceptible']. plot(color='k', linestyle='dotted',
                                            label='Larva Susceptible')

full_pupa_bt['genotype_resistant'].   plot(color='b', linestyle='dashed',
                                           label='Pupa Resistant')
full_pupa_bt['genotype_heterozygous'].plot(color='r', linestyle='dashed',
                                           label='Pupa Heterozygous')
full_pupa_bt['genotype_susceptible']. plot(color='k', linestyle='dashed',
                                           label='Pupa Susceptible')

full_adult_bt['genotype_resistant'].   plot(color='b', linestyle='dashdot',
                                            label='Adult Resistant')
full_adult_bt['genotype_heterozygous'].plot(color='r', linestyle='dashdot',
                                            label='Adult Heterozygous')
full_adult_bt['genotype_susceptible']. plot(color='k', linestyle='dashdot',
                                            label='Adult Susceptible')
#       Add plot labels
plt.legend()
plt.xlabel('time (days)')
plt.ylabel('population')
plt.title('Full Development on Bt plant')
#       Show/save plot
if save_fig:
    plt.savefig('Full_Bt_develop.png')
plt.show()
