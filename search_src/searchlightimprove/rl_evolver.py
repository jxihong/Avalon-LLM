from .headers import *
from searchlight.bandit import MultiarmedBanditLearner
from .llm_utils.llm_api_models import LLMModel
# from .prompts.improvement_prompts import gen_specific_improvement_prompt, gen_draw_conclusions_from_feedback_prompt, gen_implement_function_from_improvement_prompt
from .prompts.prompt_generators import PromptGenerator
from src.searchlight.utils import UpdatablePriorityDictionary
from src.searchlight.gameplay.agents import Agent
from src.searchlight.headers import State, ValueHeuristic2
from .value_heuristic_improve import *

import numpy as np
import os

from typing import Optional

class RLValueHeuristicsSSGEvaluator(SimulateSearchGameEvaluator):

    def __init__(self, simulator: GameSimulator, transitor: ForwardTransitor2, actor_enumerator: ActorEnumerator, action_enumerator: ActionEnumerator, num_batch_runs: int = 10, players = {0,1}, rng: np.random.Generator = np.random.default_rng(), against_benchmark=False, search_budget=16, random_rollouts=16):
        super().__init__(simulator, num_batch_runs, players, rng)
        self.against_benchmark = against_benchmark
        self.transitor = transitor
        self.actor_enumerator = actor_enumerator
        self.action_enumerator = action_enumerator
        self.action_predictor = PolicyPredictor()
        self.search_budget = search_budget
        self.random_rollouts = random_rollouts


    def evaluate(self, models) -> tuple[list[float], list]:
        '''
        Args:
            functions: list of functions to evaluate

        Returns:
            scores: list of scores for each function
            notes: list of notes for each function. specific notes are stored in a dictionary. 
                - if the function is not executable, the dictionary will contain an 'execution_error' key
                - otherwise the dictionary will contain the usual trajectory notes
        '''
        agents = self.create_agents(models)

        if not self.against_benchmark:
            # evaluate the passed functions
            passed_scores, passed_notes = super().evaluate_agents(agents)
        else:
            passed_scores = []
            passed_notes = []
            for model in models:
                # evaluate each function against the benchmark instead
                function_scores, function_notes, benchmark_scores = self.evaluate_with_benchmark([model])
                passed_scores.extend(function_scores)
                passed_notes.extend(function_notes)

        return passed_scores, passed_notes
        
    
    def create_agents(self, models) -> list[SearchAgent]:
        # create graphs
        graphs = [ValueGraph2(adjuster=PUCTAdjuster(), utility_estimator=UtilityEstimatorLast()) for _ in range(len(models))]
        # create value heuristics
        value_heuristics = [RLValueHeuristic(model) for model in models]
        # create initial inferencers
        initial_inferencers = [PackageInitialInferencer(self.transitor, self.action_enumerator, self.action_predictor, self.actor_enumerator, value_heuristic) for value_heuristic in value_heuristics]
        # create MCTS search algorithms
        search_algorithms = [SMMonteCarlo(initial_inferencer=initial_inferencer, rng=self.random_agent.rng, node_budget=self.search_budget, num_rollout=self.search_budget) for initial_inferencer in initial_inferencers]
        # create agents
        agents = [SearchAgent(search_algorithm, graph, self.rng) for graph, search_algorithm in zip(graphs, search_algorithms)]
        return agents
    
    def create_benchmark_agents(self) -> tuple[list[str], list[SearchAgent]]:
        '''
        Creates benchmark agents for evaluation
        '''
        num_agents = 1
        # create graphs
        graphs = [ValueGraph2(adjuster=PUCTAdjuster(), utility_estimator=UtilityEstimatorLast()) for _ in range(num_agents)]
        # create value heuristics
        value_heuristics = [RandomRolloutValueHeuristic(self.actor_enumerator, self.action_enumerator, self.transitor, num_rollouts=self.random_rollouts, rng=self.random_agent.rng) for _ in range(num_agents)]
        # create initial inferencers
        initial_inferencers = [PackageInitialInferencer(self.transitor, self.action_enumerator, self.action_predictor, self.actor_enumerator, value_heuristic) for value_heuristic in value_heuristics]
        # create MCTS search algorithms
        search_algorithms = [SMMonteCarlo(initial_inferencer=initial_inferencer, rng=self.random_agent.rng, node_budget=self.search_budget, num_rollout=self.search_budget) for initial_inferencer in initial_inferencers]
        # create agents
        agents = [SearchAgent(search_algorithm, graph, self.rng) for graph, search_algorithm in zip(graphs, search_algorithms)]
        return ['RandomRolloutValueHeuristicMCTS'], agents
    
    def evaluate_with_benchmark(self, models) -> tuple[list[float], list, dict[str, float]]:
        '''
        Evaluates the functions with additional benchmark agents. The benchmark agents are:
        - RandomRolloutValueHeuristic under MCTS search

        Also possibly increases search budget for the agents. 

        Functions are assumed to be executable.

        Args:
            functions: list of functions to evaluate

        Returns:
            function_scores: list of scores for each function
            notes: list of notes for each function. specific notes are stored in a dictionary. 
                - if the function is not executable, the dictionary will contain an 'execution_error' key
                - otherwise the dictionary will contain the usual trajectory notes
            benchmark_scores: dictionary of benchmark scores for each benchmark agent
        '''
        # first create the function agents
        model_agents = self.create_agents(models)

        # create benchmark agents
        benchmark_names, benchmark_agents = self.create_benchmark_agents()

        all_agents = model_agents + benchmark_agents

        # print(f'evaluating {len(all_agents)} agents {all_agents}')
        # run the evaluation
        scores, notes = self.evaluate_agents(all_agents)

        # print('done evaluating agents')

        # separate the scores
        function_scores = scores[:len(model_agents)]
        benchmark_scores = scores[len(model_agents):]
        function_notes = notes[:len(model_agents)]

        # assign the benchmark scores to the benchmark names
        benchmark_scores = {name: score for name, score in zip(benchmark_names, benchmark_scores)}

        return function_scores, function_notes, benchmark_scores
    
class RLValueHeuristic(ValueHeuristic2):
    # TODO: implement this class
    pass

class RLEvolver(Evolver):
    '''
    Abstract class for evolving functions
    '''

    # functions_dict: UpdatablePriorityDictionary # where values are a dictionary

    def __init__(self, evaluator: Evaluator, batch_size: int = 10, ):
        '''
        Args:
            evaluator: evaluator for functions
            batch_size: number of functions to propose at a time
            seed_functions: list of seed functions to start with, (function, abstract)
            check_function: function to check if a function is valid
            parse_function: function to parse a function
            model: LLM model to use for generating functions
            num_fittest_functions: number of fittest functions to consider each iteration
        '''
        super().__init__()
        self.evaluator = evaluator
        self.batch_size = batch_size
        # self.functions_dict = UpdatablePriorityDictionary()
        self.num_evolutions = 0 # number of evolutions conducted
        self.data = [] # data for training the model

        # TODO: you should create a pytorch model here
        self.model = None

        # do initial evaluation of your model

        # evaluate the model
        vh = RLValueHeuristic(torch_model = self.model)
        scores, notes = self.evaluate(vh)
        self.data.append(notes[0]['feedback']['trajectory_data'])

        self.num_evolutions += 1

        # create logger
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def evaluate(self, functions) -> tuple[list[float], list[dict]]:
        return self.evaluator.evaluate(functions)
    
    def evolve_once(self):
        '''
        Conducts one cycle of evolution
        '''

        # TODO: get data (see analyzers.py for more example of how to extract data)
        training_data = self.data[-1]

        self.logger.info('training data: {training_data}')

        # TODO: train model

        # evaluate the model
        vh = RLValueHeuristic(torch_model = self.model)
        scores, notes = self.evaluate(vh)

        self.num_evolutions += 1
        self.data.append(notes[0]['feedback']['trajectory_data'])


    def evolve(self, num_cycles: int):
        '''
        Evolves the functions for a certain number of cycles
        '''
        for _ in range(num_cycles):
            self.evolve_once()