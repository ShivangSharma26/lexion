import yaml
from datasets import load_dataset
from transformers import LayoutLMTokenizer

def load_config(config_path="config.yaml"):
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

def get_funsd_dataset(config):
    dataset_name = config["dataset"]["name"]
    train_samples = config["dataset"]["train_samples"]
    test_samples = config["dataset"]["test_samples"]

    # We use nielsr/funsd as it has word-level bboxes and labels
    dataset = load_dataset("nielsr/funsd", trust_remote_code=True)
    
    # Take subsets for CPU training
    train_ds = dataset["train"].select(range(min(train_samples, len(dataset["train"]))))
    test_ds = dataset["test"].select(range(min(test_samples, len(dataset["test"]))))
    
    return train_ds, test_ds

def prepare_dataset(dataset, tokenizer_name, max_seq_length):
    tokenizer = LayoutLMTokenizer.from_pretrained(tokenizer_name)
    
    def tokenize_and_align_labels(examples):
        tokenized_inputs = tokenizer(
            examples["words"],
            padding="max_length",
            truncation=True,
            max_length=max_seq_length,
            is_split_into_words=True,
            return_tensors="pt"
        )
        
        # HuggingFace LayoutLMTokenizer doesn't automatically handle bboxes well in the same call
        # in older versions without custom logic, but let's implement basic alignment
        bboxes = []
        labels = []

        for i, (word_boxes, word_labels) in enumerate(zip(examples["bboxes"], examples["ner_tags"])):
            word_ids = tokenized_inputs.word_ids(batch_index=i)
            
            box_seq = []
            label_seq = []
            
            for word_idx in word_ids:
                if word_idx is None:
                    box_seq.append([0, 0, 0, 0])
                    label_seq.append(-100) # Ignore index
                else:
                    box_seq.append(word_boxes[word_idx])
                    label_seq.append(word_labels[word_idx])
            
            bboxes.append(box_seq)
            labels.append(label_seq)

        tokenized_inputs["bbox"] = bboxes
        tokenized_inputs["labels"] = labels
        return tokenized_inputs

    tokenized_dataset = dataset.map(tokenize_and_align_labels, batched=True, remove_columns=dataset.column_names)
    tokenized_dataset.set_format(type="torch")
    
    return tokenized_dataset, tokenizer
