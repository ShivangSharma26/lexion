# Lexicon: Document Intelligence Engine

Lexicon is an AI system that reads documents — invoices, resumes, contracts, forms — and pulls out the specific pieces of information that matter, automatically.

It uses LayoutLM (a Transformer model) to understand text AND its spatial layout (bounding boxes) via OCR, making it far superior to plain text models (like BERT) for document intelligence tasks.

## Setup

1. **Install Tesseract OCR**:
   - On Windows: Download and install from [UB-Mannheim](https://github.com/UB-Mannheim/tesseract/wiki). Ensure it's added to your PATH.
   - On Linux: `apt-get install tesseract-ocr`

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### 1. Fine-tuning the Model
You can fine-tune the LayoutLM model on the FUNSD dataset. By default, it runs on CPU with a tiny data subset for quick testing.
```bash
python train/finetune.py
```

### 2. Running the API
Start the FastAPI server:
```bash
uvicorn serve.api:app --reload
```
You can then send a POST request to `http://localhost:8000/extract` with a file (e.g. via Postman or `curl`) to get the structured entities back.

### 3. Docker
Build and run the complete system in Docker (includes Tesseract automatically):
```bash
docker build -t lexicon .
docker run -p 8000:8000 lexicon
```
