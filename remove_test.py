import numpy.random as rnd

import joblib as para

import source.hint    as hint
import source.keyword as keyword

import source.simulation.simulation as main_simulation

import source.space.agents as main_agents
import source.space.location as main_location
import source.space.space  as main_space

import source.agents.agent as main_agent


def init_plant(bt: str) -> float:
    return 0


def deactivate(this: hint.agent):
    this.deactivate()

    return this.unique_id


def deactivator(these: hint.agent_list):
    results = []

    for this in these:
        results.append(deactivate(this))

    return results


grid_generators = [(keyword.square, 3, 3, False),
                   (keyword.square, 2, 2, False)]
space = main_space.Space.setup(grid_generators)
agents = main_agents.Agents.empty(space, ['test'], {}, (0, init_plant))

# noinspection PyTypeChecker
simulation = main_simulation.Simulation(space,
                                        agents,
                                        None,
                                        None,
                                        None,
                                        None,
                                        None,
                                        None)

test_agents = [main_agent.Agent('test',
                                str(index),
                                simulation,
                                main_location.Location([0, 0, 0]),
                                True)
               for index in range(1000)]
for agent in test_agents:
    agent.activate()


test_copy     = test_agents.copy()
# rnd.shuffle(test_copy)
remove_agents = test_copy[:100]

n = 4
splits = [remove_agents[i::n] for i in range(n)]

values = para.Parallel(n_jobs=n, require='sharedmem')(para.delayed(deactivator)(agent_list) for agent_list in splits)

current_agents = simulation.agents.agents('test')
for agent in remove_agents:
    assert agent not in current_agents

for agent in test_agents:
    if agent in remove_agents:
        assert agent not in current_agents
    else:
        assert agent in current_agents

# for agent in remove_agents:
#     agent.deactivate()
