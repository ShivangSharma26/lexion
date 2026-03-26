from transformers import BertForTokenClassification

def get_bert_model(num_labels):
    # This is a baseline text-only model.
    # It ignores layout (bounding boxes) completely.
    model = BertForTokenClassification.from_pretrained(
        "bert-base-uncased",
        num_labels=num_labels
    )
    return model
