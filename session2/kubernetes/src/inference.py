import click

from typing import List, Dict
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from torch.nn.functional import softmax


class TextModel(object):
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("pysentimiento/robertuito-sentiment-analysis")
        self.model = AutoModelForSequenceClassification.from_pretrained("pysentimiento/robertuito-sentiment-analysis")
        self.labels = ['NEG', 'NEU', 'POS']

    def preprocess_text(self, text: List[str]) -> Dict[str, List[List[int]]]:
        return self.tokenizer(text, padding=True, return_tensors="pt")

    def predict_proba(self, features: Dict[str, List[List[int]]]) -> List[List[int]]:
        outputs = self.model(**features)
        return softmax(outputs.logits, dim=1).data.cpu().numpy()

    def __call__(self, text: List[str]) -> List[List[int]]:
        text = self.preprocess_text(text)
        return self.predict_proba(text)

@click.command()
@click.option("--prompt", required=True)
def inference(prompt: str) -> list:
    model = TextModel()
    probs = model([prompt])
    label_probs = [dict(zip(model.labels, x)) for x in probs]
    print(label_probs)
    return label_probs


if __name__ == "__main__":
    inference()
