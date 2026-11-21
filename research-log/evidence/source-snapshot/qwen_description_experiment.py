"""Description-only A/B experiment, preserving the baseline prompt builder."""
import json
from pathlib import Path
from .qwen_agent import QwenAgent
from .qwen_episodes import episode_instructions, run
from .qwen_prompt_comparison import SystemPromptBackend


def enhanced_prompt():
    prefix, encoded = episode_instructions().split('Available tool schemas: ', 1)
    schemas = json.loads(encoded)
    descriptions = {
        'get_ad_spend': ('Retrieves actual total advertising spend in USD from the dataset. '
            'Use when advertising spend is needed to answer a spending question or calculate ROAS.'),
        'get_conversions': ('Retrieves the actual total number of conversions from the dataset. '
            'Use to compare conversion counts or check a minimum-conversions requirement.'),
        'get_revenue': ('Retrieves actual total revenue in USD from the dataset. '
            'Use for revenue totals, combined revenue, or the revenue input to ROAS.'),
    }
    for schema in schemas:
        name = schema['name']
        if name in descriptions:
            schema['description'] = descriptions[name] + (
                ' platform selects google, meta, or tiktok; start_date and end_date are '
                'inclusive YYYY-MM-DD bounds; optional campaign selects brand or prospecting, '
                'and omitting it sums all campaigns. Returns an observation with id and the '
                'numeric total in result. Use result for the requested comparison, sum, or '
                'final answer; retain id when this lookup is needed by calculate_roas. '
                'Do not invent dataset values.')
        else:
            schema['description'] = (
                'Calculates ROAS as revenue divided by advertising spend. Use when the task '
                'requests ROAS or comparison of ROAS values. revenue and spend are objects '
                'whose observation_id identifies earlier get_revenue and get_ad_spend '
                'observations for the same platform, campaign, and date range. These inputs '
                'are observation references, not numeric amounts. Retrieve both observations '
                'before calling this tool. Returns an observation with id and the numeric '
                'ROAS ratio in result. Use result for the final ratio or compare retrieved '
                'ratios to choose the requested name. Do not invent observation IDs.')
    return prefix + 'Available tool schemas: ' + json.dumps(schemas)


def main():
    root = Path('qwen-description-experiment')
    root.mkdir(exist_ok=False)
    prompts = {'A_existing': episode_instructions(), 'B_descriptions': enhanced_prompt()}
    (root / 'system-prompts.json').write_text(json.dumps(prompts, indent=2) + '\n')
    for name, prompt in prompts.items():
        agent = QwenAgent()
        backend = agent.backend
        agent.backend = SystemPromptBackend(backend, prompt)
        for level in (2, 3):
            _, summary = run(agent, level, root / name / f'level{level}')
            print(name, level, json.dumps(summary['by_level'][str(level)]), flush=True)
        del agent, backend


if __name__ == '__main__':
    main()
