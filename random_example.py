import socket
import json
import sys
import random

class Agent():
    """
    Agent class you should implement this
    """

    def __init__(self):
        pass

    def set_initial_status(self, initial_status):
        self.initial_status = initial_status
        self.agent_id = int(initial_status["your_agent_id"])
        self.field = initial_status["field"]

    def get_reward(self, reward):
        """
        get reward from environment per turn/episode
        """
        pass

    def action(self, current_status):
        """
        return action from current_status

        returns: [ action, direction  ]
        """
        my_x, my_y = current_status["agents"][self.agent_id]
        self.owners = current_status["owners"]
        return [ random.randint(0, 1), random.randint(1, 9) ]


