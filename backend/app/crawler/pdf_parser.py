import fitz
import io
import re
from datetime import datetime
from PIL import Image
import pytesseract

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""

    for page in doc:
        page_text = page.get_text()

        if page_text.strip():
            text += page_text
            continue

        pix = doc[page.number].get_pixmap(matrix=fitz.Matrix(2, 2))
        image = Image.open(io.BytesIO(pix.tobytes("png")))
        text += pytesseract.image_to_string(image, lang="eng")

    return text


def extract_text_from_image(image_path):
    try:
        image = Image.open(image_path)
        return pytesseract.image_to_string(image, lang="eng")
    except Exception as e:
        print(f"Image OCR Error: {e}")
        return ""


def parse_notice_metadata(text: str):
    """
    Extracts semester, exam type, batch, and issued date from notice/admission text.
    """
    metadata = {}

    lower_text = text.lower()

    # Semester detection (works for "UG 10th Semester", "7th & 8th Semester", etc.)
    sem_match = re.search(r'(\d+)(?:st|nd|rd|th)\s+Semester', text, re.IGNORECASE)
    if sem_match:
        metadata["semester"] = sem_match.group(1)

    # Exam/admission type detection
    if "internal" in lower_text:
        metadata["exam_type"] = "internal"
    elif "external" in lower_text or "semester end" in lower_text:
        metadata["exam_type"] = "external"
    elif "admission" in lower_text or "selection list" in lower_text:
        metadata["exam_type"] = "admission"

    # Batch detection
    batch_match = re.search(r'Batch\s+(\d{4})', text)
    if batch_match:
        metadata["batch"] = batch_match.group(1)

    # Issued date detection (supports "Dated: 25-06-2026" or plain date)
    date_match = re.search(r'(\d{2}-\d{2}-\d{4})', text)
    if date_match:
        metadata["issued_date"] = datetime.strptime(
            date_match.group(1), "%d-%m-%Y"
        ).date().isoformat()

    return metadata


def extract_text_with_metadata(pdf_path):
    """
    Extracts text from PDF and attaches metadata for retrieval filtering.
    """
    text = extract_text_from_pdf(pdf_path)
    metadata = parse_notice_metadata(text)
    return {"text": text, "metadata": metadata}
