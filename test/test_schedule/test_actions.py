import unittest      as ut
import unittest.mock as mk

import collections as collect
import dataclasses as dclass

import source.agents.agent as main_agent

import source.schedule.actions as actions


class TestAction(ut.TestCase):
    """test the Action class"""

    def setUp(self):
        """Setup the tests"""

        self.action = mk.MagicMock(spec=str)

        self.Action = actions.Action(self.action)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.Action, actions.Action)

        self.assertEqual(self.Action.action, self.action)

        self.assertTrue(dclass.is_dataclass(self.Action))

    def test_perform(self):
        """test have agent perform action"""

        agent = mk.create_autospec(main_agent.Agent, spec_set=True)

        with mk.patch.object(actions, 'getattr') as mkGet:
            self.assertEqual(self.Action.perform(agent),
                             mkGet.return_value.return_value)
            self.assertEqual(mkGet.return_value.call_args_list,
                             [mk.call()])
            self.assertEqual(mkGet.call_args_list,
                             [mk.call(agent, self.action)])


class TestActions(ut.TestCase):
    """test the Actions class"""

    def setUp(self):
        """Setup the tests"""

        self.actions   = [mk.create_autospec(actions.Action, spec_set=True)
                          for _ in range(3)]
        self.agent_key = mk.MagicMock(spec=str)

        self.Actions = actions.Actions(self.actions,
                                       self.agent_key)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.Actions, collect.UserList)
        self.assertIsInstance(self.Actions, actions.Actions)

        self.assertEqual(self.Actions.agent_key, self.agent_key)

        self.assertEqual(self.Actions,      self.actions)
        self.assertEqual(self.Actions.data, self.actions)

    def test_perform(self):
        """test perform actions on agent"""

        agent = mk.create_autospec(main_agent.Agent, spec_set=True)

        results = []
        for action in self.actions:
            result = [mk.create_autospec(main_agent.Agent, spec_set=True)
                      for _ in range(3)]
            action.perform.return_value = result
            results.extend(result)

        self.assertEqual(self.Actions.perform(agent),
                         results)
        for action in self.actions:
            self.assertEqual(action.perform.call_args_list,
                             [mk.call(agent)])

    def test_setup(self):
        """test setup the agent"""

        action_keys = [mk.MagicMock(spec=str) for _ in range(3)]

        self.Actions = actions.Actions.setup(self.agent_key, action_keys)
        self.assertIsInstance(self.Actions, actions.Actions)
        self.assertEqual(self.Actions.agent_key, self.agent_key)

        for index, action in enumerate(self.Actions):
            self.assertIsInstance(action, actions.Action)
            self.assertEqual(action.action, action_keys[index])
        for index, action in enumerate(action_keys):
            self.assertIsInstance(self.Actions[index], actions.Action)
            self.assertEqual(self.Actions[index].action, action)
        self.assertEqual(len(self.Actions), 3)
