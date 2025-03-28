from transformers import AutoTokenizer, AutoModelForSequenceClassification
from torch.nn.functional import softmax
import torch

MODEL_NAME = "savasy/bert-base-turkish-sentiment-cased"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)

labels = ['negative', 'neutral', 'positive']

NEGATIVE_HINTS = [
    "açılmıyor", "hata", "donuyor", "çöküyor", "sorun", "problem",
    "rezalet", "şikayet", "berbat", "kötü", "eksik", "tekrar yükledim",
    "memnun değilim", "kapanıyor", "gereksiz", "işe yaramıyor","eror",
    "error","hatalı","yanlış","yanlis","çöktü","çöker","çöküyor","çözüm","gerekir",
    "hata veriyor","hata alıyorum"
]

def analyze_sentiment(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)

    probabilities = softmax(outputs.logits, dim=1)
    predicted_class = torch.argmax(probabilities).item()
    label = labels[predicted_class]

    # Neutral'ları pozitif kabul et
    sentiment = "negative" if label == "negative" else "positive"

    # Ekstra kontrol: Olumsuz ipuçları varsa zorla negative'e çek
    lowered = text.lower()
    if sentiment == "positive" and any(neg in lowered for neg in NEGATIVE_HINTS):
        sentiment = "negative"

    return sentiment