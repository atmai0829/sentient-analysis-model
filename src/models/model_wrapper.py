"""One interface for every model: predict_proba_pos(sentences) -> list[float]."""
import hashlib
import re

from .model_configs import MODELS


class SentimentModel:
    def __init__(self, name, checkpoint, pos_index=1, device=None):
        import torch
        from transformers import AutoModelForSequenceClassification, AutoTokenizer

        self.name = name
        self.torch = torch
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = AutoTokenizer.from_pretrained(checkpoint)
        self.model = AutoModelForSequenceClassification.from_pretrained(checkpoint)
        self.model.to(self.device).eval()

        # Prefer the checkpoint's own label names when they say "positive".
        self.pos_index = pos_index
        for idx, label in self.model.config.id2label.items():
            if "POS" in str(label).upper():
                self.pos_index = int(idx)
        print(f"[{name}] {checkpoint} on {self.device}; "
              f"id2label={self.model.config.id2label}; pos_index={self.pos_index}")

    def predict_proba_pos(self, sentences, batch_size=32):
        out = []
        with self.torch.no_grad():
            for i in range(0, len(sentences), batch_size):
                batch = list(sentences[i:i + batch_size])
                enc = self.tokenizer(batch, padding=True, truncation=True,
                                     max_length=128, return_tensors="pt").to(self.device)
                probs = self.torch.softmax(self.model(**enc).logits, dim=-1)
                out.extend(probs[:, self.pos_index].cpu().tolist())
        return out


class MockModel:
    """Fake classifier for testing the pipeline without downloads/GPU.

    Deliberately leans on the first sentiment word it sees (a caricature of the
    trigger-word shortcut) plus seeded noise. Its numbers mean NOTHING about
    real models; it only exists so the plumbing can be tested end to end.
    """
    POS = {"loved", "thrilled", "best", "excited", "perfect", "delighted", "nice",
           "glad", "pleased", "fine", "free", "early", "approved", "acceptance",
           "promotion", "raise", "bonus", "scholarship", "offered", "funded"}
    NEG = {"hated", "dreaded", "loathed", "annoyed", "disliked", "unhappy",
           "bothered", "poisoning", "canceled", "late", "rejection", "rejected",
           "failed", "broke", "mold", "doubled", "robbed", "surgery"}

    def __init__(self, name, seed_strength=0.6):
        self.name = name
        self.strength = seed_strength
        print(f"[{name}] MOCK model (no real inference)")

    def predict_proba_pos(self, sentences, batch_size=32):
        out = []
        for s in sentences:
            words = re.findall(r"[a-z']+", s.lower())
            score = 0.0
            first = next((w for w in words if w in self.POS or w in self.NEG), None)
            if first:
                score += self.strength * (1 if first in self.POS else -1)
            score += 0.30 * (sum(w in self.POS for w in words) - sum(w in self.NEG for w in words))
            h = int(hashlib.md5((self.name + s).encode()).hexdigest()[:6], 16) / 0xFFFFFF
            score += (h - 0.5) * 0.8
            out.append(1 / (1 + 2.718281828 ** (-3 * score)))
        return out


def check_label_mapping(model):
    """Catch an inverted pos/neg mapping before it silently ruins results."""
    pos, neg = model.predict_proba_pos(["I absolutely loved this wonderful film.",
                                         "This was a terrible, awful waste of time."])
    ok = pos > 0.5 > neg
    if not ok:
        print(f"  WARNING [{model.name}]: label sanity check failed "
              f"(p_pos on clearly-positive={pos:.2f}, on clearly-negative={neg:.2f}). "
              f"Check pos_index in model_configs.py.")
    return ok


def load_model(name, mock=False):
    if mock:
        return MockModel(name, seed_strength={"distilbert": 0.5, "bert": 0.35, "roberta": 0.2, "bert-large": 0.25, "roberta-large": 0.1}.get(name, 0.35))
    cfg = MODELS[name]
    model = SentimentModel(name, cfg["checkpoint"], cfg["pos_index"])
    check_label_mapping(model)
    return model
