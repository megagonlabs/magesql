import json
import os

import torch
from transformers import DistilBertForSequenceClassification, DistilBertTokenizer

# Load the saved model, tokenizer, and label map
def load_model(model_path):
    print(f"Loading model and label map from {model_path}...")
    model = DistilBertForSequenceClassification.from_pretrained(model_path)
    tokenizer = DistilBertTokenizer.from_pretrained(model_path)

    # Load the label_map
    label_map_path = os.path.join(model_path, "label_map.json")
    with open(label_map_path, 'r') as f:
        label_map = json.load(f)

    return model, tokenizer, label_map

# Prediction function that returns db_id
def predict_db(model, tokenizer, text, device, label_map):
    model.eval()

    # Tokenizing the input text
    inputs = tokenizer.encode_plus(
        text,
        return_tensors="pt",
        max_length=128,
        truncation=True,
        padding='max_length'
    )

    input_ids = inputs['input_ids'].to(device)
    attention_mask = inputs['attention_mask'].to(device)

    # Forward pass
    with torch.no_grad():
        outputs = model(input_ids, attention_mask=attention_mask)
        logits = outputs.logits

    # Get predicted label index
    preds = torch.argmax(logits, dim=1).item()

    # Map the predicted index back to the db_id
    predicted_db_id = label_map[str(preds)]
    return predicted_db_id