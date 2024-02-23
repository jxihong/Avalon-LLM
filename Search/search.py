from Search.beliefs import ValueGraph, ValueGraph2, ValueNode2
from Search.headers import *
from Search.estimators import *
from collections import deque
import warnings
import itertools
from datetime import datetime
import numpy as np
from queue import PriorityQueue

# TODO: implement MinMaxStats
# TODO: implement UCT search


    


class Search:
    '''
    Abstract class for search algorithms

    The design philosophy is that search algorithms themselves do not contain any data 
    Instead, all data is stored in the graph (see beliefs.py)
    '''
    def __init__(self):
        # for recording stats
        self.total_nodes_expanded = 0
        self.nodes_expanded = 0

    def expand(self, node_id):
        '''
        Expand starting from a node
        '''
        return self._expand(node_id)
        
    def _expand(self, node_id):
        '''
        Expand starting from a node
        '''
        raise NotImplementedError
    
    def get_total_nodes_expanded(self):
        return self.total_nodes_expanded
    
    def reset_total_nodes_expanded(self):
        self.total_nodes_expanded = 0

    def get_nodes_expanded(self):
        return self.nodes_expanded
    
class FullSearch(Search):
    '''
    Abstract class for full search algorithms
    '''
    def __init__(self, forward_transistor: ForwardTransitor,
                 value_heuristic: ValueHeuristic, actor_enumerator: ActorEnumerator,
                 action_enumerator: ActionEnumerator, action_predictor: ActionPredictor,
                 utility_estimator: UtilityEstimator):
        # self.graph = graph
        self.forward_transistor = forward_transistor
        self.value_heuristic = value_heuristic
        self.action_enumerator = action_enumerator
        self.utility_estimator = utility_estimator
        self.actor_enumerator = actor_enumerator
        self.action_predictor = action_predictor

        super().__init__()

class MCSearch(Search):
    '''
    Abstract class for Monte Carlo search algorithms
    '''
    def __init__(self, forward_transistor: ForwardTransitor,
                 initial_inferencer: InitialInferencer,
                 utility_estimator: UtilityEstimator):
        
        self.forward_transistor = forward_transistor
        self.initial_inferencer = initial_inferencer
        self.utility_estimator = utility_estimator
        
        super().__init__()

        

# TODO: refactor this to use the new model headers
# class ValueBFS(Search):
#     '''
#     Used to perform breadth-first search
#     '''
#     def __init__(self, forward_transistor: ForwardTransitor,
#                  value_heuristic: ValueHeuristic, action_enumerator: ActionEnumerator, 
#                  random_state_enumerator: RandomStateEnumerator, random_state_predictor: RandomStatePredictor,
#                  opponent_action_enumerator: OpponentActionEnumerator, opponent_action_predictor: OpponentActionPredictor, 
#                  utility_estimator: UtilityEstimator):
#         super().__init__(forward_transistor, value_heuristic, action_enumerator, 
#                          random_state_enumerator, random_state_predictor,
#                          opponent_action_enumerator, opponent_action_predictor, 
#                          utility_estimator, opponent_enumerator = OpponentEnumerator())
#         self.opponent_action_predictor = opponent_action_predictor

#     def expand(self, graph: ValueGraph, state: State, prev_node = None, depth=3, render = False, revise = False):
#         '''
#         Expand starting from a node
        
#         Args:
#             state: state to expand from
#             depth: depth to expand to
#             revise: whether to revise the graph or not

#         Returns:
#             value: updated value of the node
#         '''

#         node = graph.get_node(state)
#         if node is None: # node does not exist, create it
#             node = graph.add_state(state)   
#         if prev_node is not None:
#             node.parents.add(prev_node)
#             prev_node.children.add(node)

#         # check if node is terminal
#         if state.is_done():
#             value = state.get_reward()
#             node.values_estimates.append(value)
#             return value

#         if depth == 0:
#             value = self.value_heuristic.evaluate(state)
#             node.values_estimates.append(value)
#             utility = self.utility_estimator.estimate(node)
#             return utility
#         else:
#             value = 0.0
#             next_state_to_values = dict()
#             next_depth = depth if node.virtual else depth -1 # skip virtual nodes
            
#             if state.state_type == 'control':
#                 # enumerate actions
#                 if node.actions is None or revise:
#                     node.actions = self.action_enumerator.enumerate(state)

#                 # find next states
#                 if not node.next_states or revise:
#                     for action in node.actions:
#                         next_state = self.forward_transistor.transition(state, action)
#                         node.next_states.add(next_state)
#                         node.action_to_next_state[action] = next_state

#                 # expand next states
#                 for next_state in node.next_states:
#                     next_state_to_values[next_state] = self.expand(graph, next_state, node, next_depth)

#                 # add action to value
#                 for action in node.actions:
#                     next_state = node.action_to_next_state[action]
#                     node.action_to_value[action] = next_state_to_values[next_state]

#                 # value should be max of actions
#                 value = max(node.action_to_value.values())

#             elif state.state_type == 'adversarial':
#                 # enumerate opponents
#                 if node.opponents is None or revise:
#                     node.opponents = self.opponent_enumerator.enumerate(state)

#                 # enumerate actions
#                 if not node.adactions or revise:
#                     for opponent in node.opponents:
#                         node.adactions[opponent] = self.opponent_action_enumerator.enumerate(state, opponent)

#                 # predict probabilities over actions
#                 if not node.opponent_to_probs_over_actions or revise:
#                     for opponent in node.opponents:
#                         node.opponent_to_probs_over_actions[opponent] = self.opponent_action_predictor.predict(state, node.adactions[opponent], opponent)

#                 # enumerate joint adversarial actions
#                 if node.joint_adversarial_actions is None or revise:
#                     node.joint_adversarial_actions = list(itertools.product(*node.adactions.values()))

#                 # find joint adversarial actions to probabilities over actions
#                 if not node.joint_adversarial_actions_to_probs or revise:
#                     for joint_adversarial_action in node.joint_adversarial_actions:
#                         node.joint_adversarial_actions_to_probs[joint_adversarial_action] = 1.0
#                         for i, opponent in enumerate(node.opponents):
#                             action = joint_adversarial_action[i]
#                             prob = node.opponent_to_probs_over_actions[opponent][action]
#                             node.joint_adversarial_actions_to_probs[joint_adversarial_action] *= prob
                        
#                 # find next states
#                 if not node.next_states or revise:
#                     for joint_adversarial_action in node.joint_adversarial_actions:
#                         next_state = self.forward_transistor.transition(state, joint_adversarial_action)
#                         node.next_states.add(next_state)
#                         node.joint_adversarial_actions_to_next_states[joint_adversarial_action] = next_state

#                 # expand next states
#                 for next_state in node.next_states:
#                     next_state_to_values[next_state] = self.expand(graph, next_state, node, next_depth)

#                 # add expected value over actions
#                 for joint_adversarial_action in node.joint_adversarial_actions:
#                     prob = node.joint_adversarial_actions_to_probs[joint_adversarial_action]
#                     next_state = node.joint_adversarial_actions_to_next_states[joint_adversarial_action]
#                     value += prob*next_state_to_values[next_state]

#             elif state.state_type == 'stochastic': # random
#                 if node.actions is None or revise:
#                     node.actions = self.random_state_enumerator.enumerate(state)
#                 if not node.action_to_next_state or revise: # Dictionary is empty
#                     for action in node.actions:
#                         node.action_to_next_state[action] = self.forward_transistor.transition(state, action)
#                 if not node.probs_over_actions or revise: # Dictionary is empty
#                     node.probs_over_actions = self.random_state_predictor.predict(state, node.actions)
#                 for next_state in set(node.action_to_next_state.values()):
#                     next_state_to_values[next_state] = self.expand(graph, next_state, node, next_depth)

#                 # add expected value over actions 
#                 for action in node.actions:
#                     next_state = node.action_to_next_state[action]
#                     prob = node.probs_over_actions[action]
#                     value += prob*next_state_to_values[next_state]

#             elif state.state_type == 'simultaneous':
                
#                 # enumerate opponents
#                 if node.opponents is None or revise:
#                     node.opponents = self.opponent_enumerator.enumerate(state)
                    
#                 # enumerate adactions
#                 if not node.adactions or revise:
#                     for opponent in node.opponents:
#                         node.adactions[opponent] = self.opponent_action_enumerator.enumerate(state, opponent)

#                 # predict probabilities over actions
#                 if not node.opponent_to_probs_over_actions or revise:
#                     for opponent in node.opponents:
#                         node.opponent_to_probs_over_actions[opponent] = self.opponent_action_predictor.predict(state, node.adactions[opponent], player=opponent, prob=True)
                
#                 # enumerate joint adversarial actions. make sure they are tuples
#                 if node.joint_adversarial_actions is None or revise:
#                     node.joint_adversarial_actions = itertools.product(*node.adactions.values())

#                 # find joint adversarial actions to probabilities over actions
#                 if not node.joint_adversarial_actions_to_probs or revise:
#                     for joint_adversarial_action in node.joint_adversarial_actions:
#                         node.joint_adversarial_actions_to_probs[joint_adversarial_action] = 1.0
#                         for i, opponent in enumerate(node.opponents):
#                             action = joint_adversarial_action[i]
#                             prob = node.opponent_to_probs_over_actions[opponent][action]
#                             node.joint_adversarial_actions_to_probs[joint_adversarial_action] *= prob

#                 # enumerate proagonist actions
#                 if node.proactions is None or revise:
#                     node.proactions = self.action_enumerator.enumerate(state)
                        
#                 # enumerate all possible joint actions. first dimension always protagonist. dimensions after that are opponents
#                 if node.joint_actions is None or revise:
#                     node.joint_actions = itertools.product(node.proactions, *node.adactions.values())

#                 # find next states
#                 # TODO: some weird bug here where node.next_states is not empty but node.joint_actions_to_next_states is empty
#                 # UPDATE: fixed. dicts are mutable so when I was adding to node.joint_actions_to_next_states, I was adding to the same dict
#                 if not node.next_states or revise:
#                     for joint_action in node.joint_actions:
#                         next_state = self.forward_transistor.transition(state, joint_action)
#                         node.next_states.add(next_state)
#                         node.joint_actions_to_next_states[joint_action] = next_state

#                 # expand next states
#                 for next_state in node.next_states:
#                     next_state_to_values[next_state] = self.expand(graph, next_state, node, next_depth)

#                 # reset action_to_value to 0
#                 node.action_to_value = dict()
#                 for action in node.proactions:
#                     node.action_to_value[action] = 0.0

#                 # add expected value over actions
#                 for joint_action in node.joint_actions:
#                     prob = node.joint_adversarial_actions_to_probs[joint_action[1:]]
#                     next_state = node.joint_actions_to_next_states[joint_action]
#                     node.action_to_value[joint_action[0]] += prob*next_state_to_values[next_state]

#                 # value should be max of actions
#                 value = max(node.action_to_value.values())
                

#             if render and not node.virtual:
#                 plt = graph.to_mathplotlib()
#                 timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
#                 filename = f'Search/output/output_graph_{timestamp}.png'
#                 plt.savefig(filename)
#                 plt.close()
#                 # plt.show()
            
#             node.values_estimates.append(value)
#             utility = self.utility_estimator.estimate(node)
#             return utility

class SMMinimax(FullSearch):
    '''
    Used to perform breadth-first search

    This only works if the opponent is a single agent and the game is a zero-sum game
    '''
    def __init__(self, forward_transistor: ForwardTransitor,
                 value_heuristic: ValueHeuristic, actor_enumerator: ActorEnumerator,
                 action_enumerator: ActionEnumerator, action_predictor: ActionPredictor,
                 utility_estimator: UtilityEstimator):
        
        super().__init__(forward_transistor, value_heuristic, actor_enumerator,
                         action_enumerator, action_predictor, utility_estimator)
        
    def expand(self, graph: ValueGraph, state: State, 
               prev_node = None, depth=3, render = False, 
               revise = False, oracle = True, 
               node_budget=None):
        '''
        Expand starting from a node
        
        Args:
            state: state to expand from
            depth: depth to expand to
            render: whether to render the graph or not
            revise: whether to revise the graph or not
            oracle: whether the opponent always plays the best response or not as if they knew the protagonist's policy

        Returns:
            value: updated value of the node
        '''
        self.nodes_expanded = 0
        return self._expand(graph, state, prev_node, depth, render, revise, oracle, node_budget)

    def _expand(self, graph: ValueGraph, state: State, 
                prev_node = None, depth=3, render = False, 
                revise = False, oracle = True, 
                node_budget=None):
        '''
        Expand starting from a node
        
        Args:
            state: state to expand from
            depth: depth to expand to
            render: whether to render the graph or not
            revise: whether to revise the graph or not
            oracle: whether the opponent always plays the best response or not as if they knew the protagonist's policy

        Returns:
            value: updated value of the node
        '''

        # self.total_nodes_expanded += 1
        # self.nodes_expanded += 1

        if not oracle:
            raise NotImplementedError
        
        # print('Now exploring state', state)

        node = graph.get_node(state)
        if node is None: # node does not exist, create it
            node = graph.add_state(state)   
        if prev_node is not None:
            node.parents.add(prev_node)
            prev_node.children.add(node)

        # check if node is terminal
        if state.is_done():
            value = state.get_reward()
            # print('Terminal state', state, 'value', utility)
        elif depth == 0:
            value = self.value_heuristic.evaluate(state)
            # print('Depth 0 state', state, 'value', utility)
        elif node_budget is not None and self.nodes_expanded >= node_budget:
            # use heuristic to estimate value if node budget is exceeded
            value = self.value_heuristic.evaluate(state)
        else:
            self.total_nodes_expanded += 1
            self.nodes_expanded += 1

            value = 0.0
            next_state_to_values = dict()
            next_depth = depth if node.virtual else depth -1 # skip virtual nodes

            # enumerate actors
            if node.actors is None or revise:
                node.actors = self.actor_enumerator.enumerate(state)

            # print('node actors', node.actors)

            if -1 in node.actors: # random
                assert len(node.actors) == 1

                if node.actions is None or revise:
                    node.actions = self.action_enumerator.enumerate(state, -1)

                # print('node actions', node.actions)

                if not node.action_to_next_state or revise: # Dictionary is empty
                    node.next_states = set()
                    for action in node.actions:
                        # print('action', action)
                        next_state = self.forward_transistor.transition(state, {-1: action})
                        node.action_to_next_state[action] = next_state
                        node.next_states.add(next_state)
                if not node.probs_over_actions or revise: # Dictionary is empty
                    node.probs_over_actions = self.action_predictor.predict(state, node.actions, -1)

                # print('node expanded random', self.nodes_expanded)

                # if len(node.next_states) > node_budget-self.nodes_expanded and node_budget is not None, then use heuristic
                # if node_budget is not None and len(node.next_states) > node_budget-self.nodes_expanded:
                #     # use heuristic to estimate value if node budget is exceeded
                #     value = self.value_heuristic.evaluate(state)
                #     # print('Simultaneous state', state, 'heuristic value', value)
                #     node.values_estimates.append(value)
                #     utility = self.utility_estimator.estimate(node)
                #     return utility
                
                # print('probs over actions', node.probs_over_actions)
                for next_state in set(node.action_to_next_state.values()):
                    # print('next state', next_state)
                    next_state_to_values[next_state] = self._expand(graph, next_state, node, next_depth,
                                                                    revise=revise, oracle=oracle, node_budget=node_budget)
                
                # print('next state to values', next_state_to_values)

                # add expected value over actions 
                for action in node.actions:
                    next_state = node.action_to_next_state[action]
                    prob = node.probs_over_actions[action]
                    value += prob*next_state_to_values[next_state]

                # print('Random state', state, 'expected value', value)

            elif (0 in node.actors) and (1 in node.actors): # simultaneous
                assert len(node.actors) == 2

                # enumerate actions for each actor
                if not node.actor_to_actions or revise:
                    for actor in node.actors:
                        node.actor_to_actions[actor] = self.action_enumerator.enumerate(state, actor)

                # print('actor to actions', node.actor_to_actions)

                # print([x for x in itertools.product(*node.actor_to_actions.values())])
            
                # enumerate all possible joint actions as tuples of tuples (actor,action) pairs
                if node.actions is None or revise:
                    actors = node.actor_to_actions.keys()
                    node.actions = [tuple(zip(actors, x)) for x in itertools.product(*node.actor_to_actions.values())]
                
                # print('actions', node.actions)

                # find next states
                if node.next_states is None or revise:
                    node.next_states = set()
                    # print('next states not found')
                    for joint_action in node.actions:
                        next_state = self.forward_transistor.transition(state, dict(joint_action))
                        node.next_states.add(next_state)
                        node.action_to_next_state[joint_action] = next_state
                        # print('joint action', joint_action, 'next state', next_state)
                    node.next_states = frozenset(node.next_states)

                # print('next states', node.next_states)
                
                # print('nodes expanded simult', self.nodes_expanded)

                # # if len(node.next_states) > node_budget-self.nodes_expanded and node_budget is not None, then use heuristic
                # if node_budget is not None and len(node.next_states) > node_budget-self.nodes_expanded:
                #     # use heuristic to estimate value if node budget is exceeded
                #     value = self.value_heuristic.evaluate(state)
                #     # print('Simultaneous state', state, 'heuristic value', value)
                #     node.values_estimates.append(value)
                #     utility = self.utility_estimator.estimate(node)
                #     return utility

                # expand next states
                for next_state in node.next_states:
                    # print('next state', next_state)
                    # print('next state hash', hash(next_state))
                    next_state_to_values[next_state] = self._expand(graph, next_state, node, next_depth,
                                                                    revise=revise, oracle=oracle, node_budget=node_budget)

                # print('next state to values', next_state_to_values)

                # for each protagonist action, find the best response of the opponent
                opponent_best_responses = dict() # mapping from protagonist action to tuple of (opponent action, value)

                # set br values to infinity
                for proaction in node.actor_to_actions[0]:
                    opponent_best_responses[proaction] = (None, float('inf'))

                # find best response for each protagonist action
                for joint_action in node.actions:
                    proaction = dict(joint_action)[0]
                    value = next_state_to_values[node.action_to_next_state[joint_action]]
                    # print('joint action', joint_action, 'value', value)
                    if value < opponent_best_responses[proaction][1]:
                        opponent_best_responses[proaction] = (joint_action[1], value)

                # print('opponent best responses', opponent_best_responses)

                # set action to value to be opponent best response
                for proaction in node.actor_to_actions[0]:
                    node.proaction_to_value[proaction] = opponent_best_responses[proaction][1]

                # value should be max of actions
                value = max(node.proaction_to_value.values())

                # print('Simultaneous state', state, 'minimax value', value)
            
            else:
                print('node actors', node.actors)
                print('state', state)
                print('state actors', state.actors)
                raise NotImplementedError
                
            if render and not node.virtual:
                plt = graph.to_mathplotlib()
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f'Search/output/output_graph_{timestamp}.png'
                plt.savefig(filename)
                plt.close()
                # plt.show()
            
        node.values_estimates.append(value)
        utility = self.utility_estimator.estimate(node)
        return utility
        
class SMAlphaBetaMinimax(FullSearch):
    '''
    Used to perform simultaneous expected minimax search with alpha-beta pruning

    This only works if the opponent is a single agent and the game is a zero-sum game
    '''
    def __init__(self, forward_transistor: ForwardTransitor,
                 value_heuristic: ValueHeuristic, actor_enumerator: ActorEnumerator,
                 action_enumerator: ActionEnumerator, action_predictor: ActionPredictor,
                 utility_estimator: UtilityEstimator):
        
        super().__init__(forward_transistor, value_heuristic, actor_enumerator,
                         action_enumerator, action_predictor, utility_estimator)
        
    def expand(self, graph: ValueGraph, state: State,
                prev_node = None, depth=3, render = False, 
                revise = False, oracle = True, 
                alpha = -float('inf'), beta = float('inf'), threshold = 0.0,
                node_budget=None):
          '''
          Expand starting from a node
          
          Args:
                state: state to expand from
                depth: depth to expand to
                render: whether to render the graph or not
                revise: whether to revise the graph or not
                oracle: whether the opponent always plays the best response or not as if they knew the protagonist's policy
                alpha: alpha value for alpha-beta pruning
                beta: beta value for alpha-beta pruning
                threshold: threshold for alpha-beta pruning
    
          Returns:
                value: updated value of the node
          '''
          self.nodes_expanded = 0
          return self._expand(graph, state, prev_node, depth, render, revise, oracle, alpha, beta, threshold, node_budget)

    def _expand(self, graph: ValueGraph, state: State, 
               prev_node = None, depth=3, render = False, 
               revise = False, oracle = True, 
               alpha = -float('inf'), beta = float('inf'), threshold = 0.0,
               node_budget=None):
        '''
        Expand starting from a node
        
        Args:
            state: state to expand from
            depth: depth to expand to
            render: whether to render the graph or not
            revise: whether to revise the graph or not
            oracle: whether the opponent always plays the best response or not as if they knew the protagonist's policy
            alpha: alpha value for alpha-beta pruning
            beta: beta value for alpha-beta pruning
            threshold: threshold for alpha-beta pruning

        Returns:
            value: updated value of the node
        '''

        # self.total_nodes_expanded += 1
        # self.nodes_expanded += 1

        if not oracle:
            raise NotImplementedError
        
        # print('Now exploring state', state)

        node = graph.get_node(state)
        if node is None: # node does not exist, create it
            node = graph.add_state(state)   
        if prev_node is not None:
            node.parents.add(prev_node)
            prev_node.children.add(node)

        # check if node is terminal
        if state.is_done():
            value = state.get_reward()
            # print('Terminal state', state, 'value', utility)
        elif depth == 0:
            value = self.value_heuristic.evaluate(state)
            # print('Depth 0 state', state, 'value', utility)
        elif node_budget is not None and self.nodes_expanded >= node_budget:
            # use heuristic to estimate value if node budget is exceeded
            value = self.value_heuristic.evaluate(state)
        else:
            value = 0.0
            self.total_nodes_expanded += 1
            self.nodes_expanded += 1
            next_state_to_values = dict()
            next_depth = depth if node.virtual else depth -1 # skip virtual nodes

            # enumerate actors
            if node.actors is None or revise:
                node.actors = self.actor_enumerator.enumerate(state)

            # print('node actors', node.actors)

            if -1 in node.actors: # random
                assert len(node.actors) == 1

                if node.actions is None or revise:
                    node.actions = self.action_enumerator.enumerate(state, -1)

                # print('node actions', node.actions)

                if not node.action_to_next_state or revise: # Dictionary is empty
                    node.next_states = set()
                    for action in node.actions:
                        # print('action', action)
                        next_state = self.forward_transistor.transition(state, {-1: action})
                        node.action_to_next_state[action] = next_state
                        node.next_states.add(next_state)
                if not node.probs_over_actions or revise: # Dictionary is empty
                    node.probs_over_actions = self.action_predictor.predict(state, node.actions, -1)

                

                # if len(node.next_states) > node_budget-self.nodes_expanded and node_budget is not None, then use heuristic
                # if node_budget is not None and len(node.next_states) > node_budget-self.nodes_expanded:
                #     # use heuristic to estimate value if node budget is exceeded
                #     value = self.value_heuristic.evaluate(state)
                #     # print('Simultaneous state', state, 'heuristic value', value)
                #     node.values_estimates.append(value)
                #     utility = self.utility_estimator.estimate(node)
                #     return utility
                # print('probs over actions', node.probs_over_actions)
                for next_state in set(node.action_to_next_state.values()):
                    # print('next state', next_state)
                    next_state_to_values[next_state] = self._expand(graph, next_state, node, next_depth,
                                                                    revise=revise, oracle=oracle,
                                                                    alpha = alpha, beta = beta,
                                                                    threshold = threshold,
                                                                    node_budget=node_budget)
                
                # print('next state to values', next_state_to_values)

                # add expected value over actions 
                for action in node.actions:
                    next_state = node.action_to_next_state[action]
                    prob = node.probs_over_actions[action]
                    value += prob*next_state_to_values[next_state]

                # print('Random state', state, 'expected value', value)

            elif (0 in node.actors) and (1 in node.actors): # simultaneous
                assert len(node.actors) == 2

                # enumerate actions for each actor
                if not node.actor_to_actions or revise:
                    for actor in node.actors:
                        node.actor_to_actions[actor] = self.action_enumerator.enumerate(state, actor)

                # print('actor to actions', node.actor_to_actions)

                # print([x for x in itertools.product(*node.actor_to_actions.values())])
                        
                # # create next states
                # if node.next_states is None or revise:
                #     node.next_states = set()

                # set proaction to value to be -inf
                for proaction in node.actor_to_actions[0]:
                    node.proaction_to_value[proaction] = -float('inf')

                # find next states
                if node.next_states is None or revise:
                    node.next_states = set()
                    # print('next states not found')
                    for proaction in node.actor_to_actions[0]:
                        for adaction in node.actor_to_actions[1]:
                            joint_action = ((0, proaction), (1, adaction))
                            next_state = self.forward_transistor.transition(state, dict(joint_action))
                            node.next_states.add(next_state)
                            node.action_to_next_state[joint_action] = next_state
                            # print('joint action', joint_action, 'next state', next_state)

                # if len(node.next_states) > node_budget-self.nodes_expanded and node_budget is not None, then use heuristic
                # if node_budget is not None and len(node.next_states) > node_budget-self.nodes_expanded:
                #     # use heuristic to estimate value if node budget is exceeded
                #     value = self.value_heuristic.evaluate(state)
                #     # print('Simultaneous state', state, 'heuristic value', value)
                #     node.values_estimates.append(value)
                #     utility = self.utility_estimator.estimate(node)
                #     return utility
                
                # print('actions', node.actions) 
                maxvalue = -float('inf')
                for proaction in node.actor_to_actions[0]:
                    minvalue = float('inf')
                    for adaction in node.actor_to_actions[1]:
                        joint_action = ((0, proaction), (1, adaction))
                        next_state = node.action_to_next_state[joint_action]
                        if next_state not in next_state_to_values:
                            next_state_to_values[next_state] = self._expand(graph, next_state, 
                                                                           node, next_depth,
                                                                           alpha = alpha, beta = beta,
                                                                           threshold = threshold,
                                                                           revise=revise, oracle=oracle,
                                                                           node_budget=node_budget)
                        minvalue = min(minvalue, next_state_to_values[next_state])
                        if minvalue < alpha + threshold:
                            break
                        beta = min(beta, minvalue)
                    maxvalue = max(maxvalue, minvalue)
                    node.proaction_to_value[proaction] = minvalue
                    if maxvalue > beta - threshold:
                        break
                    alpha = max(alpha, maxvalue)

                # print('next states', node.next_states)

                # print('next state to values', next_state_to_values)

                # print('proaction to value', node.proaction_to_value)

                # value should be max of actions
                value = maxvalue

                # print('Simultaneous state', state, 'minimax value', value)
            
            else:
                print('node actors', node.actors)
                print('state', state)
                print('state actors', state.actors)
                raise NotImplementedError
                
            if render and not node.virtual:
                plt = graph.to_mathplotlib()
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f'Search/output/output_graph_{timestamp}.png'
                plt.savefig(filename)
                plt.close()
                # plt.show()
            
        node.values_estimates.append(value)
        utility = self.utility_estimator.estimate(node)
        return utility
    
class SmartSMAlphaBetaEMinimax(Search):
    '''
    Used to perform simultaneous expected minimax search with alpha-beta pruning with model guided priority

    This only works if the opponent is a single agent and the game is a zero-sum game
    '''
    def __init__(self, forward_transistor: ForwardTransitor,
                 value_heuristic: ValueHeuristic, actor_enumerator: ActorEnumerator,
                 action_enumerator: ActionEnumerator, action_predictor: ActionPredictor,
                 utility_estimator: UtilityEstimator):
        
        super().__init__(forward_transistor, value_heuristic, actor_enumerator,
                         action_enumerator, action_predictor, utility_estimator)
        
    def expand(self, graph: ValueGraph, state: State,
                prev_node = None, depth=None, render = False, 
                revise = False, oracle = True, 
                alpha = -float('inf'), beta = float('inf'), threshold = 0.0,
                node_budget=100):
        '''
        Expand starting from a node
        
        Args:
            state: state to expand from
            depth: depth to expand to
            render: whether to render the graph or not
            revise: whether to revise the graph or not
            oracle: whether the opponent always plays the best response or not as if they knew the protagonist's policy
            alpha: alpha value for alpha-beta pruning
            beta: beta value for alpha-beta pruning
            threshold: threshold for alpha-beta pruning

        Returns:
            value: updated value of the node
        '''

        nodes_expanded = 0
        expand_queue = PriorityQueue()

        # put in the first state
        expand_queue.put((0, state))

        # first expand belief tree by node_budget nodes
        while nodes_expanded < node_budget and not expand_queue.empty():
            # pop the state with the highest priority
            priority, state = expand_queue.get()

            # get the corresponding node
            node = graph.get_node(state)

            # 

        return self._expand(graph, state, prev_node, depth, render, revise, oracle, alpha, beta, threshold, node_budget)

    def _expand(self, graph: ValueGraph, state: State, 
               prev_node = None, depth=None, render = False, 
               revise = False, oracle = True, 
               alpha = -float('inf'), beta = float('inf'), threshold = 0.0,
               node_budget=10):
        '''
        Expand starting from a node
        
        Args:
            state: state to expand from
            depth: maximum depth to expand to
            render: whether to render the graph or not
            revise: whether to revise the graph or not
            oracle: whether the opponent always plays the best response or not as if they knew the protagonist's policy
            alpha: alpha value for alpha-beta pruning
            beta: beta value for alpha-beta pruning
            threshold: threshold for alpha-beta pruning

        Returns:
            value: updated value of the node
        '''

        # self.total_nodes_expanded += 1
        # self.nodes_expanded += 1

        if not oracle:
            raise NotImplementedError
        
        # print('Now exploring state', state)

        node = graph.get_node(state)
        if node is None: # node does not exist, create it
            node = graph.add_state(state)   
        if prev_node is not None:
            node.parents.add(prev_node)
            prev_node.children.add(node)

        # check if node is terminal
        if state.is_done():
            value = state.get_reward()
            # print('Terminal state', state, 'value', utility)
        elif depth == 0:
            value = self.value_heuristic.evaluate(state)
            # print('Depth 0 state', state, 'value', utility)
        elif node_budget is not None and self.nodes_expanded >= node_budget:
            # use heuristic to estimate value if node budget is exceeded
            value = self.value_heuristic.evaluate(state)
        else:
            value = 0.0
            self.total_nodes_expanded += 1
            self.nodes_expanded += 1
            next_state_to_values = dict()
            next_depth = depth if node.virtual else depth -1 # skip virtual nodes

            # enumerate actors
            if node.actors is None or revise:
                node.actors = self.actor_enumerator.enumerate(state)

            # print('node actors', node.actors)

            if -1 in node.actors: # random
                assert len(node.actors) == 1

                if node.actions is None or revise:
                    node.actions = self.action_enumerator.enumerate(state, -1)

                # print('node actions', node.actions)

                if not node.action_to_next_state or revise: # Dictionary is empty
                    node.next_states = set()
                    for action in node.actions:
                        # print('action', action)
                        next_state = self.forward_transistor.transition(state, {-1: action})
                        node.action_to_next_state[action] = next_state
                        node.next_states.add(next_state)
                if not node.probs_over_actions or revise: # Dictionary is empty
                    node.probs_over_actions = self.action_predictor.predict(state, node.actions, -1)

                

                # if len(node.next_states) > node_budget-self.nodes_expanded and node_budget is not None, then use heuristic
                # if node_budget is not None and len(node.next_states) > node_budget-self.nodes_expanded:
                #     # use heuristic to estimate value if node budget is exceeded
                #     value = self.value_heuristic.evaluate(state)
                #     # print('Simultaneous state', state, 'heuristic value', value)
                #     node.values_estimates.append(value)
                #     utility = self.utility_estimator.estimate(node)
                #     return utility
                # print('probs over actions', node.probs_over_actions)
                for next_state in set(node.action_to_next_state.values()):
                    # print('next state', next_state)
                    next_state_to_values[next_state] = self._expand(graph, next_state, node, next_depth,
                                                                    revise=revise, oracle=oracle,
                                                                    alpha = alpha, beta = beta,
                                                                    threshold = threshold,
                                                                    node_budget=node_budget)
                
                # print('next state to values', next_state_to_values)

                # add expected value over actions 
                for action in node.actions:
                    next_state = node.action_to_next_state[action]
                    prob = node.probs_over_actions[action]
                    value += prob*next_state_to_values[next_state]

                # print('Random state', state, 'expected value', value)

            elif (0 in node.actors) and (1 in node.actors): # simultaneous
                assert len(node.actors) == 2

                # enumerate actions for each actor
                if not node.actor_to_actions or revise:
                    for actor in node.actors:
                        node.actor_to_actions[actor] = self.action_enumerator.enumerate(state, actor)

                # print('actor to actions', node.actor_to_actions)

                # print([x for x in itertools.product(*node.actor_to_actions.values())])
                        
                # # create next states
                # if node.next_states is None or revise:
                #     node.next_states = set()

                # set proaction to value to be -inf
                for proaction in node.actor_to_actions[0]:
                    node.proaction_to_value[proaction] = -float('inf')

                # find next states
                if node.next_states is None or revise:
                    node.next_states = set()
                    # print('next states not found')
                    for proaction in node.actor_to_actions[0]:
                        for adaction in node.actor_to_actions[1]:
                            joint_action = ((0, proaction), (1, adaction))
                            next_state = self.forward_transistor.transition(state, dict(joint_action))
                            node.next_states.add(next_state)
                            node.action_to_next_state[joint_action] = next_state
                            # print('joint action', joint_action, 'next state', next_state)

                # if len(node.next_states) > node_budget-self.nodes_expanded and node_budget is not None, then use heuristic
                # if node_budget is not None and len(node.next_states) > node_budget-self.nodes_expanded:
                #     # use heuristic to estimate value if node budget is exceeded
                #     value = self.value_heuristic.evaluate(state)
                #     # print('Simultaneous state', state, 'heuristic value', value)
                #     node.values_estimates.append(value)
                #     utility = self.utility_estimator.estimate(node)
                #     return utility
                
                # print('actions', node.actions) 
                maxvalue = -float('inf')
                for proaction in node.actor_to_actions[0]:
                    minvalue = float('inf')
                    for adaction in node.actor_to_actions[1]:
                        joint_action = ((0, proaction), (1, adaction))
                        next_state = node.action_to_next_state[joint_action]
                        if next_state not in next_state_to_values:
                            next_state_to_values[next_state] = self._expand(graph, next_state, 
                                                                           node, next_depth,
                                                                           alpha = alpha, beta = beta,
                                                                           threshold = threshold,
                                                                           revise=revise, oracle=oracle,
                                                                           node_budget=node_budget)
                        minvalue = min(minvalue, next_state_to_values[next_state])
                        if minvalue < alpha + threshold:
                            break
                        beta = min(beta, minvalue)
                    maxvalue = max(maxvalue, minvalue)
                    node.proaction_to_value[proaction] = minvalue
                    if maxvalue > beta - threshold:
                        break
                    alpha = max(alpha, maxvalue)

                # print('next states', node.next_states)

                # print('next state to values', next_state_to_values)

                # print('proaction to value', node.proaction_to_value)

                # value should be max of actions
                value = maxvalue

                # print('Simultaneous state', state, 'minimax value', value)
            
            else:
                print('node actors', node.actors)
                print('state', state)
                print('state actors', state.actors)
                raise NotImplementedError
                
            if render and not node.virtual:
                plt = graph.to_mathplotlib()
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f'Search/output/output_graph_{timestamp}.png'
                plt.savefig(filename)
                plt.close()
                # plt.show()
            
        node.values_estimates.append(value)
        utility = self.utility_estimator.estimate(node)
        return utility
    
class QValueAdjuster:
    '''
    Abstract class. Used to adjust qvalues for a given node
    '''
    def __init__(self) -> None:
        pass

    def adjust(self, qvalue, prior, state_visits, state_action_visits) -> float:
        '''
        Adjusts the qvalue for a given state-action pair

        Args:
            qvalue: qvalue to adjust
            prior: prior probability of the action
            state_visits: number of visits to the state
            state_action_visits: number of visits to the state-action pair

        Returns:
            adjusted qvalue
        '''
        raise NotImplementedError
    
class PUCTAdjuster(QValueAdjuster):

    def __init__(self, c1=1.0, c2=19652) -> None:
        self.c1 = c1
        self.c2 = c2

    def adjust(self, qvalue, prior, state_visits, state_action_visits) -> float:
        '''
        Adjusts the qvalue for a given state-action pair

        Args:
            qvalue: qvalue to adjust
            prior: prior probability of the action
            state_visits: number of visits to the state
            state_action_visits: number of visits to the state-action pair

        Returns:
            adjusted qvalue
        '''
        return qvalue + prior*np.sqrt(state_visits)/(1 + state_action_visits) *(self.c1* + np.log((state_visits + self.c2 + 1)/self.c2))
    
class SMMonteCarlo(MCSearch):
    '''
    Used to perform simultaneous expected monte carlo tree search 
    TODO: add alpha-beta pruning

    This only works if the opponent is a single agent and the game is a zero-sum game
    '''
    def __init__(self, forward_transistor: ForwardTransitor,
                 initial_inferencer: InitialInferencer,
                 utility_estimator: UtilityEstimator,
                 adjuster: QValueAdjuster,
                 rng: np.random.Generator = np.random.default_rng()):
        
        super().__init__(forward_transistor, initial_inferencer, utility_estimator)
        self.rng = rng
        self.adjuster = adjuster
        
    def expand(self, graph: ValueGraph, state: State,
                render = False, player = 0,
                revise = False, oracle = True, 
                node_budget=100, num_rollout = 100):
        '''
        Expand starting from a node
        
        Args:
            state: state to expand from
            render: whether to render the graph or not
            revise: whether to revise the graph or not
            oracle: whether the opponent always plays the best response or not as if they knew the protagonist's policy
            alpha: alpha value for alpha-beta pruning
            beta: beta value for alpha-beta pruning
            threshold: threshold for alpha-beta pruning

        Returns:
            value: updated value of the node
        '''

        nodes_expanded = 0

        # first expand belief tree by node_budget nodes
        while nodes_expanded < node_budget and num_rollout > 0:

            # run one simulation
            self.mc_simulate(graph, state)
            num_rollout -= 1

        # get the value of the node and return it
        node = graph.get_node(state)
        return self.utility_estimator.estimate(node, player)
    
    def initial_inference(self, state: State):
        '''
        Conducts initial inference on a state
        '''
        return self.initial_inferencer.predict(state)

    def mc_simulate(self, graph: ValueGraph2, state: State, prev_node = None):
        '''
        Runs one simulation (rollout) from the given state

        The convention for joint actions is a tuple of tuples (actor, action), which can be converted to a dictionary
        using dict(joint_action)
        '''
        node = graph.get_node(state)
        if node is None: # node does not exist, create it. this should never happen unless root node
            node = graph.add_state(state)   

        if not node.is_expanded:
            # conduct initial inference on the node
            (actors, policies, actions, next_values, intermediate_rewards, transitions) = self.initial_inference(state)
            node.actors = actors
            node.actor_to_action_to_prob = policies
            node.actions = actions # joint actions, a set of tuples of tuples (actor, action)
            node.action_to_actor_to_reward = intermediate_rewards
            node.action_to_next_state = transitions
            node.is_expanded = True

            # if prev_node is not None:
            #     node.parents.add(prev_node)
            #     prev_node.children.add(node)

            # for each possible next state, create a node and add it to the graph if it does not exist
            for next_state in next_values.keys():
                if not graph.get_node(next_state):
                    new_node = graph.add_state(next_state)
                    node.children.add(new_node)
                    new_node.parents.add(node)
                    new_node.is_expanded = False
                    new_node.actor_to_value_estimates = dict()

                    # for each actor and value in next_values, add it to new_node.actor_to_value_estimates
                    for actor, value in next_values[next_state].items():
                        new_node.actor_to_value_estimates[actor] = [value]
            return True

        # check if node is terminal
        if node.actions is None:
            return False
        
        # if not then select an action to simulate
        action = self.select_action(node, graph)

        # get the next state
        next_state = node.action_to_next_state[action]

        # simulate the next state
        is_expanded = self.mc_simulate(graph, next_state, node)

        # backpropagate the value from the next state
        self.backpropagate(node, action, next_state, graph)

    def select_action(self, node: ValueNode2, graph: ValueGraph2):
        '''
        Selects a joint action to simulate
        '''
        # calculate the probability of each joint action
        action_to_prob = dict()
        for joint_action in node.actions:
            prob = 1.0
            for actor, action in joint_action:
                prob *= node.actor_to_action_to_prob[actor][action]
            action_to_prob[joint_action] = prob

        # get action of each actor using _select_action_by_actor. put in tuple of tuples (actor, action)
        joint_action = tuple((actor, self._select_action_by_actor(node, actor, action_to_prob, graph)) for actor in node.actors)
        
        return joint_action
        

    def _select_action_by_actor(self, node: ValueNode2, actor, action_to_prob: dict, graph: ValueGraph2):
        '''
        Selects an action to simulate for a given actor

        Args:
            node: node to select action from
            actor: actor to select action for
            action_to_prob: dictionary of estimated joint actions to probability
        '''
        
        # if actor == -1 (environment), then select an action according to the policy
        # i.e. probability weights should be node.actor_to_action_to_prob[actor].values()
        if actor == -1:
            return self.rng.choice(list(node.actor_to_action_to_prob[actor].keys()), 
                                   p = list(node.actor_to_action_to_prob[actor].values()))
        # otherwise choose the action with the highest adjusted qvalue
        else:
            adj_qvalues = self.get_adjusted_qvalues(node, actor, action_to_prob, graph) # this is a dictionary of action to qvalue
            return max(adj_qvalues, key=adj_qvalues.get)
            
    def get_adjusted_qvalues(self, node: ValueNode2, actor, action_to_prob: dict, graph: ValueGraph2) -> dict:
        '''
        Gets the adjusted qvalues for a given actor.
        Usually the PUCT value is used

        Args:
            node: node to get the adjusted qvalues for
            actor: actor to get the adjusted qvalues for
            action_to_prob: dictionary of estimated joint actions to probability

        Returns:
            action_to_value: dictionary of adjusted qvalues
        '''

        # find the expected qvalue for each action
        action_to_expected_qvalue = dict()
        # action_to_expected_qvalue to 0 for each action
        for action in node.actor_to_action_to_prob[actor].keys():
            action_to_expected_qvalue[action] = 0.0
        # find expected qvalue by summing over all joint actions that contain the action
        for joint_action, prob in action_to_prob.items():
            # get the action in the joint action that corresponds to the actor
            action = dict(joint_action)[actor]
            # get next state
            next_state = node.action_to_next_state[joint_action]
            # get the value of the next state using utility estimator
            next_value = self.utility_estimator.estimate(graph.get_node(next_state), actor)
            # add the value to the expected qvalue
            action_to_expected_qvalue[action] += prob*next_value
            # get the intermediate reward
            reward = node.action_to_actor_to_reward[joint_action][actor]
            # add the reward to the expected qvalue
            action_to_expected_qvalue[action] += prob*reward

        # for each action, use the adjuster to get the adjusted qvalue
        action_to_value = dict()
        for action in node.actor_to_action_to_prob[actor].keys():
            action_to_value[action] = self.adjuster.adjust(action_to_expected_qvalue[action],
                                                        node.actor_to_action_to_prob[actor][action],
                                                        node.visits, node.actor_to_action_visits[actor][action])
        return action_to_value

    def backpropagate(self, node: ValueNode2, action, next_state: State, graph: ValueGraph2):
        '''
        Backpropagates the value from the next state to the current node for each actor

        Args:
            node: node to backpropagate to
            action: action taken to get to the next state
            next_state: next state to backpropagate from
            graph: graph to backpropagate to

        Returns:
            None
        '''
        # we need to backpropagate for each actor
        for actor in node.actors:
            # can skip if actor is -1 (environment)
            if actor == -1:
                continue
            # get the value of the next state
            next_value = self.utility_estimator.estimate(graph.get_node(next_state), actor)
            # get the intermediate reward
            reward = node.action_to_actor_to_reward[action][actor]
            # update the value of the current node
            node.actor_to_value_estimates[actor].append(next_value + reward)
            # update the number of visits to the state
            node.visits += 1
            # get the action that this actor took
            actor_action = dict(action)[actor]
            # update the number of visits to the state-action pair
            node.actor_to_action_visits[actor][actor_action] += 1

    