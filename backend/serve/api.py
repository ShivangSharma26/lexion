from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import torch
from transformers import LayoutLMForTokenClassification, LayoutLMTokenizerFast
from ocr.extract import extract_text_and_boxes
from data.labels import id2label
import os
from pdf2image import convert_from_path
import tempfile
import json

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Lexicon Document Intelligence Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows all origins
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods
    allow_headers=["*"], # Allows all headers
)

# Load pre-finetuned model from Hugging Face for high accuracy out-of-the-box
MODEL_PATH = "philschmid/layoutlm-funsd"
print(f"Loading fine-tuned model: {MODEL_PATH}")

tokenizer = LayoutLMTokenizerFast.from_pretrained(MODEL_PATH)
model = LayoutLMForTokenClassification.from_pretrained(MODEL_PATH)

model.eval()
id2l = model.config.id2label # Use the model's built-in label mapping

@app.post("/extract")
async def extract_document(file: UploadFile = File(...)):
    is_pdf = file.filename.lower().endswith('.pdf')
    suffix = ".pdf" if is_pdf else ".png"

    # Save uploaded file to temp
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        # If PDF, convert the first page to an image
        if is_pdf:
            images = convert_from_path(tmp_path, first_page=1, last_page=1)
            if not images:
                raise Exception("Could not extract image from PDF")
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as img_tmp:
                images[0].save(img_tmp.name, "PNG")
                process_path = img_tmp.name
        else:
            process_path = tmp_path

        # Run OCR
        words, boxes, image = extract_text_and_boxes(process_path)
        
        if len(words) == 0:
            return JSONResponse(content={"error": "No text found in image"})

        # Tokenize (text only first)
        encoding = tokenizer(
            words, 
            is_split_into_words=True,
            return_tensors="pt", 
            truncation=True, 
            padding="max_length",
            max_length=512
        )
        
        # Align bounding boxes to tokens manually
        word_ids = encoding.word_ids(batch_index=0)
        box_seq = []
        for word_idx in word_ids:
            if word_idx is None:
                box_seq.append([0, 0, 0, 0])
            else:
                box_seq.append(boxes[word_idx])
                
        encoding["bbox"] = torch.tensor([box_seq])
        
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
                    "confidence": item["confidence"],
                    "box": item["box"]
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

        # --- GENERALIZED SPATIAL RELATION EXTRACTION ---
        questions = [e for e in entities if e["type"] == "QUESTION"]
        answers = [e for e in entities if e["type"] == "ANSWER"]
        headers = [e for e in entities if e["type"] == "HEADER"]
        
        # Initialize answers array for each question
        for q in questions:
            q["matched_answers"] = []

        unpaired_answers = []

        # For every answer, find the most logical Question parent (either Column Header or Row Key)
        for a in answers:
            a_box = a["box"]
            a_cx = (a_box[0] + a_box[2]) / 2
            a_cy = (a_box[1] + a_box[3]) / 2
            
            best_q = None
            best_dist = float('inf')
            
            for q in questions:
                q_box = q["box"]
                q_cx = (q_box[0] + q_box[2]) / 2
                q_cy = (q_box[1] + q_box[3]) / 2
                
                dx = a_cx - q_cx
                dy = a_cy - q_cy
                
                # An answer belongs to a question if it is:
                # 1. Directly below it (Table Column scenario) -> dy > 0, small dx
                # 2. Directly to the right of it (Form Key-Value scenario) -> dx > 0, small dy
                if (dy > -20 and abs(dx) < 250) or (dx > -20 and abs(dy) < 50):
                    # Distance metric preferring vertical alignment (tables) and horizontal alignment (forms)
                    dist = abs(dy) + (abs(dx) * 1.5)
                    if dist < best_dist:
                        best_dist = dist
                        best_q = q
            
            if best_q:
                best_q["matched_answers"].append(a)
            else:
                unpaired_answers.append(a)
                
        # Format for frontend
        final_entities = []
        for q in questions:
            if q["matched_answers"]:
                # If it's a table column, it has multiple answers
                for ans in q["matched_answers"]:
                    final_entities.append({
                        "type": "PAIRED",
                        "question": q["value"],
                        "answer": ans["value"],
                        "confidence": min(q["confidence"], ans["confidence"])
                    })
            else:
                final_entities.append({
                    "type": "PAIRED",
                    "question": q["value"],
                    "answer": None,
                    "confidence": q["confidence"]
                })
                
        for h in headers:
            final_entities.append({"type": "HEADER", "value": h["value"], "confidence": h["confidence"]})
            
        for a in unpaired_answers:
            final_entities.append({"type": "UNPAIRED_ANSWER", "value": a["value"], "confidence": a["confidence"]})

        os.remove(tmp_path)
        if is_pdf and os.path.exists(process_path):
            os.remove(process_path)
        return JSONResponse(content={"entities": final_entities})
        
    except Exception as e:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        if 'process_path' in locals() and os.path.exists(process_path):
            os.remove(process_path)
        return JSONResponse(content={"error": str(e)}, status_code=500)
