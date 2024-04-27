from ..datastructures.adjusters import Search
from ..headers import *
from ..datastructures.estimators import *
from ..datastructures.beliefs import *
from ..datastructures.adjusters import *
from ..datastructures.graphs import ValueGraph2

from queue import PriorityQueue
import logging

class InferenceSearch2(Search):
    '''
    Abstract class for inference search algorithms that use an initial inferencer
    '''
    def __init__(self, initial_inferencer: InitialInferencer2, 
                 cut_cycles: bool = False, record_notes: bool = True):
        '''
        Args:
            initial_inferencer: initial inferencer to use
            cut_cycles: whether to cut cycles in the graph or not. if True, the graph will not add edges that create cycles. Otherwise, it will add edges that create cycles (leading to potentially infinite loops)
            record_notes: whether to record notes in the notes or not. recording notes will increase memory usage but will allow generate data for debugging and analysis
        '''
        
        super().__init__()
        self.initial_inferencer = initial_inferencer
        self.cut_cycles = cut_cycles
        self.record_notes = record_notes
        

    def initial_inference(self, state: State):
        '''
        Conducts initial inference on a state
        '''
        return self.initial_inferencer.predict(state)
    
    def infer_node(self, graph: ValueGraph2, state: State):
        '''
        Conducts initial inference on a state

        Args:
            graph: graph to infer on
            state: state to infer on

        Returns:
            node: node that was inferred
            did_expand: whether the node was expanded or not
        '''
        node = graph.get_node(state)
        did_expand = False
        if node is None: # node does not exist, create it. this should never happen unless root node
            node = graph.add_state(state)   

        if not node.is_expanded:
            did_expand = True

            # conduct initial inference on the node
            (policies, next_values, intermediate_rewards, transitions, notes) = self.initial_inference(state)
            node.actor_to_action_to_prob = policies
            node.action_to_actor_to_reward = intermediate_rewards
            node.action_to_next_state = transitions
            node.is_expanded = True

            # cut out actions that lead to cycles (i.e. actions that lead to states that are already in the graph)
            if self.cut_cycles:
                actions_to_remove = set()
                for action, next_state in node.action_to_next_state.items():
                    if graph.get_node(next_state): # TODO: this assumes that the graph is a tree. For more sophisticated approach, we need to check if next_state is the ancestor of the current state
                        if self.cut_cycles:
                            actions_to_remove.add(action)
                        else:
                            raise ValueError('Cycle detected in graph. To prevent infinite loops, set cut_cycles to True')
                for action in actions_to_remove:
                    # send to end node for now and set intermediate rewards to -inf
                    # node.action_to_next_state[action] = END_STATE
                    # node.action_to_actor_to_reward[action] = {actor: -float('inf') for actor in node.get_actors()}
                    del node.action_to_next_state[action]
                    del node.action_to_actor_to_reward[action]
                    for actor, single_action in action:
                        del node.actor_to_action_to_prob[actor][single_action]
                        if not node.actor_to_action_to_prob[actor]:
                            del node.actor_to_action_to_prob[actor]

                    # del node.actor_to_action_to_prob[0][action]
                    # TODO: we should also ban actions that lead to joint_actions that are already in the graph

            # increment nodes expanded
            self.increment_nodes_expanded()

            # if terminal state, return False
            if node.is_done():
                # set value estimates to 0 since it is terminal
                for actor in graph.players:
                    node.actor_to_value_estimates[actor] = [0]
            else:
                # for each possible next state, create a node and add it to the graph if it does not exist
                for next_state in next_values.keys():
                    if not graph.get_node(next_state):
                        new_node = graph.add_state(next_state)
                        node.children.add(new_node)
                        new_node.parents.add(node)
                        new_node.is_expanded = False
                        new_node.actor_to_value_estimates = dict()

                        if self.record_notes:

                            # add new feedback to new_node if it exists
                            if 'next_state_to_heuristic_notes' in notes:
                                new_node.notes['heuristic_feedback'] = notes['next_state_to_heuristic_notes'][next_state]
                                # print('heuristic_feedback', new_node.notes['heuristic_feedback'])
                                # print('next_state', next_state)

                            # add heuristics estimated score (next_values) to new_node.notes['heuristic_score']
                            new_node.notes['heuristic_score'] = next_values[next_state]

                        # for each actor and value in next_values, add it to new_node.actor_to_value_estimates
                        for actor, value in next_values[next_state].items():
                            new_node.actor_to_value_estimates[actor] = [value]
        return node, did_expand

class BestFirstSearch(InferenceSearch2):
    '''
    Abstract class for best first search algorithms
    '''
    def __init__(self, initial_inferencer: InitialInferencer2, rng: np.random.Generator = np.random.default_rng(), node_budget:int = 100, cut_cycles: bool = False):
        
        self.rng = rng
        self.node_budget = node_budget
        self.unexpanded_states = PriorityQueue()
        super().__init__(initial_inferencer, cut_cycles=cut_cycles)

    def _expand(self, graph: ValueGraph2, state: State,):
        '''
        Expand starting from a node
        '''

        # TODO: make sure popped_state is in cone of state. Yes already doing it inefficiently
        self.nodes_expanded = 0

        # if graph does not have state, add it to unexpanded_states
        if not graph.get_node(state):
            self.unexpanded_states.put((0, state))
        while self.nodes_expanded < self.node_budget and not self.unexpanded_states.empty():
            # pop node from queue
            (priority, popped_state) = self.unexpanded_states.get()

            # print('popped_state', popped_state)

            # get node from graph
            node, did_expand = self.infer_node(graph, popped_state)

            # print('children', node.children)

            

            if did_expand:
                # TODO: backpropagate the value from the next state
                # graph.backpropagate(node, action, next_state)
                # we need to backpropogate to all parents of node

                # add all children of node to queue
                # TODO: change to qvalues instead (adjusted_q_values = graph.get_adjusted_qvalues(node))
                # TODO: make sure all actors are accounted for?
                for child in node.children:
                    # child priority should be the estimated value of the child
                    child_priority = -graph.get_estimated_value(child, 0)

                    # log the child state and priority
                    self.logger.debug(f'child state: {child.state}, priority: {child_priority}')

                    self.unexpanded_states.put((child_priority, child.state))

                # increment nodes expanded
                self.increment_nodes_expanded()
                pass

            
            
                
            


        