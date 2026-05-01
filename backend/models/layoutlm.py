from transformers import LayoutLMForTokenClassification

def get_layoutlm_model(model_name, num_labels):
    # LayoutLM understands both text and layout (bounding boxes).
    model = LayoutLMForTokenClassification.from_pretrained(
        model_name,
        num_labels=num_labels
    )
    return model
