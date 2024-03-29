import unittest      as ut
import unittest.mock as mk

import collections as collect

import source.agents.agent as main_agent

import source.schedule.actions  as agent_actions
import source.schedule.schedule as schedule
import source.schedule.step     as agent_step

import source.space.agents   as main_agents
import source.space.space    as agent_space


class TestSchedule(ut.TestCase):
    """test the Schedule class"""

    def setUp(self):
        """Setup the tests"""

        self.steps = [mk.create_autospec(agent_step.Step, spec_set=True)
                      for _ in range(3)]

        self.Schedule = schedule.Schedule(self.steps)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.Schedule, collect.UserList)
        self.assertIsInstance(self.Schedule, schedule.Schedule)

        self.assertEqual(self.Schedule,      self.steps)
        self.assertEqual(self.Schedule.data, self.steps)

    def test__activate(self):
        """test activate the results"""

        results = [mk.create_autospec(main_agent.Agent, spec_set=True)
                   for _ in range(3)]

        self.Schedule._activate(results)
        for result in results:
            self.assertEqual(result.activate.call_args_list,
                             [mk.call()])

    def test__perform(self):
        """test perform the schedule and get results"""

        space  = mk.create_autospec(agent_space.Space, spec_set=True)
        agents = mk.create_autospec(main_agents.Agents, spec_set=True)

        results = []
        for step in self.steps:
            result = [mk.MagicMock() for _ in range(3)]
            step.perform.return_value = result
            results.extend(result)

        self.assertEqual(self.Schedule._perform(space, agents), results)

        for step in self.steps:
            self.assertEqual(step.perform.call_args_list,
                             [mk.call(space, agents)])
        self.assertEqual(len(self.steps), 3)

    def test_perform(self):
        """test perform the schedule"""

        space  = mk.create_autospec(agent_space.Space, spec_set=True)
        agents = mk.create_autospec(main_agents.Agents, spec_set=True)

        with mk.patch.object(schedule.Schedule, '_perform',
                             autospec=True) as mkPerform:
            with mk.patch.object(schedule.Schedule, '_activate',
                                 autospec=True) as mkActivate:
                self.Schedule.perform(space, agents)
                self.assertEqual(mkActivate.call_args_list,
                                 [mk.call(mkPerform.return_value)])
                self.assertEqual(mkPerform.call_args_list,
                                 [mk.call(self.Schedule, space, agents)])

    def test_setup(self):
        """test setup an entire schedule"""

        basic_actions = {}
        for _ in range(3):
            agent_key   = mk.MagicMock(spec=str)
            action_keys = [mk.MagicMock(spec=str) for _ in range(3)]

            basic_actions[agent_key] = action_keys
        tuple_basic = (basic_actions,)

        repeat_actions = {}
        for _ in range(3):
            agent_key   = mk.MagicMock(spec=str)
            action_keys = [mk.MagicMock(spec=str) for _ in range(3)]

            repeat_actions[agent_key] = action_keys
        tuple_repeat = (repeat_actions, 10)

        shuffle_actions_0 = {}
        for _ in range(3):
            agent_key   = mk.MagicMock(spec=str)
            action_keys = [mk.MagicMock(spec=str) for _ in range(3)]

            shuffle_actions_0[agent_key] = action_keys
        tuple_shuffle_0 = (shuffle_actions_0, 10, True)

        shuffle_actions_1 = {}
        for _ in range(3):
            agent_key   = mk.MagicMock(spec=str)
            action_keys = [mk.MagicMock(spec=str) for _ in range(3)]

            shuffle_actions_1[agent_key] = action_keys
        tuple_shuffle_1 = (shuffle_actions_1, 10, True, True)

        reg_actions = {}
        for _ in range(3):
            agent_key   = mk.MagicMock(spec=str)
            action_keys = [mk.MagicMock(spec=str) for _ in range(3)]

            reg_actions[agent_key] = action_keys
        tuple_reg = (reg_actions, 10, True, True, True)

        loc_actions = {}
        for _ in range(3):
            agent_key   = mk.MagicMock(spec=str)
            action_keys = [mk.MagicMock(spec=str) for _ in range(3)]

            loc_actions[agent_key] = action_keys
        tuple_loc = (loc_actions, 10, True, True, False, True, 1)

        step_tuples = [tuple_basic,
                       tuple_repeat,
                       tuple_shuffle_0,
                       tuple_shuffle_1,
                       tuple_reg,
                       tuple_loc]

        self.Schedule = schedule.Schedule.setup(step_tuples)
        self.assertIsInstance(self.Schedule, schedule.Schedule)

        self.assertEqual(len(self.Schedule), 6)

        # basic tuple
        self.assertIsInstance(self.Schedule[0], agent_step.Step)
        self.assertEqual(self.Schedule[0].number,          1)
        self.assertEqual(self.Schedule[0].shuffle_agents,  False)
        self.assertEqual(self.Schedule[0].shuffle_actions, False)
        self.assertEqual(self.Schedule[0].parallel_reg,    False)
        self.assertEqual(self.Schedule[0].parallel_loc,    False)
        self.assertEqual(self.Schedule[0].level,           0)
        for index_i, thing in enumerate(basic_actions.items()):
            agent_key, action_keys = thing
            self.assertIsInstance(self.Schedule[0][index_i],
                                  agent_actions.Actions)
            self.assertEqual(self.Schedule[0][index_i].agent_key, agent_key)
            for index_j, action in enumerate(action_keys):
                self.assertIsInstance(self.Schedule[0][index_i][index_j],
                                      agent_actions.Action)
                self.assertEqual(self.Schedule[0][index_i][index_j].action,
                                 action)
            for index_j, action in enumerate(self.Schedule[0][index_i]):
                self.assertIsInstance(action, agent_actions.Action)
                self.assertEqual(action.action, action_keys[index_j])
            self.assertEqual(len(self.Schedule[0][index_i]), 3)
        self.assertEqual(len(self.Schedule[0]), 3)

        # repeat tuple
        self.assertIsInstance(self.Schedule[1], agent_step.Step)
        self.assertEqual(self.Schedule[1].number,          10)
        self.assertEqual(self.Schedule[1].shuffle_agents,  False)
        self.assertEqual(self.Schedule[1].shuffle_actions, False)
        self.assertEqual(self.Schedule[1].parallel_reg,    False)
        self.assertEqual(self.Schedule[1].parallel_loc,    False)
        self.assertEqual(self.Schedule[1].level,           0)
        for index_i, thing in enumerate(repeat_actions.items()):
            agent_key, action_keys = thing
            self.assertIsInstance(self.Schedule[1][index_i],
                                  agent_actions.Actions)
            self.assertEqual(self.Schedule[1][index_i].agent_key, agent_key)
            for index_j, action in enumerate(action_keys):
                self.assertIsInstance(self.Schedule[1][index_i][index_j],
                                      agent_actions.Action)
                self.assertEqual(self.Schedule[1][index_i][index_j].action,
                                 action)
            for index_j, action in enumerate(self.Schedule[1][index_i]):
                self.assertIsInstance(action, agent_actions.Action)
                self.assertEqual(action.action, action_keys[index_j])
            self.assertEqual(len(self.Schedule[1][index_i]), 3)
        self.assertEqual(len(self.Schedule[1]), 3)

        # shuffle tuple 0
        self.assertIsInstance(self.Schedule[2], agent_step.Step)
        self.assertEqual(self.Schedule[2].number,          10)
        self.assertEqual(self.Schedule[2].shuffle_agents,  True)
        self.assertEqual(self.Schedule[2].shuffle_actions, False)
        self.assertEqual(self.Schedule[2].parallel_reg,    False)
        self.assertEqual(self.Schedule[2].parallel_loc,    False)
        self.assertEqual(self.Schedule[2].level,           0)
        for index_i, thing in enumerate(shuffle_actions_0.items()):
            agent_key, action_keys = thing
            self.assertIsInstance(self.Schedule[2][index_i],
                                  agent_actions.Actions)
            self.assertEqual(self.Schedule[2][index_i].agent_key, agent_key)
            for index_j, action in enumerate(action_keys):
                self.assertIsInstance(self.Schedule[2][index_i][index_j],
                                      agent_actions.Action)
                self.assertEqual(self.Schedule[2][index_i][index_j].action,
                                 action)
            for index_j, action in enumerate(self.Schedule[2][index_i]):
                self.assertIsInstance(action, agent_actions.Action)
                self.assertEqual(action.action, action_keys[index_j])
            self.assertEqual(len(self.Schedule[2][index_i]), 3)
        self.assertEqual(len(self.Schedule[2]), 3)

        # shuffle tuple 1
        self.assertIsInstance(self.Schedule[3], agent_step.Step)
        self.assertEqual(self.Schedule[3].number,          10)
        self.assertEqual(self.Schedule[3].shuffle_agents,  True)
        self.assertEqual(self.Schedule[3].shuffle_actions, True)
        self.assertEqual(self.Schedule[3].parallel_reg,    False)
        self.assertEqual(self.Schedule[3].parallel_loc,    False)
        self.assertEqual(self.Schedule[3].level,           0)
        for index_i, thing in enumerate(shuffle_actions_1.items()):
            agent_key, action_keys = thing
            self.assertIsInstance(self.Schedule[3][index_i],
                                  agent_actions.Actions)
            self.assertEqual(self.Schedule[3][index_i].agent_key, agent_key)
            for index_j, action in enumerate(action_keys):
                self.assertIsInstance(self.Schedule[3][index_i][index_j],
                                      agent_actions.Action)
                self.assertEqual(self.Schedule[3][index_i][index_j].action,
                                 action)
            for index_j, action in enumerate(self.Schedule[3][index_i]):
                self.assertIsInstance(action, agent_actions.Action)
                self.assertEqual(action.action, action_keys[index_j])
            self.assertEqual(len(self.Schedule[3][index_i]), 3)
        self.assertEqual(len(self.Schedule[3]), 3)

        # reg tuple
        self.assertIsInstance(self.Schedule[4], agent_step.Step)
        self.assertEqual(self.Schedule[4].number,          10)
        self.assertEqual(self.Schedule[4].shuffle_agents,  True)
        self.assertEqual(self.Schedule[4].shuffle_actions, True)
        self.assertEqual(self.Schedule[4].parallel_reg,    True)
        self.assertEqual(self.Schedule[4].parallel_loc,    False)
        self.assertEqual(self.Schedule[4].level,           0)
        for index_i, thing in enumerate(reg_actions.items()):
            agent_key, action_keys = thing
            self.assertIsInstance(self.Schedule[4][index_i],
                                  agent_actions.Actions)
            self.assertEqual(self.Schedule[4][index_i].agent_key, agent_key)
            for index_j, action in enumerate(action_keys):
                self.assertIsInstance(self.Schedule[4][index_i][index_j],
                                      agent_actions.Action)
                self.assertEqual(self.Schedule[4][index_i][index_j].action,
                                 action)
            for index_j, action in enumerate(self.Schedule[4][index_i]):
                self.assertIsInstance(action, agent_actions.Action)
                self.assertEqual(action.action, action_keys[index_j])
            self.assertEqual(len(self.Schedule[4][index_i]), 3)
        self.assertEqual(len(self.Schedule[4]), 3)

        # loc tuple
        self.assertIsInstance(self.Schedule[5], agent_step.Step)
        self.assertEqual(self.Schedule[5].number,          10)
        self.assertEqual(self.Schedule[5].shuffle_agents,  True)
        self.assertEqual(self.Schedule[5].shuffle_actions, True)
        self.assertEqual(self.Schedule[5].parallel_reg,    False)
        self.assertEqual(self.Schedule[5].parallel_loc,    True)
        self.assertEqual(self.Schedule[5].level,           1)
        for index_i, thing in enumerate(loc_actions.items()):
            agent_key, action_keys = thing
            self.assertIsInstance(self.Schedule[5][index_i],
                                  agent_actions.Actions)
            self.assertEqual(self.Schedule[5][index_i].agent_key, agent_key)
            for index_j, action in enumerate(action_keys):
                self.assertIsInstance(self.Schedule[5][index_i][index_j],
                                      agent_actions.Action)
                self.assertEqual(self.Schedule[5][index_i][index_j].action,
                                 action)
            for index_j, action in enumerate(self.Schedule[5][index_i]):
                self.assertIsInstance(action, agent_actions.Action)
                self.assertEqual(action.action, action_keys[index_j])
            self.assertEqual(len(self.Schedule[5][index_i]), 3)
        self.assertEqual(len(self.Schedule[5]), 3)
