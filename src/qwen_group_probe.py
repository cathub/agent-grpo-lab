"""Stochastic reward-variation probe; no training or process rewards."""
import json
from pathlib import Path
from .episode_evaluation import evaluate_episodes
from .evaluation import EvaluationMetadata, write_evaluation
from .qwen_agent import GenerationParameters, QwenAgent
from .qwen_episodes import QwenEpisodeSampler, episode_instructions
from .qwen_fewshot_experiment import EXAMPLE
from .qwen_prompt_comparison import SystemPromptBackend
from .scenarios import build_suite


def main():
    output = Path('qwen-level2-group16-temp07')
    output.mkdir(exist_ok=False)
    agent = QwenAgent(parameters=GenerationParameters(temperature=0.7))
    prompt = episode_instructions() + EXAMPLE
    agent.backend = SystemPromptBackend(agent.backend, prompt)
    parameters = {**agent.sampling_parameters(), 'samples_per_prompt': 16}
    metadata = EvaluationMetadata(agent.model_id, parameters,
                                  'scenarios-v1/train', 'environment-v1')
    tasks = [task for task in build_suite('train') if task.level == 2]
    results, summary = evaluate_episodes(tasks, QwenEpisodeSampler(agent), 16, metadata)
    write_evaluation(output, results, summary)
    (output / 'system-prompt.txt').write_text(prompt + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
