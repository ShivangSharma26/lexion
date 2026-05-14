git rm Dockerfile config.yaml data/labels.py data/load.py eval/evaluate.py models/baseline_bert.py models/layoutlm.py ocr/extract.py requirements.txt serve/api.py train/finetune.py
git commit -m "refactor: restructure repository to separate backend and frontend"

git add backend/config.yaml
git commit -m "chore(backend): add configuration yaml"

git add backend/data/labels.py
git commit -m "feat(backend): add label mapping for token classification"

git add backend/data/load.py
git commit -m "feat(backend): implement FUNSD dataset loader"

git add backend/models/baseline_bert.py
git commit -m "feat(backend): implement baseline BERT model"

git add backend/models/layoutlm.py
git commit -m "feat(backend): implement LayoutLM token classification architecture"

git add backend/ocr/extract.py
git commit -m "feat(backend): integrate Tesseract OCR for text and bounding boxes"

git add backend/serve/api.py
git commit -m "feat(backend): create FastAPI server for inference and spatial pairing"

git add backend/train/finetune.py
git commit -m "feat(backend): create finetuning script for LayoutLM"

git add backend/requirements.txt
git commit -m "chore(backend): define python dependencies"

git add backend/Dockerfile
git commit -m "chore(backend): containerize FastAPI application"

git add frontend/package.json
git commit -m "chore(frontend): initialize Vite React project"

git add frontend/tailwind.config.js frontend/postcss.config.js
git commit -m "chore(frontend): configure Tailwind CSS for styling"

git add frontend/src/index.css
git commit -m "style(frontend): define base CSS and Deep Space theme tokens"

git add frontend/src/components/Header.jsx
git commit -m "feat(frontend): implement glassmorphic Header component"

git add frontend/src/components/UploadZone.jsx
git commit -m "feat(frontend): implement drag-and-drop UploadZone with neon glow"

git add frontend/src/components/ResultsDashboard.jsx
git commit -m "feat(frontend): implement ResultsDashboard with 2-column layout"

git add frontend/src/App.jsx
git commit -m "feat(frontend): assemble main App layout and wire API integration"

git add frontend/src/main.jsx
git commit -m "chore(frontend): set up React rendering entry point"

git add frontend/
git commit -m "chore(frontend): add remaining frontend boilerplate and assets"

git add .
git commit -m "chore: final cleanup and configuration"

git push origin main
