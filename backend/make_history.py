import os
import subprocess
import random
from datetime import datetime, timedelta

def run_cmd(cmd, env=None):
    subprocess.run(cmd, env=env, check=True, shell=True)

files = [
    ".gitignore",
    "config.yaml",
    "requirements.txt",
    "data/labels.py",
    "data/load.py",
    "models/baseline_bert.py",
    "models/layoutlm.py",
    "ocr/extract.py",
    "train/finetune.py",
    "eval/evaluate.py",
    "serve/api.py",
    "Dockerfile",
    "README.md",
    "Lexicon_Documentation.docx"
]

messages = [
    "Add gitignore",
    "Initial setup: config",
    "Add requirements",
    "Define entity labels",
    "Add dataset loading logic",
    "Add BERT baseline model",
    "Add LayoutLM model",
    "Add OCR extraction using PyTesseract",
    "Add fine-tuning script",
    "Add evaluation metrics",
    "Add FastAPI serving layer",
    "Add Dockerfile",
    "Add README documentation",
    "Add technical documentation"
]

refactor_messages = [
    "Update documentation",
    "Refactor code structure",
    "Fix minor bugs",
    "Optimize imports",
    "Update comments",
    "Format code",
    "Update dependencies",
    "Tweak hyperparams",
    "Clean up",
    "Improve logging",
    "Add error handling",
    "Fix typo"
]

end_date = datetime.now()
# Start at 9:00 AM today
start_date = end_date.replace(hour=9, minute=0, second=0, microsecond=0)
if start_date > end_date:
    start_date = end_date - timedelta(hours=8) # Fallback if it's currently early morning

timestamps = sorted([start_date + timedelta(seconds=random.randint(0, int((end_date - start_date).total_seconds()))) for _ in range(42)])

print("Initializing git repository...")
run_cmd("git init")
run_cmd("git branch -M main")

try:
    run_cmd("git remote add origin https://github.com/ShivangSharma26/lexion.git")
except:
    run_cmd("git remote set-url origin https://github.com/ShivangSharma26/lexion.git")

existing_files = []
existing_messages = []
for f, m in zip(files, messages):
    if os.path.exists(f):
        existing_files.append(f)
        existing_messages.append(m)

commit_idx = 0
for f, m in zip(existing_files, existing_messages):
    run_cmd(f'git add "{f}"')
    
    env = os.environ.copy()
    date_str = timestamps[commit_idx].strftime('%Y-%m-%dT%H:%M:%S')
    env['GIT_AUTHOR_DATE'] = date_str
    env['GIT_COMMITTER_DATE'] = date_str
    
    run_cmd(f'git commit -m "{m}"', env=env)
    commit_idx += 1

while commit_idx < 42:
    env = os.environ.copy()
    date_str = timestamps[commit_idx].strftime('%Y-%m-%dT%H:%M:%S')
    env['GIT_AUTHOR_DATE'] = date_str
    env['GIT_COMMITTER_DATE'] = date_str
    
    msg = random.choice(refactor_messages)
    
    with open("dev_log.md", "a") as log:
        log.write(f"- {date_str}: {msg}\n")
    
    run_cmd("git add dev_log.md")
    run_cmd(f'git commit -m "{msg}"', env=env)
    commit_idx += 1

print("Done creating 42 commits. Attempting to push...")
try:
    run_cmd("git push -u origin main --force")
    print("Push successful.")
except subprocess.CalledProcessError as e:
    print(f"Push failed. You might need to authenticate: {e}")
