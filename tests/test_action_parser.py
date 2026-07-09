import unittest

from action_parser import parse_action
from goal_motor import Action, ActionTypes


class TestActionParser(unittest.TestCase):
    def test_multiple_actions_are_expanded_into_action_objects(self):
        parsed = parse_action({
            "action": "multiple",
            "actions": [
                {"action": "wait", "duration": 10},
                {"action": "wait", "duration": 20},
            ],
        })

        self.assertIsInstance(parsed, ActionTypes.Actions)
        self.assertEqual(len(parsed.actions), 2)
        self.assertTrue(all(isinstance(action, Action) for action in parsed.actions))


if __name__ == "__main__":
    unittest.main()
