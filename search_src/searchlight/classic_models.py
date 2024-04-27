from .headers import *
import numpy as np
from .headers import State
from .gameplay.simulators import *

class RandomActionPredictor(PolicyPredictor):

    def _predict(self, state: State, actions, actor) -> dict:
        '''
        Predicts the policy probabilities across actions given the current state and actor

        Args:
            state: current state
            actions: list of actions
            actor: actor to predict policy for

        Returns:
            probs: dictionary of actions to probabilities
        '''
        probs = dict()
        for action in actions:
            probs[action] = 1/len(actions)
        return probs

class RandomRolloutValueHeuristic(ValueHeuristic2):

    def __init__(self, actor_enumerator: ActorEnumerator, action_enumerator: ActionEnumerator,
                  forward_transitor: ForwardTransitor2, players = {0,1},
                  num_rollouts=10, rng: np.random.Generator = np.random.default_rng(),):
        '''
        Args:
            actor_enumerator: actor enumerator
            action_enumerator: action enumerator
            action_predictor: action predictor
            forward_transitor: forward transitor
            num_rollouts: number of rollouts to perform
        '''
        super().__init__()
        self.game_simulator = GameSimulator(forward_transitor, actor_enumerator, action_enumerator)
        self.num_rollouts = num_rollouts
        self.rng = rng
        # create random agents
        self.random_agents = dict()
        for player in players:
            self.random_agents[player] = RandomAgent(rng)
        self.random_agents[-1] = RandomAgent(rng)
    
    def _evaluate(self, state: State, actor=0) -> tuple[dict[Any, float], dict]:
        avg_scores, trajectories = self.game_simulator.simulate_games(self.random_agents, self.num_rollouts, state)
        return avg_scores, {'trajectories': trajectories}

        
            


