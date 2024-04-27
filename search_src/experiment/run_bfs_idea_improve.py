from src.searchlightimprove.headers import *
from src.searchlightimprove.llm_utils.llm_api_models import GPT35Multi
from src.searchlightimprove.prompts.improvement_prompts import IMPROVEMENT_PROMPTS
from src.GOPS.baseline_models_GOPS import *
from src.GOPS.value_heuristic_evaluators import GOPSValueHeuristicsSSGEvaluator
from src.searchlightimprove.analyzers import HeuristicsAnalyzer
from src.searchlight.gameplay.simulators import GameSimulator
from src.GOPS.examples.abstract_list3 import abstract_list
from src.GOPS.examples.func_list3 import func_list
from src.utils import setup_logging_environment
from src.searchlightimprove.evolvers import ImprovementLibraryEvolver, BeamEvolver, ThoughtBeamEvolver
from src.searchlightimprove.prompts.prompt_generators import PromptGenerator
from src.searchlightimprove.prompts.improvement_prompts import GOPS_RULES, GOPS_FUNCTION_SIGNATURE
from src.Avalon.baseline_models_Avalon import *
from src.searchlight.datastructures.graphs import ValueGraph2
from src.Avalon.examples.avalon_func import avalon_func_list
# from src.Avalon.value_heuristic_evaluators import AvalonValueHeuristicsSSGEvaluator
from src.searchlightimprove.value_heuristic_improve import ValueHeuristicsSSGEvaluator
import logging
import os
import datetime


import hydra
from omegaconf import DictConfig, OmegaConf

@hydra.main(version_base=None, config_path="../configs", config_name="run_modular_improve")
def main(cfg : DictConfig):
    # TODO: see if we can make this more descent
    # create main logger
    logger = logging.getLogger(__name__)
    logger.info('Starting initialization')
    starttime = datetime.datetime.now()

    hydra_working_dir = hydra.core.hydra_config.HydraConfig.get().runtime.output_dir
    logger.info(f"Outputs for current run will be saved to {hydra_working_dir}")
    # parameters for configuration
    # TODO: move these to a configuration file, use hydra
    
    num_batch_runs = cfg.preset_modular_improve.num_batch_runs
    batch_size = cfg.preset_modular_improve.batch_size
    evolutions = cfg.preset_modular_improve.evolutions
    num_responses = cfg.preset_modular_improve.num_responses
    against_benchmark = cfg.preset_modular_improve.get("against_benchmark", None)
    final_eval_num_batch_runs = cfg.preset_modular_improve.get("final_eval_num_batch_runs", 1)
    save_dir = cfg.get("save_dir", hydra_working_dir)
    num_fittest_functions = cfg.preset_modular_improve.get("num_fittest_functions", 1)
    num_ideas_per_iteration = cfg.preset_modular_improve.get("num_ideas_per_iteration", 1)
    num_search_budget = cfg.preset_modular_improve.get("num_search_budget", 16)
    num_random_rollouts = cfg.preset_modular_improve.get("num_random_rollouts", 4)
    evolver_name = cfg.evolver_name

    model_type = cfg.model.get("model", "gpt-3.5-turbo")

    logger.info(str(OmegaConf.to_yaml(cfg)))

    # note that number of simulations will be O(num_responses^3 * num_batch_runs * batch_size^2)

    # create improvement proposer
    gpt = GPT35Multi(temperature=0.7, num_responses=num_responses, model=model_type)

    # creat rng
    rng = np.random.default_rng(12)

    # configure the environment
    env_name = cfg.env_preset.env_name
    if env_name == 'GOPS':
        # create GOPSValueHeuristicsSSGEvaluator
        GOPS_num_cards = cfg.env_preset.num_cards
        transitor=GOPSForwardTransitor2()
        actor_enumerator=GOPSActorEnumerator()
        action_enumerator=GOPSActionEnumerator()
        start_state=GOPSState2({-1}, tuple(),tuple(), tuple(), GOPS_num_cards)

        # create prompt generator
        prompt_generator = PromptGenerator(environment_rules=GOPS_RULES, function_signature=GOPS_FUNCTION_SIGNATURE)
        seed_functions = [(func, {'abstract': abstract}) for func, abstract in zip(func_list, abstract_list)]
        # create game simulator
        simulator = GameSimulator(transitor=transitor, 
                                  actor_enumerator=actor_enumerator, action_enumerator=action_enumerator, start_state=start_state,
                                  rng=rng)
        # create evaluator
        evaluator = GOPSValueHeuristicsSSGEvaluator(simulator=simulator, num_batch_runs=num_batch_runs, players = {0,1}, against_benchmark=against_benchmark)

        # create check_function
        check_function = LLMFunctionalValueHeuristic.test_evaluate_static
        parse_function = LLMFunctionalValueHeuristic.parse_llm_function

        partial_information = False

    elif env_name == 'Avalon':
        # get relevant parameters
        num_players = cfg.env_preset.num_players

        # create avalon environment
        env = AvalonGameEnvironment.from_num_players(num_players)
        player_lst = [i for i in range(num_players)]
        player_set = set(player_lst)
        action_enumerator = AvalonActionEnumerator(env)
        transitor = AvalonTransitor(env)
        actor_enumerator = AvalonActorEnumerator()
        start_state = AvalonState.init_from_env(env)
        players = player_set

        # create prompt generator for avalon
        prompt_generator = PromptGenerator(environment_rules=GAME_RULES, function_signature=HEURISTICS_FUNCTION_SIGNATURE)
        seed_functions = [(func, {'abstract': abstract}) for func, abstract in zip(avalon_func_list, abstract_list)]

        # create game simulator
        simulator = GameSimulator(transitor=transitor, 
                                  actor_enumerator=actor_enumerator, action_enumerator=action_enumerator, start_state=start_state, 
                                  rng=rng)

        check_function = AvalonLLMFunctionalValueHeuristic.test_evaluate_static
        parse_function = AvalonLLMFunctionalValueHeuristic.parse_llm_generated_function

        partial_information = True

        # create evaluator
        evaluator = ValueHeuristicsSSGEvaluator(
            simulator=simulator,
            transitor=transitor,
            actor_enumerator=actor_enumerator,
            action_enumerator=action_enumerator,
            check_function=check_function,
            llm_func_value_heuristic_class=AvalonLLMFunctionalValueHeuristic,
            num_batch_runs=num_batch_runs,
            players=players,
            rng=rng,
            against_benchmark=against_benchmark,
            search_budget=num_search_budget,
            random_rollouts=num_random_rollouts, 
            partial_information=partial_information,
        )
    else:
        raise ValueError(f'Environment {env_name} not supported')

    # create analyzer
    analyzer = HeuristicsAnalyzer(num_samples=6, prompt_generator=prompt_generator)

    # create evolver
    if evolver_name == 'ImprovementLibrary':
        evolver = ImprovementLibraryEvolver(evaluator=evaluator, model=gpt, analyzer=analyzer, batch_size=batch_size, seed_functions=seed_functions, check_function=check_function, prompt_generator = prompt_generator, parse_function=parse_function, num_fittest_functions=num_fittest_functions, num_ideas_per_iteration=num_ideas_per_iteration)
    elif evolver_name == 'Beam':
        evolver = BeamEvolver(evaluator=evaluator, model=gpt, analyzer=analyzer, seed_functions=seed_functions, prompt_generator=prompt_generator, check_function=check_function, parse_function=parse_function, batch_size=batch_size, num_fittest_functions=num_fittest_functions)
    elif evolver_name == 'ThoughtBeam':
        evolver = ThoughtBeamEvolver(evaluator=evaluator, model=gpt, analyzer=analyzer, seed_functions=seed_functions, prompt_generator=prompt_generator, check_function=check_function, parse_function=parse_function, batch_size=batch_size, num_fittest_functions=num_fittest_functions)
    else:
        raise ValueError(f'Evolver {evolver_name} not supported')

    # log how long it took to initialize
    endtime = datetime.datetime.now()
    elapsed_time = endtime - starttime
    logger.info(f'Initialization took {elapsed_time}')

    logger.info('Starting evolution')

    starttime = datetime.datetime.now()

    # evolve 
    evolver.evolve(evolutions)

    # log how long it took to evolve
    endtime = datetime.datetime.now()
    elapsed_time = endtime - starttime
    logger.info(f'Evolution took {elapsed_time}')

    # log num_calls and num_generated_responses from LLM model
    logger.info(f'num_calls: {gpt.num_calls}')
    logger.info(f'expense: ${gpt.total_expense}')
    logger.info(f'num_generated_responses: {gpt.num_generated_responses}')

    logger.info('Starting final evaluation')

    starttime = datetime.datetime.now()

    # set batch_runs of evaluator to final_eval_num_batch_runs
    evaluator.set_num_batch_runs(final_eval_num_batch_runs)

    endtime = datetime.datetime.now()
    elapsed_time = endtime - starttime
    logger.info(f'Final evaluation took {elapsed_time}')

    if evolver_name == 'ImprovementLibrary':
        # produce analysis
        function_results, benchmark_scores, idea_results = evolver.produce_analysis()

        # produce results
        evolver.produce_figures(function_results, benchmark_scores, idea_results, save_dir)

    elif evolver_name == 'Beam':
        # produce analysis
        function_results, benchmark_scores = evolver.produce_analysis()

        # produce results
        evolver.produce_figures(function_results, benchmark_scores, save_dir)

    elif evolver_name == 'ThoughtBeam':
        # produce analysis
        function_results, benchmark_scores = evolver.produce_analysis()

        # produce results
        evolver.produce_figures(function_results, benchmark_scores, save_dir)


if __name__ == '__main__':
    setup_logging_environment(log_level=logging.INFO)
    print('Running main')
    main()