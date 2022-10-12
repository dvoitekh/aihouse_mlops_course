import click
import torch

from typing import List, Dict, Tuple
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from torch.nn.functional import softmax

# TODO: edit code start
class Model(object):
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("pysentimiento/robertuito-sentiment-analysis")
        self.model = AutoModelForSequenceClassification.from_pretrained("pysentimiento/robertuito-sentiment-analysis")
        self.labels = ['NEG', 'NEU', 'POS']

    def extract_features(self, text: List[str]) -> Dict[str, List[List[int]]]:
        return self.tokenizer(text, padding=True, return_tensors="pt")

    def predict_proba(self, features: Dict[str, List[List[int]]]) -> List[List[int]]:
        outputs = self.model(**features)
        return softmax(outputs.logits, dim=1).data.cpu().numpy()

    def __call__(self, text: List[str]) -> List[List[int]]:
        features = self.extract_features(text)
        return self.predict_proba(features)

@click.command()
@click.option("--prompt", required=True)
def inference(prompt: str) -> list:
    model = Model()
    probs = model([prompt])
    label_probs = [dict(zip(model.labels, x)) for x in probs]
    print(label_probs)
    return label_probs
# TODO: edit code end

if __name__ == "__main__":
    inference()
