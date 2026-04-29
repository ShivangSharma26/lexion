# The standard FUNSD tagging scheme (B-Header, I-Header, B-Question, I-Question, etc.)

LABELS = [
    "O",
    "B-HEADER",
    "I-HEADER",
    "B-QUESTION",
    "I-QUESTION",
    "B-ANSWER",
    "I-ANSWER"
]

def get_label_list():
    return LABELS

def id2label():
    return {i: label for i, label in enumerate(LABELS)}

def label2id():
    return {label: i for i, label in enumerate(LABELS)}
