import datetime
import dataclasses       as dclass
import numpy             as np
import matplotlib.pyplot as plt

import data.biomass       as input_biomass
import data.data_tracking as input_tracking
import data.forage        as input_forage
import data.reproduction  as input_repro
import data.survival      as input_survive

import source.hint    as hint
import source.keyword as keyword

import source.simulation.simulation as main_simulation


# Plotting parameters
num_steps  = 40
num_eggs   = 10
num_larvae = 1000
num_pupae  = 1000
num_adults = 1000
# num_steps  = 40
# num_eggs   = 0
# num_larvae = 200
# num_pupae  = 0
# num_adults = 0
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
    steps       = [({keyword.larva:  [keyword.consume,
                                      keyword.grow,
                                      keyword.survive,
                                      keyword.reset],
                     keyword.egg:    [keyword.survive],
                     keyword.pupa:   [keyword.survive],
                     keyword.female: [keyword.survive]},)]
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
initial_pops = ((num_eggs,   num_eggs,   num_eggs),
                (num_larvae, num_larvae, num_larvae),
                (num_pupae,  num_pupae,  num_pupae),
                (num_adults, num_adults, num_adults),
                (0,          0,          0))
print('{} Running Survival Bt simulations'.format(datetime.datetime.now()))
simulator_bt = Simulator(initial_pops, 1)
start = datetime.datetime.now()
simulator_bt.run(t)
end   = datetime.datetime.now()
print('Run time: {}'.format(end - start))
dataframes_bt = simulator_bt.simulation.agents.dataframes()
egg_bt        = dataframes_bt['(0, 0)_egg']
larva_bt      = dataframes_bt['(0, 0)_larva']
pupa_bt       = dataframes_bt['(0, 0)_pupa']
adult_bt      = dataframes_bt['(0, 0)_female']

print('{} Running Survival not Bt simulations'.format(datetime.datetime.now()))
simulator_not_bt = Simulator(initial_pops, 0)
start = datetime.datetime.now()
simulator_not_bt.run(t)
end   = datetime.datetime.now()
print('Run time: {}'.format(end - start))
dataframes_not_bt = simulator_not_bt.simulation.agents.dataframes()
egg_not_bt        = dataframes_not_bt['(0, 0)_egg']
larva_not_bt      = dataframes_not_bt['(0, 0)_larva']
pupa_not_bt       = dataframes_not_bt['(0, 0)_pupa']
adult_not_bt      = dataframes_not_bt['(0, 0)_female']

#   Plot Egg on not_bt
plt.figure()
#       Plot data
egg_not_bt['genotype_resistant'].   plot(color='b', label='Resistant')
egg_not_bt['genotype_heterozygous'].plot(color='r', label='Heterozygous')
egg_not_bt['genotype_susceptible']. plot(color='k', label='Susceptible')
#       Add plot labels
plt.legend()
plt.xlabel('time (days)')
plt.ylabel('population')
plt.title('Egg Survival on Non-Bt plant')
#       Show/save plot
if save_fig:
    plt.savefig('Egg_not_Bt_survive.png')
plt.show()
#   Plot Egg on Bt
plt.figure()
#       Plot data
egg_bt['genotype_resistant'].   plot(color='b', label='Resistant')
egg_bt['genotype_heterozygous'].plot(color='r', label='Heterozygous')
egg_bt['genotype_susceptible']. plot(color='k', label='Susceptible')
#       Add plot labels
plt.legend()
plt.xlabel('time (days)')
plt.ylabel('population')
plt.title('Egg Survival on Bt plant')
#       Show/save plot
if save_fig:
    plt.savefig('Egg_Bt_survive.png')
plt.show()

#   Plot Larva on not_bt
plt.figure()
#       Plot data
larva_not_bt['genotype_resistant'].   plot(color='b', label='Resistant')
larva_not_bt['genotype_heterozygous'].plot(color='r', label='Heterozygous')
larva_not_bt['genotype_susceptible']. plot(color='k', label='Susceptible')
#       Add plot labels
plt.legend()
plt.xlabel('time (days)')
plt.ylabel('population')
plt.title('Larva Survival on Non-Bt plant')
#       Show/save plot
if save_fig:
    plt.savefig('Larva_not_Bt_survive.png')
plt.show()
#   Plot Larva on Bt
plt.figure()
#       Plot data
larva_bt['genotype_resistant'].   plot(color='b', label='Resistant')
larva_bt['genotype_heterozygous'].plot(color='r', label='Heterozygous')
larva_bt['genotype_susceptible']. plot(color='k', label='Susceptible')
#       Add plot labels
plt.legend()
plt.xlabel('time (days)')
plt.ylabel('population')
plt.title('Larva Survival on Bt plant')
#       Show/save plot
if save_fig:
    plt.savefig('Larva_Bt_survive.png')
plt.show()

#   Plot Pupa on not_bt
plt.figure()
#       Plot data
pupa_not_bt['genotype_resistant'].   plot(color='b', label='Resistant')
pupa_not_bt['genotype_heterozygous'].plot(color='r', label='Heterozygous')
pupa_not_bt['genotype_susceptible']. plot(color='k', label='Susceptible')
#       Add plot labels
plt.legend()
plt.xlabel('time (days)')
plt.ylabel('population')
plt.title('Pupa Survival on Non-Bt plant')
#       Show/save plot
if save_fig:
    plt.savefig('Pupa_not_Bt_survive.png')
plt.show()
#   Plot Pupa on Bt
plt.figure()
#       Plot data
pupa_bt['genotype_resistant'].   plot(color='b', label='Resistant')
pupa_bt['genotype_heterozygous'].plot(color='r', label='Heterozygous')
pupa_bt['genotype_susceptible']. plot(color='k', label='Susceptible')
#       Add plot labels
plt.legend()
plt.xlabel('time (days)')
plt.ylabel('population')
plt.title('Pupa Survival on Bt plant')
#       Show/save plot
if save_fig:
    plt.savefig('Pupa_Bt_survive.png')
plt.show()

#   Plot Adult on not_bt
plt.figure()
#       Plot data
adult_not_bt['genotype_resistant'].   plot(color='b', label='Resistant')
adult_not_bt['genotype_heterozygous'].plot(color='r', label='Heterozygous')
adult_not_bt['genotype_susceptible']. plot(color='k', label='Susceptible')
#       Add plot labels
plt.legend()
plt.xlabel('time (days)')
plt.ylabel('population')
plt.title('Adult Survival on Non-Bt plant')
#       Show/save plot
if save_fig:
    plt.savefig('Adult_not_Bt_survive.png')
plt.show()
#   Plot Adult on Bt
plt.figure()
#       Plot data
adult_bt['genotype_resistant'].   plot(color='b', label='Resistant')
adult_bt['genotype_heterozygous'].plot(color='r', label='Heterozygous')
adult_bt['genotype_susceptible']. plot(color='k', label='Susceptible')
#       Add plot labels
plt.legend()
plt.xlabel('time (days)')
plt.ylabel('population')
plt.title('Adult Survival on Bt plant')
#       Show/save plot
if save_fig:
    plt.savefig('Adult_Bt_survive.png')
plt.show()
