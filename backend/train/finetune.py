import os
import torch
from transformers import Trainer, TrainingArguments
from data.load import load_config, get_funsd_dataset, prepare_dataset
from data.labels import get_label_list, id2label, label2id
from models.layoutlm import get_layoutlm_model
from eval.evaluate import compute_metrics

def main():
    config = load_config()
    device = config["training"]["device"]
    
    # Force CPU if requested
    if device == "cpu":
        os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
        print("Forcing CPU training as per config.")
        
    labels = get_label_list()
    num_labels = len(labels)
    
    print("Loading dataset...")
    train_ds_raw, test_ds_raw = get_funsd_dataset(config)
    
    print("Tokenizing and aligning labels...")
    train_dataset, tokenizer = prepare_dataset(train_ds_raw, config["model"]["name"], config["model"]["max_seq_length"])
    test_dataset, _ = prepare_dataset(test_ds_raw, config["model"]["name"], config["model"]["max_seq_length"])

    print("Initializing model...")
    model = get_layoutlm_model(config["model"]["name"], num_labels)
    model.config.id2label = id2label()
    model.config.label2id = label2id()

    training_args = TrainingArguments(
        output_dir="./layoutlm-funsd-finetuned",
        max_steps=config["training"]["num_epochs"] * len(train_dataset) // config["training"]["batch_size"],
        per_device_train_batch_size=config["training"]["batch_size"],
        per_device_eval_batch_size=config["training"]["batch_size"],
        learning_rate=float(config["training"]["learning_rate"]),
        evaluation_strategy="steps",
        eval_steps=10,
        save_steps=10,
        logging_steps=5,
        no_cuda=(device == "cpu"),
        report_to="none" # skip wandb/tensorboard for testing
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=test_dataset,
        tokenizer=tokenizer,
        compute_metrics=compute_metrics
    )

    print("Starting training...")
    trainer.train()
    
    print("Evaluating...")
    metrics = trainer.evaluate()
    print("Evaluation Metrics:", metrics)
    
    trainer.save_model("./layoutlm-funsd-finetuned")
    print("Model saved to ./layoutlm-funsd-finetuned")

if __name__ == "__main__":
    main()
