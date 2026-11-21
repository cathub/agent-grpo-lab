"""Isolated one-example and token-budget diagnostics."""
import json
from pathlib import Path
from .qwen_agent import GenerationParameters, QwenAgent
from .qwen_episodes import episode_instructions, run
from .qwen_prompt_comparison import SystemPromptBackend

# Schema-valid, off-benchmark dates; no answer or observation is demonstrated.
EXAMPLE = (' Example tool action (raw JSON, without Markdown fences): '
           '{"tool":"get_conversions","arguments":{"platform":"tiktok",'
           '"start_date":"2024-06-10","end_date":"2024-06-12"}}')


def main():
    root = Path('qwen-fewshot-experiment')
    root.mkdir(exist_ok=False)
    manifest = {}
    for name, prompt, budget in (
        ('one_example_128', episode_instructions() + EXAMPLE, 128),
        ('original_256', episode_instructions(), 256),
    ):
        agent = QwenAgent(parameters=GenerationParameters(max_tokens=budget))
        backend = agent.backend
        agent.backend = SystemPromptBackend(backend, prompt)
        manifest[name] = {'system_prompt': prompt,
                          'generation_parameters': agent.sampling_parameters()}
        for level in (2, 3):
            _, summary = run(agent, level, root / name / f'level{level}')
            print(name, level, json.dumps(summary['by_level'][str(level)]), flush=True)
        del agent, backend
    (root / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')


if __name__ == '__main__':
    main()
