import fitz
import io

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

        pix = page.get_pixmap(
            matrix=fitz.Matrix(2, 2)
        )

        image = Image.open(
            io.BytesIO(
                pix.tobytes("png")
            )
        )

        text += pytesseract.image_to_string(
            image,
            lang="eng"
        )

    return text


def extract_text_from_image(image_path):

    try:

        image = Image.open(image_path)

        return pytesseract.image_to_string(
            image,
            lang="eng"
        )

    except Exception as e:

        print(
            f"Image OCR Error: {e}"
        )

        return ""