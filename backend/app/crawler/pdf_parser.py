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

def roman_to_int(roman: str) -> int:
    roman_map = {
        "I": 1, "II": 2, "III": 3, "IV": 4, "V": 5,
        "VI": 6, "VII": 7, "VIII": 8, "IX": 9, "X": 10
    }
    return roman_map.get(roman.upper(), None)

def word_to_int(word: str) -> int:
    word_map = {
        "first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5,
        "sixth": 6, "seventh": 7, "eighth": 8, "ninth": 9, "tenth": 10
    }
    return word_map.get(word.lower(), None)

def parse_notice_metadata(text: str):
    metadata = {}
    lower_text = text.lower()

    # Semester detection (only 1–10 allowed, numeric, roman, or word-based ordinals)
    sem_matches = re.findall(
        r'(?:Semester\s*(?:No\.?\s*)?(?:-|–)?\s*(\d+)|(\d+)(?:st|nd|rd|th)?\s*Semester|Sem\s*[-:]?\s*(\d+)|Semester\s*(First|Second|Third|Fourth|Fifth|Sixth|Seventh|Eighth|Ninth|Tenth)|\b(First|Second|Third|Fourth|Fifth|Sixth|Seventh|Eighth|Ninth|Tenth)\b)',
        text,
        re.IGNORECASE
    )

    semesters = []
    for match in sem_matches:
        for m in match:
            if not m:
                continue
            if m.isdigit():
                num = int(m)
                if 1 <= num <= 10:
                    semesters.append(str(num))
            elif re.match(r'^[IVX]+$', m, re.IGNORECASE):
                num = roman_to_int(m)
                if num and 1 <= num <= 10:
                    semesters.append(str(num))
            else:
                num = word_to_int(m)
                if num and 1 <= num <= 10:
                    semesters.append(str(num))

    if semesters:
        metadata["semester"] = ",".join(sorted(set(semesters), key=int))

    # Exam/admission type detection (admission has priority)
    if "admission" in lower_text or "selection list" in lower_text or "counselling" in lower_text:
        metadata["exam_type"] = "admission"
    elif "internal" in lower_text:
        metadata["exam_type"] = "internal"
    elif "external" in lower_text or "semester end" in lower_text:
        metadata["exam_type"] = "external"
    elif "timetable" in lower_text or "time table" in lower_text:
        metadata["exam_type"] = "timetable"
    else:
        metadata["exam_type"] = None

    # Batch detection
    batch_match = re.search(r'[Bb]atch(?:\s+of)?\s*(\d{4})(?:[-/](\d{2,4}))?', text)
    if batch_match:
        if batch_match.group(2):
            metadata["batch"] = f"{batch_match.group(1)}-{batch_match.group(2)}"
        else:
            metadata["batch"] = batch_match.group(1)

    # Issued date detection
    date_match = re.search(r'(\d{2}-\d{2}-\d{4})', text)
    if date_match:
        metadata["issued_date"] = datetime.strptime(
            date_match.group(1), "%d-%m-%Y"
        ).date().isoformat()

    return metadata

def extract_text_with_metadata(pdf_path):
    text = extract_text_from_pdf(pdf_path)
    metadata = parse_notice_metadata(text)
    return {"text": text, "metadata": metadata}