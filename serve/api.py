from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import torch
from transformers import LayoutLMForTokenClassification, LayoutLMTokenizer
from ocr.extract import extract_text_and_boxes
from data.labels import id2label
import os
import tempfile
import json

app = FastAPI(title="Lexicon Document Intelligence Engine")

# Load pre-finetuned model from Hugging Face for high accuracy out-of-the-box
MODEL_PATH = "nielsr/layoutlm-base-uncased-finetuned-funsd"
print(f"Loading fine-tuned model: {MODEL_PATH}")

tokenizer = LayoutLMTokenizer.from_pretrained(MODEL_PATH)
model = LayoutLMForTokenClassification.from_pretrained(MODEL_PATH)

model.eval()
id2l = model.config.id2label # Use the model's built-in label mapping

@app.post("/extract")
async def extract_document(file: UploadFile = File(...)):
    # Save uploaded file to temp
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        # Run OCR
        words, boxes, image = extract_text_and_boxes(tmp_path)
        
        if len(words) == 0:
            return JSONResponse(content={"error": "No text found in image"})

        # Tokenize
        encoding = tokenizer(
            words, 
            boxes=boxes, 
            return_tensors="pt", 
            truncation=True, 
            padding="max_length"
        )
        
        # Inference
        with torch.no_grad():
            outputs = model(**encoding)
            
        predictions = outputs.logits.argmax(-1).squeeze().tolist()
        
        # We need to map tokens back to words. 
        # For a production pipeline we'd group B/I tags and average probabilities for confidence.
        # Here we do a simplified word-level alignment.
        word_ids = encoding.word_ids(batch_index=0)
        
        results = []
        current_word_idx = -1
        
        for idx, word_id in enumerate(word_ids):
            if word_id is not None and word_id != current_word_idx:
                current_word_idx = word_id
                label = id2l.get(predictions[idx], "O")
                # Very basic confidence mock since we argmaxed. In real scenario use softmax.
                prob = torch.softmax(outputs.logits[0, idx], dim=-1)[predictions[idx]].item()
                
                results.append({
                    "word": words[word_id],
                    "label": label,
                    "confidence": round(prob, 4),
                    "box": boxes[word_id]
                })

        # Assemble structured output (combine sequential tokens of the same entity)
        entities = []
        current_entity = None
        
        for item in results:
            label = item["label"]
            if label.startswith("B-"):
                if current_entity:
                    entities.append(current_entity)
                current_entity = {
                    "type": label[2:],
                    "value": item["word"],
                    "confidence": item["confidence"]
                }
            elif label.startswith("I-") and current_entity and current_entity["type"] == label[2:]:
                current_entity["value"] += " " + item["word"]
                current_entity["confidence"] = min(current_entity["confidence"], item["confidence"])
            else:
                if current_entity:
                    entities.append(current_entity)
                    current_entity = None
        
        if current_entity:
            entities.append(current_entity)

        os.remove(tmp_path)
        return JSONResponse(content={"entities": entities})
        
    except Exception as e:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        return JSONResponse(content={"error": str(e)}, status_code=500)
