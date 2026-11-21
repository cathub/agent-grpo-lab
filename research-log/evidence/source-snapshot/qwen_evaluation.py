"""Evaluate local Qwen on the existing Level 1 training split."""
import argparse
from pathlib import Path
from .evaluation import EvaluationMetadata, evaluate, write_evaluation
from .qwen_agent import DEFAULT_MODEL, GenerationParameters, QwenAgent
from .scenarios import build_suite


def run(agent, output_dir):
    tasks = [task.legacy for task in build_suite('train') if task.level == 1]
    metadata = EvaluationMetadata(agent.model_id, agent.sampling_parameters(),
                                  'day1-v1/l1-train', 'day1-v1')
    rollouts, summary = evaluate(tasks, agent.sample, metadata)
    write_evaluation(output_dir, rollouts, summary)
    return rollouts, summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model', default=DEFAULT_MODEL)
    parser.add_argument('--max-tokens', type=int, default=128)
    parser.add_argument('--temperature', type=float, default=0.0)
    parser.add_argument('--top-p', type=float, default=1.0)
    parser.add_argument('--seed', type=int, default=0)
    parser.add_argument('--output-dir', type=Path, default=Path('qwen-evaluation-output'))
    args = parser.parse_args()
    agent = QwenAgent(args.model, GenerationParameters(
        args.max_tokens, args.temperature, args.top_p, args.seed))
    _, summary = run(agent, args.output_dir)
    print(f"Success rate: {summary['task_success_rate']:.1%}")
    print(f"Failures: {summary['failure_category_counts']}")
    print(f'Logs: {args.output_dir}')


if __name__ == '__main__':
    main()
