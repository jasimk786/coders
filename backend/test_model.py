# Test model loading and inference
import os
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch.nn.functional as F
import numpy as np

LOCAL_MODEL_DIR = os.path.join('..', 'fine_tuned_bert')
LOCAL_MODEL_DIR = os.path.normpath(LOCAL_MODEL_DIR)

print('Loading fine-tuned model...')
tokenizer = AutoTokenizer.from_pretrained(LOCAL_MODEL_DIR)
model = AutoModelForSequenceClassification.from_pretrained(LOCAL_MODEL_DIR)
model.eval()

print('Model loaded successfully!')
print('Config:', model.config.id2label)

# Test inference
test_texts = [
    'NASA discovers new planet with potential for life.',
    'BREAKING: Aliens invade Earth, martial law declared!'
]

print('\nTesting predictions:')
for text in test_texts:
    inputs = tokenizer(text, truncation=True, padding=True, return_tensors='pt')
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        probs = F.softmax(logits, dim=-1).squeeze().tolist()

    pred_index = np.argmax(probs)
    prediction = model.config.id2label[pred_index]
    confidence = probs[pred_index] * 100.0

    print(f'"{text[:40]}..." -> {prediction} ({confidence:.1f}%)')