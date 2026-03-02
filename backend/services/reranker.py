import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer


class CrossEncoderReranker:
    def __init__(
        self,
        model_name="BAAI/bge-reranker-base",
        device=None,
        batch_size=8
    ):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.batch_size = batch_size

        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.model.to(self.device)
        self.model.eval()

    def rerank(self, query: str, evidences: list, top_n=5):
        """
        evidences: list of dict with key 'text'
        """

        if not evidences:
            return []

        pairs = [[query, ev["text"]] for ev in evidences]

        scores = []

        with torch.no_grad():
            for i in range(0, len(pairs), self.batch_size):
                batch = pairs[i:i+self.batch_size]

                inputs = self.tokenizer(
                    batch,
                    padding=True,
                    truncation=True,
                    return_tensors="pt",
                    max_length=512
                )

                inputs = {k: v.to(self.device) for k, v in inputs.items()}

                outputs = self.model(**inputs)
                batch_scores = outputs.logits.view(-1).tolist()

                scores.extend(batch_scores)

        # attach scores
        for ev, score in zip(evidences, scores):
            ev["rerank_score"] = float(score)

        # sort descending
        reranked = sorted(
            evidences,
            key=lambda x: x["rerank_score"],
            reverse=True
        )

        return reranked[:top_n]