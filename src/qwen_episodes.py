"""Multi-step Qwen sessions; benchmark references never enter inference."""
import argparse
import json
from copy import deepcopy
from pathlib import Path

from .episode_evaluation import evaluate_episodes
from .evaluation import EvaluationMetadata, write_evaluation
from .qwen_agent import QwenAgent, tool_schema
from .scenarios import build_suite


def episode_instructions():
    schemas = deepcopy(tool_schema())
    for schema in schemas[:2]:
        schema['parameters']['properties']['platform']['enum'] = ['google', 'meta', 'tiktok']
        schema['parameters']['properties']['campaign'] = {
            'type': 'string', 'enum': ['brand', 'prospecting'],
            'description': 'Optional; omit to sum all campaigns.'}
    revenue = deepcopy(schemas[0])
    revenue.update(name='get_revenue', description='Total revenue in USD.')
    schemas.insert(2, revenue)
    reference = {'type': 'object', 'properties': {'observation_id': {'type': 'integer'}},
                 'required': ['observation_id'], 'additionalProperties': False}
    schemas[-1]['parameters']['properties'] = {'revenue': reference, 'spend': reference}
    return (
        'Return exactly one JSON action per turn, without markdown, explanation, or tags. '
        'A tool action has exactly keys "tool" and "arguments". '
        'After the required tools, submit {"final_answer": value}, using a JSON number '
        'for amounts or ratios, or a lowercase name for comparisons. '
        'Date ranges include both endpoints. Preserve the requested scope. '
        'Do not duplicate calls. Tool observations contain id and result. '
        'calculate_roas requires revenue and spend objects with observation_id referencing '
        'earlier get_revenue and get_ad_spend observations for the same scope, not raw numbers. '
        'Perform all checks requested by the task before submitting the answer. '
        'Available tool schemas: ' + json.dumps(schemas))


class QwenEpisodeSampler:
    def __init__(self, agent):
        self.agent = agent

    def __call__(self, prompt, level, sample_id):
        if level not in (2, 3):
            raise ValueError('This adapter supports Levels 2 and 3 only')

        def session(trajectory):
            messages = [{'role': 'system', 'content': episode_instructions()},
                        {'role': 'user', 'content': prompt}]
            for turn in trajectory:
                messages.append({'role': 'assistant', 'content': turn.raw_output})
                messages.append({'role': 'user', 'content':
                                 'Tool observation: ' + json.dumps(turn.observation)})
            return self.agent.backend.generate(messages, self.agent.parameters)
        return session


def run(agent, level, output_dir):
    if level not in (2, 3):
        raise ValueError('Choose Level 2 or 3')
    tasks = [task for task in build_suite('train') if task.level == level]
    metadata = EvaluationMetadata(agent.model_id, agent.sampling_parameters(),
                                  'scenarios-v1/train', 'environment-v1')
    results, summary = evaluate_episodes(tasks, QwenEpisodeSampler(agent), 1, metadata)
    write_evaluation(output_dir, results, summary)
    return results, summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--level', type=int, choices=(2, 3), required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    _, summary = run(QwenAgent(), args.level, args.output_dir)
    print(json.dumps(summary['by_level'], indent=2))


if __name__ == '__main__':
    main()
