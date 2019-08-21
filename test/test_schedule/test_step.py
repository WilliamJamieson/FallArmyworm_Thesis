import unittest      as ut
import unittest.mock as mk

import collections  as collect
import itertools    as i_tools
import numpy.random as rnd

import source.agents.agent as main_agent

import source.schedule.actions as agent_actions
import source.schedule.step    as step

import source.space.agents   as main_agents
import source.space.location as location
import source.space.space    as agent_space


class ActionsTest(agent_actions.Actions):
    """Class to add dynamic values for tests"""

    agent_key = mk.MagicMock(spec=str)


class SpaceTest(agent_space.Space):
    """Class to add dynamic values for tests"""

    location_keys = mk.MagicMock(spec=dict)


class AgentParallel(main_agent.Agent):
    """Class to contain a basic agent for parallel"""

    def __init__(self, agent_key, unique_id, loc):
        super().__init__(agent_key, unique_id, None, loc, True)

        self.results0 = [mk.MagicMock() for _ in range(3)]
        self.results1 = [mk.MagicMock() for _ in range(3)]
        self.results2 = [mk.MagicMock() for _ in range(3)]

    def test0(self) -> list:
        """Test action to perform"""

        return self.results0

    def test1(self) -> list:
        """Test action to perform"""

        return self.results1

    def test2(self) -> list:
        """Test action to perform"""

        return self.results2


class TestStep(ut.TestCase):
    """test Step class"""

    def setUp(self):
        """Setup the tests"""

        self.actions = [mk.create_autospec(ActionsTest, spec_set=True)
                        for _ in range(3)]

        self.number       = mk.MagicMock(spec=int)
        self.shuffle      = mk.MagicMock(spec=bool)
        self.parallel_reg = mk.MagicMock(spec=bool)
        self.parallel_loc = mk.MagicMock(spec=bool)
        self.level        = mk.MagicMock(spec=int)

        self.Step = step.Step(self.actions,
                              self.number,
                              self.shuffle,
                              self.parallel_reg,
                              self.parallel_loc,
                              self.level)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.Step, collect.UserList)
        self.assertIsInstance(self.Step, step.Step)

        self.assertEqual(self.Step.number,       self.number)
        self.assertEqual(self.Step.shuffle,      self.shuffle)
        self.assertEqual(self.Step.parallel_reg, self.parallel_reg)
        self.assertEqual(self.Step.parallel_loc, self.parallel_loc)
        self.assertEqual(self.Step.level,        self.level)

        self.assertEqual(self.Step,      self.actions)
        self.assertEqual(self.Step.data, self.actions)
        
    def test__perform_agent_action_regular(self):
        """test perform an action in regular state"""

        action = mk.create_autospec(ActionsTest, spec_set=True)
        agents = [mk.create_autospec(main_agent.Agent, spec_set=True)
                  for _ in range(3)]

        results = []
        effects = []
        for _ in agents:
            result = [mk.MagicMock() for _ in range(3)]
            effects.append(result)
            results.extend(result)
        action.perform.side_effect = effects

        self.assertEqual(self.Step._perform_agent_action_regular(action,
                                                                 agents),
                         results)
        for index, call in enumerate(action.perform.call_args_list):
            self.assertEqual(call,
                             mk.call(agents[index]))
        self.assertEqual(len(action.perform.call_args_list), 3)
        
    def test__perform_agent_action_parallel(self):
        """test perform an action in parallel state"""

        loc = mk.create_autospec(location.Location, spec_set=True)

        agent = AgentParallel('test', 0, loc)

        action0 = agent_actions.Action('test0')
        self.assertEqual(action0.perform(agent), agent.results0)
        action1 = agent_actions.Action('test1')
        self.assertEqual(action1.perform(agent), agent.results1)
        action2 = agent_actions.Action('test2')
        self.assertEqual(action2.perform(agent), agent.results2)

        results_i_tools = list(i_tools.chain.from_iterable([agent.results0,
                                                            agent.results1,
                                                            agent.results2]))
        results  = []
        results += agent.results0
        results += agent.results1
        results += agent.results2
        self.assertEqual(results, results_i_tools)

        actions = agent_actions.Actions([action0, action1, action2], 'test')
        self.assertEqual(actions.perform(agent), results)

        agents = [AgentParallel('test', index, loc) for index in range(40)]
        regular_results  = self.Step._perform_agent_action_regular( actions,
                                                                    agents)
        self.assertEqual(len(regular_results), 40 * 9)
        parallel_results = self.Step._perform_agent_action_parallel(actions,
                                                                    agents)
        self.assertEqual(regular_results, parallel_results)

    def test__perform_agent_action(self):
        """test perform action on agent_bin"""

        action    = mk.create_autospec(ActionsTest, spec_set=True)
        agent_bin = mk.create_autospec(main_agents.AgentsBin, spec_set=True)
        agents    = [mk.create_autospec(main_agent.Agent, spec_set=True)
                     for _ in range(3)]

        agent_bin.__getitem__.return_value = agents

        with mk.patch.object(step.Step, '_perform_agent_action_parallel',
                             autospec=True) as mkParallel:
            with mk.patch.object(step.Step,
                                 '_perform_agent_action_regular') as mkRegular:
                with mk.patch.object(rnd, 'shuffle') as mkRnd:
                    # Test run parallel
                    self.Step.parallel_reg = True
                    self.assertEqual(self.Step._perform_agent_action(action,
                                                                     agent_bin),
                                     mkParallel.return_value)
                    self.assertEqual(mkParallel.call_args_list,
                                     [mk.call(self.Step, action, agents)])
                    self.assertEqual(mkRegular.call_args_list, [])
                    self.assertEqual(agent_bin.__getitem__.call_args_list,
                                     [mk.call(action.agent_key)])
                    self.assertEqual(mkRnd.call_args_list,
                                     [mk.call(agents)])

                    mkRnd.reset_mock()
                    mkParallel.reset_mock()
                    agent_bin.reset_mock()
                    # Test run regular
                    self.Step.parallel_reg = False
                    self.assertEqual(self.Step._perform_agent_action(action,
                                                                     agent_bin),
                                     mkRegular.return_value)
                    self.assertEqual(mkRegular.call_args_list,
                                     [mk.call(action, agents)])
                    self.assertEqual(mkParallel.call_args_list, [])
                    self.assertEqual(agent_bin.__getitem__.call_args_list,
                                     [mk.call(action.agent_key)])
                    self.assertEqual(mkRnd.call_args_list,
                                     [mk.call(agents)])
                    
    def test__perform_actions_step(self):
        """test perform actions at each location"""

        location_key = mk.MagicMock(spec=str)

        agents    = mk.create_autospec(main_agents.Agents, spec_set=True)
        agent_bin = mk.create_autospec(main_agents.AgentsBin, spec_set=True)
        agents.__getitem__.return_value = agent_bin

        results = []
        effects = []
        for _ in self.actions:
            result = [mk.MagicMock() for _ in range(3)]
            effects.append(result)
            results.extend(result)

        with mk.patch.object(step.Step, '_perform_agent_action',
                             autospec=True) as mkPerform:
            mkPerform.side_effect = effects

            self.assertEqual(self.Step._perform_actions_step(location_key,
                                                             agents),
                             results)

            for index, call in enumerate(mkPerform.call_args_list):
                self.assertEqual(call,
                                 mk.call(self.Step,
                                         self.actions[index], agent_bin))
            for index, action in enumerate(self.actions):
                self.assertEqual(mkPerform.call_args_list[index],
                                 mk.call(self.Step, action, agent_bin))
            self.assertEqual(len(mkPerform.call_args_list), 3)

            self.assertEqual(agents.__getitem__.call_args_list,
                             [mk.call(location_key)])

    def test__perform_regular_step(self):
        """test perform a regular step"""

        location_keys = [mk.MagicMock(spec=str) for _ in range(3)]
        agents        = mk.create_autospec(main_agents.Agents, spec_set=True)

        results = []
        effects = []
        for _ in self.actions:
            result = [mk.MagicMock() for _ in range(3)]
            effects.append(result)
            results.extend(result)

        with mk.patch.object(step.Step, '_perform_actions_step',
                             autospec=True) as mkPerform:
            mkPerform.side_effect = effects

            self.assertEqual(self.Step._perform_regular_step(location_keys,
                                                             agents),
                             results)

            for index, call in enumerate(mkPerform.call_args_list):
                self.assertEqual(call,
                                 mk.call(self.Step,
                                         location_keys[index], agents))
            for index, location_key in enumerate(location_keys):
                self.assertEqual(mkPerform.call_args_list[index],
                                 mk.call(self.Step,
                                         location_key, agents))
            self.assertEqual(len(mkPerform.call_args_list), 3)

    def test__perform_parallel_step(self):
        """test perform a parallel step"""

        locations     = []
        location_keys = []
        for index in range(40):
            loc = location.Location([0, index])
            locations.    append(loc)
            location_keys.append(loc.location_key)

        locs = locations.copy()
        locs.append(location.Location([0]))
        agent_keys = ['test0', 'test1', 'test2']
        agents     = main_agents.Agents.empty(locs, agent_keys, {})

        unique_id = 0
        for loc in locations:
            for agent_key in agent_keys:
                for _ in range(3):
                    agent = AgentParallel(agent_key, unique_id, loc)
                    agents.activate(agent)
                    unique_id += 1
        for agent_key in agent_keys:
            self.assertEqual(len(agents.agents(agent_key)), 120)
            for location_key in location_keys:
                self.assertEqual(len(agents[location_key][agent_key]), 3)

        action_keys = ['test0', 'test1', 'test2']
        actions = []
        for agent_key in agent_keys:
            action = agent_actions.Actions.setup(agent_key, action_keys)
            actions.append(action)

        self.Step = step.Step(actions)

        regular_results = self.Step._perform_regular_step(location_keys,
                                                          agents)
        self.assertEqual(len(regular_results), 40 * 3 * 3 * 9)
        parallel_results = self.Step._perform_parallel_step(location_keys,
                                                            agents)
        self.assertEqual(len(regular_results), len(parallel_results))
        set_regular = set(regular_results)
        self.assertEqual(len(regular_results), len(set_regular))
        set_parallel = set(parallel_results)
        self.assertEqual(len(parallel_results), len(set_parallel))
        self.assertEqual(set_regular, set_parallel)

    def test__perform_step(self):
        """test perform a single set of actions"""

        space         = mk.create_autospec(SpaceTest, spec_set=True)
        agents        = mk.create_autospec(main_agents.Agents, spec_set=True)
        location_keys = [mk.MagicMock(spec=str) for _ in range(3)]
        
        space.location_keys.__getitem__.return_value = location_keys

        with mk.patch.object(step.Step, '_perform_parallel_step',
                             autospec=True) as mkParallel:
            with mk.patch.object(step.Step, '_perform_regular_step',
                                 autospec=True) as mkRegular:
                with mk.patch.object(rnd, 'shuffle') as mkRnd:
                    # Parallel No shuffle
                    self.Step.shuffle      = False
                    self.Step.parallel_loc = True
                    self.assertEqual(self.Step._perform_step(space, agents),
                                     mkParallel.return_value)
                    self.assertEqual(mkParallel.call_args_list,
                                     [mk.call(self.Step,
                                              location_keys, agents)])
                    self.assertEqual(mkRegular.call_args_list, [])
                    self.assertEqual(space.location_keys.
                                        __getitem__.call_args_list,
                                     [mk.call(self.level)])
                    self.assertEqual(mkRnd.call_args_list, [])

                    mkParallel.reset_mock()
                    space.location_keys.__getitem__.reset_mock()
                    # Parallel With  shuffle
                    self.Step.shuffle      = True
                    self.Step.parallel_loc = True
                    self.assertEqual(self.Step._perform_step(space, agents),
                                     mkParallel.return_value)
                    self.assertEqual(mkParallel.call_args_list,
                                     [mk.call(self.Step,
                                              location_keys, agents)])
                    self.assertEqual(mkRegular.call_args_list, [])
                    self.assertEqual(space.location_keys.
                                     __getitem__.call_args_list,
                                     [mk.call(self.level)])
                    self.assertEqual(mkRnd.call_args_list,
                                     [mk.call(self.Step)])

                    mkParallel.reset_mock()
                    space.location_keys.__getitem__.reset_mock()
                    mkRnd.reset_mock()
                    # No Parallel No shuffle
                    self.Step.shuffle      = False
                    self.Step.parallel_loc = False
                    self.assertEqual(self.Step._perform_step(space, agents),
                                     mkRegular.return_value)
                    self.assertEqual(mkRegular.call_args_list,
                                     [mk.call(self.Step,
                                              location_keys, agents)])
                    self.assertEqual(mkParallel.call_args_list, [])
                    self.assertEqual(space.location_keys.
                                     __getitem__.call_args_list,
                                     [mk.call(self.level)])
                    self.assertEqual(mkRnd.call_args_list, [])

                    mkRegular.reset_mock()
                    space.location_keys.__getitem__.reset_mock()
                    # No Parallel With  shuffle
                    self.Step.shuffle      = True
                    self.Step.parallel_loc = False
                    self.assertEqual(self.Step._perform_step(space, agents),
                                     mkRegular.return_value)
                    self.assertEqual(mkRegular.call_args_list,
                                     [mk.call(self.Step,
                                              location_keys, agents)])
                    self.assertEqual(mkParallel.call_args_list, [])
                    self.assertEqual(space.location_keys.
                                     __getitem__.call_args_list,
                                     [mk.call(self.level)])
                    self.assertEqual(mkRnd.call_args_list,
                                     [mk.call(self.Step)])

    def test_perform(self):
        """test perform the step"""

        space  = mk.create_autospec(SpaceTest, spec_set=True)
        agents = mk.create_autospec(main_agents.Agents, spec_set=True)

        results = []
        effects = []
        for _ in self.actions:
            result = [mk.MagicMock() for _ in range(3)]
            effects.append(result)
            results.extend(result)

        self.Step.number = 3
        with mk.patch.object(step.Step, '_perform_step',
                             autospec=True) as mkPerform:
            mkPerform.side_effect = effects

            self.assertEqual(self.Step.perform(space,
                                               agents),
                             results)

            for index, call in enumerate(mkPerform.call_args_list):
                self.assertEqual(call,
                                 mk.call(self.Step,
                                         space, agents))
            self.assertEqual(len(mkPerform.call_args_list), 3)

    def test_setup(self):
        """test setup the class"""

        actions = {}
        for _ in range(3):
            agent_key   = mk.MagicMock(spec=str)
            action_keys = [mk.MagicMock(spec=str) for _ in range(3)]

            actions[agent_key] = action_keys

        # Test default
        self.Step = step.Step.setup(actions)
        self.assertIsInstance(self.Step, step.Step)
        self.assertEqual(self.Step.number,       1)
        self.assertEqual(self.Step.shuffle,      False)
        self.assertEqual(self.Step.parallel_reg, False)
        self.assertEqual(self.Step.parallel_loc, False)
        self.assertEqual(self.Step.level,        0)

        for index_i, thing in enumerate(actions.items()):
            agent_key, action_keys = thing
            self.assertIsInstance(self.Step[index_i], agent_actions.Actions)
            self.assertEqual(self.Step[index_i].agent_key, agent_key)

            for index_j, action in enumerate(action_keys):
                self.assertIsInstance(self.Step[index_i][index_j],
                                      agent_actions.Action)
                self.assertEqual(self.Step[index_i][index_j].action, action)
            for index_j, action in enumerate(self.Step[index_i]):
                self.assertIsInstance(action, agent_actions.Action)
                self.assertEqual(action.action, action_keys[index_j])
            self.assertEqual(len(self.Step[index_i]), 3)
        self.assertEqual(len(self.Step), 3)

        # Test Not Default
        self.Step = step.Step.setup(actions,
                                    self.number,
                                    self.shuffle,
                                    self.parallel_reg,
                                    False,
                                    self.level)
        self.assertIsInstance(self.Step, step.Step)
        self.assertEqual(self.Step.number,       self.number)
        self.assertEqual(self.Step.shuffle,      self.shuffle)
        self.assertEqual(self.Step.parallel_reg, self.parallel_reg)
        self.assertEqual(self.Step.parallel_loc, False)
        self.assertEqual(self.Step.level,        self.level)

        for index_i, thing in enumerate(actions.items()):
            agent_key, action_keys = thing
            self.assertIsInstance(self.Step[index_i], agent_actions.Actions)
            self.assertEqual(self.Step[index_i].agent_key, agent_key)

            for index_j, action in enumerate(action_keys):
                self.assertIsInstance(self.Step[index_i][index_j],
                                      agent_actions.Action)
                self.assertEqual(self.Step[index_i][index_j].action, action)
            for index_j, action in enumerate(self.Step[index_i]):
                self.assertIsInstance(action, agent_actions.Action)
                self.assertEqual(action.action, action_keys[index_j])
            self.assertEqual(len(self.Step[index_i]), 3)
        self.assertEqual(len(self.Step), 3)

        # Test Not Default
        self.Step = step.Step.setup(actions,
                                    self.number,
                                    self.shuffle,
                                    False,
                                    self.parallel_loc,
                                    self.level)
        self.assertIsInstance(self.Step, step.Step)
        self.assertEqual(self.Step.number,       self.number)
        self.assertEqual(self.Step.shuffle,      self.shuffle)
        self.assertEqual(self.Step.parallel_reg, False)
        self.assertEqual(self.Step.parallel_loc, self.parallel_loc)
        self.assertEqual(self.Step.level,        self.level)

        for index_i, thing in enumerate(actions.items()):
            agent_key, action_keys = thing
            self.assertIsInstance(self.Step[index_i], agent_actions.Actions)
            self.assertEqual(self.Step[index_i].agent_key, agent_key)

            for index_j, action in enumerate(action_keys):
                self.assertIsInstance(self.Step[index_i][index_j],
                                      agent_actions.Action)
                self.assertEqual(self.Step[index_i][index_j].action, action)
            for index_j, action in enumerate(self.Step[index_i]):
                self.assertIsInstance(action, agent_actions.Action)
                self.assertEqual(action.action, action_keys[index_j])
            self.assertEqual(len(self.Step[index_i]), 3)
        self.assertEqual(len(self.Step), 3)

        # Test error
        with self.assertRaisesRegex(TypeError,
                                    'Cannot have both location and regular '
                                    'parallel'):
            self.Step = step.Step.setup(actions,
                                        self.number,
                                        self.shuffle,
                                        True,
                                        True,
                                        self.level)
