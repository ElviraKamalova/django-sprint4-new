import functools
import torch
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
)

from core.constants import TOXICITY_THRESHOLD, MODEL_NAME


@functools.cache
def load_model_and_tokenizer():
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
    model.eval()
    return tokenizer, model


tokenizer, model = load_model_and_tokenizer()


def get_toxicity_score(text: str) -> float:
    inputs = tokenizer(
        text,
        return_tensors='pt',
        truncation=True,
        padding=True,
    )

    with torch.inference_mode():
        logits = model(**inputs).logits[0]
        probabilities = torch.sigmoid(logits)

    non_toxic_probability = probabilities[0].item()
    return 1 - non_toxic_probability


def is_toxic(text: str) -> bool:
    return get_toxicity_score(text) >= TOXICITY_THRESHOLD
