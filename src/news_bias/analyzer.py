import torch
from torch import Tensor, device as torch_device
from transformers import DistilBertForSequenceClassification, DistilBertTokenizerFast
from typing import List, Dict, Any, Union, Optional
import pandas as pd
from datetime import datetime

class BiasAnalyzer:
    def __init__(self, model_path: str):
        """Initialize the BiasAnalyzer with a trained model."""
        self.device: torch_device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        try:
            # Try loading as a local path
            from pathlib import Path
            model_path = str(Path(model_path).resolve())
            if not Path(model_path).exists():
                raise ValueError(f"Model path does not exist: {model_path}")

            self.model: DistilBertForSequenceClassification = DistilBertForSequenceClassification.from_pretrained(
                model_path,
                local_files_only=True,
                trust_remote_code=False
            )
            self.tokenizer = DistilBertTokenizerFast.from_pretrained(
                model_path,
                local_files_only=True,
                trust_remote_code=False
            )
        except Exception as e:
            print(f"Error loading model from local path: {e}")
            print("Falling back to default DistilBERT model...")
            self.model = DistilBertForSequenceClassification.from_pretrained('distilbert-base-uncased')
            self.tokenizer = DistilBertTokenizerFast.from_pretrained('distilbert-base-uncased')

        self.model = self.model.to(self.device)
        self.model.eval()

    def predict_bias(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Predict bias for a list of texts."""
        results: List[Dict[str, Any]] = []

        with torch.no_grad():
            for text in texts:
                inputs = self.tokenizer(
                    text,
                    return_tensors='pt',
                    truncation=True,
                    max_length=512
                )
                inputs = {k: v.to(self.device) for k, v in inputs.items()}

                outputs = self.model(**inputs)
                probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
                pred_tensor = torch.argmax(probs, dim=-1)
                pred_idx = int(pred_tensor[0].item())
                confidence = float(probs[0][pred_idx].item())

                results.append({
                    'text': text,
                    'bias': 'Left' if pred_idx == 1 else 'Right',
                    'confidence': confidence
                })

        return results

    def analyze_sources(self, headlines_by_source: Dict[str, List[str]]) -> pd.DataFrame:
        """Analyze headlines from multiple sources and return results as DataFrame."""
        all_results = []
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        for source, headlines in headlines_by_source.items():
            if headlines:
                results = self.predict_bias(headlines)
                for result in results:
                    result['source'] = source
                    result['timestamp'] = timestamp
                    all_results.append(result)

        return pd.DataFrame(all_results)
