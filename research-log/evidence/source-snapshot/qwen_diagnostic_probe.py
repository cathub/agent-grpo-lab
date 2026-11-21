"""Same stochastic probe, with rendered inputs and MLX generation diagnostics."""
import json
from pathlib import Path
from .episode_evaluation import evaluate_episodes
from .evaluation import EvaluationMetadata, write_evaluation
from .qwen_agent import GenerationParameters, QwenAgent
from .qwen_episodes import QwenEpisodeSampler, episode_instructions
from .qwen_fewshot_experiment import EXAMPLE
from .qwen_prompt_comparison import SystemPromptBackend
from .scenarios import build_suite


class DiagnosticBackend:
    def __init__(self, backend, stream):
        self.backend, self.stream = backend, stream
        self.context = {}

    def generate(self, messages, parameters):
        from mlx_lm import stream_generate
        from mlx_lm.sample_utils import make_sampler
        tokenizer = self.backend.tokenizer
        rendered = tokenizer.apply_chat_template(messages, tokenize=False,
                                                  add_generation_prompt=True)
        # Identical encoding policy to MLX stream_generate's string-input path.
        special = tokenizer.bos_token is None or not rendered.startswith(tokenizer.bos_token)
        ids = tokenizer.encode(rendered, add_special_tokens=special)
        text = ''
        for response in stream_generate(
            self.backend.model, tokenizer, prompt=rendered,
            max_tokens=parameters.max_tokens,
            sampler=make_sampler(temp=parameters.temperature, top_p=parameters.top_p),
        ):
            text += response.text
        self.stream.write(json.dumps({
            **self.context, 'messages': messages, 'rendered_prompt': rendered,
            'input_token_ids': ids, 'input_token_count': response.prompt_tokens,
            'encoded_input_token_count': len(ids),
            'output_token_count': response.generation_tokens,
            'output_text_token_count': len(tokenizer.encode(text, add_special_tokens=False)),
            'stop_reason': response.finish_reason,
            'output_truncated': response.finish_reason == 'length',
            'input_truncated': False, 'raw_output': text,
        }) + '\n')
        self.stream.flush()
        return text


def main():
    output = Path('qwen-level2-group16-diagnostics')
    output.mkdir(exist_ok=False)
    agent = QwenAgent(parameters=GenerationParameters(temperature=0.7))
    prompt = episode_instructions() + EXAMPLE
    tasks = [task for task in build_suite('train') if task.level == 2]
    with (output / 'turn-diagnostics.jsonl').open('w') as stream:
        diagnostic = DiagnosticBackend(agent.backend, stream)
        agent.backend = SystemPromptBackend(diagnostic, prompt)
        factory = QwenEpisodeSampler(agent)

        def sampler(task_prompt, level, sample_id):
            session = factory(task_prompt, level, sample_id)
            task_id = next(t.task_id for t in tasks if t.prompt == task_prompt)

            def turn(history):
                diagnostic.context = {'task_id': task_id, 'sample_id': sample_id,
                                      'turn': len(history) + 1}
                return session(history)
            return turn

        metadata = EvaluationMetadata(agent.model_id,
            {**agent.sampling_parameters(), 'samples_per_prompt': 16},
            'scenarios-v1/train', 'environment-v1')
        results, summary = evaluate_episodes(tasks, sampler, 16, metadata)
        write_evaluation(output, results, summary)
    (output / 'system-prompt.txt').write_text(prompt + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
