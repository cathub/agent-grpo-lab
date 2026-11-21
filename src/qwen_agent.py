"""Local inference without benchmark references or scoring."""
import json
from dataclasses import asdict, dataclass

DEFAULT_MODEL = 'mlx-community/Qwen2.5-0.5B-Instruct-4bit'


def tool_schema():
    lookup = {'platform': {'type': 'string', 'enum': ['google', 'meta']},
              'start_date': {'type': 'string', 'description': 'YYYY-MM-DD inclusive'},
              'end_date': {'type': 'string', 'description': 'YYYY-MM-DD inclusive'}}
    return [{'name': name, 'description': description, 'parameters': {
        'type': 'object', 'properties': props, 'required': list(props),
        'additionalProperties': False}} for name, description, props in [
            ('get_ad_spend', 'Total ad spend in USD.', lookup),
            ('get_conversions', 'Total conversions.', lookup),
            ('calculate_roas', 'Revenue divided by spend as a ratio.', {
                'revenue': {'type': 'number', 'minimum': 0},
                'spend': {'type': 'number', 'exclusiveMinimum': 0}})]]


@dataclass(frozen=True)
class GenerationParameters:
    max_tokens: int = 128
    temperature: float = 0.0
    top_p: float = 1.0
    seed: int = 0

    def __post_init__(self):
        if self.max_tokens <= 0 or self.temperature < 0 or not 0 < self.top_p <= 1:
            raise ValueError('Invalid generation parameters')


class MLXBackend:
    def __init__(self, model_id, parameters):
        import mlx.core as mx
        from mlx_lm import load
        self.model, self.tokenizer = load(model_id)
        mx.random.seed(parameters.seed)

    def generate(self, messages, parameters):
        from mlx_lm import generate
        from mlx_lm.sample_utils import make_sampler
        prompt = self.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True)
        return generate(self.model, self.tokenizer, prompt=prompt,
                        max_tokens=parameters.max_tokens,
                        sampler=make_sampler(temp=parameters.temperature,
                                             top_p=parameters.top_p), verbose=False)


class QwenAgent:
    def __init__(self, model_id=DEFAULT_MODEL, parameters=None, backend=None):
        self.model_id = model_id
        self.parameters = parameters or GenerationParameters()
        self.backend = backend if backend is not None else MLXBackend(model_id, self.parameters)

    def sample(self, prompt):
        messages = [{'role': 'system', 'content': (
            'Return exactly one JSON object with exactly keys "tool" and "arguments". '
            'Use an available tool name and arguments matching its schema. '
            'No markdown, explanation, tool-call tags, or multiple calls. '
            'Date ranges include both endpoints. Available tool schemas: '
            + json.dumps(tool_schema()))}, {'role': 'user', 'content': prompt}]
        # Preserve malformed outputs for scoring; never repair or retry.
        return [self.backend.generate(messages, self.parameters)]

    def sampling_parameters(self):
        return {**asdict(self.parameters), 'samples_per_prompt': 1}
