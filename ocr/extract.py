import pytesseract
from PIL import Image

def normalize_box(box, width, height):
    return [
        int(1000 * (box[0] / width)),
        int(1000 * (box[1] / height)),
        int(1000 * (box[2] / width)),
        int(1000 * (box[3] / height)),
    ]

def extract_text_and_boxes(image_path):
    """
    Extracts text and word-level bounding boxes from an image using PyTesseract.
    Returns:
        words: List of strings
        boxes: List of [x0, y0, x1, y1] normalized to 0-1000
    """
    image = Image.open(image_path).convert("RGB")
    width, height = image.size
    
    # We use pytesseract's image_to_data which gives details per word
    ocr_df = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
    
    words = []
    boxes = []
    
    n_boxes = len(ocr_df['text'])
    for i in range(n_boxes):
        word = ocr_df['text'][i]
        # Ignore empty text
        if word.strip() == '':
            continue
            
        x, y, w, h = (ocr_df['left'][i], ocr_df['top'][i], ocr_df['width'][i], ocr_df['height'][i])
        box = [x, y, x + w, y + h]
        normalized_box = normalize_box(box, width, height)
        
        words.append(word)
        boxes.append(normalized_box)
        
    return words, boxes, image
