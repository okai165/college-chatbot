import os
import json
from datetime import datetime, timedelta

from fastapi import APIRouter, UploadFile, File, Form
from sqlalchemy import text

from pypdf import PdfReader
from docx import Document

from pdf2image import convert_from_path
import pytesseract

from app.db.database import engine
from app.rag.chunker import chunk_text
from app.rag.embedder import generate_embedding

router = APIRouter()

UPLOAD_FOLDER = "uploads"
METADATA_FILE = os.path.join(UPLOAD_FOLDER, "metadata.json")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

if not os.path.exists(METADATA_FILE):
    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump([], f)


def load_metadata():
    try:
        with open(METADATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_metadata(metadata):
    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)


# =========================
# TESSERACT PATH
# =========================
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


# =========================
# PDF TEXT EXTRACTION
# =========================
def extract_pdf_text(path):

    text_data = ""

    # =========================
    # NORMAL PDF EXTRACTION
    # =========================
    try:

        reader = PdfReader(path)

        for page in reader.pages:

            page_text = page.extract_text()

            if page_text:
                text_data += page_text + "\n"

    except Exception as e:

        print("❌ Normal PDF extraction failed:", e)

    # =========================
    # OCR FALLBACK
    # =========================
    if len(text_data.strip()) < 50:

        print("⚠ Scanned PDF detected → Running OCR...")

        try:

            images = convert_from_path(
                path,
                poppler_path=r"C:\poppler\Release-26.02.0-0\poppler-26.02.0\Library\bin"
            )

            print(f"📸 Total pages converted: {len(images)}")

            for i, img in enumerate(images):

                print(f"🔍 OCR page {i+1}")

                ocr_text = pytesseract.image_to_string(
                    img,
                    lang="eng",
                    config="--psm 6"
                )

                text_data += ocr_text + "\n"

        except Exception as e:

            print("❌ OCR failed:", e)

    return text_data


# =========================
# DOCX EXTRACTION
# =========================
def extract_docx_text(path):

    doc = Document(path)

    return "\n".join(
        [p.text for p in doc.paragraphs]
    )


# =========================
# TXT EXTRACTION
# =========================
def extract_txt_text(path):

    with open(path, "r", encoding="utf-8") as f:
        return f.read()


# =========================
# INGEST FUNCTION
# =========================
def ingest_text(text_data):

    chunks = chunk_text(text_data)

    print(f"\n📦 TOTAL CHUNKS: {len(chunks)}")

    with engine.begin() as conn:

        for i, chunk in enumerate(chunks):

            print(f"➡ Ingesting chunk {i+1}")

            embedding = generate_embedding(chunk)

            conn.execute(
                text("""
                    INSERT INTO documents
                    (content, embedding)
                    VALUES
                    (:content, :embedding)
                """),
                {
                    "content": chunk,
                    "embedding": embedding
                }
            )

    print("✅ Ingestion completed")


# =========================
# FILE UPLOAD API
# =========================
@router.post("/upload-documents")
async def upload_documents(
    files: list[UploadFile] = File(...),
    category: str = Form("Admission")
):

    uploaded_files = []
    metadata = load_metadata()

    for file in files:

        print(f"\n📄 Processing: {file.filename}")

        file_path = os.path.join(
            UPLOAD_FOLDER,
            file.filename
        )

        # =========================
        # SAVE FILE
        # =========================
        with open(file_path, "wb") as f:

            content = await file.read()

            f.write(content)

        # =========================
        # EXTRACT TEXT
        # =========================
        text_data = ""

        if file.filename.lower().endswith(".pdf"):

            text_data = extract_pdf_text(file_path)

        elif file.filename.lower().endswith(".docx"):

            text_data = extract_docx_text(file_path)

        elif file.filename.lower().endswith(".txt"):

            text_data = extract_txt_text(file_path)

        else:

            print(f"❌ Unsupported file: {file.filename}")
            continue

        # =========================
        # DEBUG OUTPUT
        # =========================
        print("\n===== EXTRACTED TEXT =====\n")
        print(text_data[:2000])

        # =========================
        # INGEST
        # =========================
        if text_data.strip():

            ingest_text(text_data)

            uploaded_files.append(file.filename)
            metadata.append({
                "filename": file.filename,
                "category": category,
                "uploaded_at": datetime.utcnow().isoformat(),
                "size": len(content)
            })

            print(f"✅ Successfully ingested: {file.filename}")

        else:

            print(f"❌ No text extracted from: {file.filename}")

    save_metadata(metadata)

    return {
        "message": "Documents uploaded and ingested successfully",
        "files": uploaded_files
    }


@router.get("/uploaded-documents")
def get_uploaded_documents(
    category: str | None = None,
    days: int | None = None
):
    metadata = load_metadata()
    
    # Create a dict for quick lookup of existing metadata by filename
    metadata_dict = {item["filename"]: item for item in metadata}
    
    # Scan uploads folder for files and add missing metadata
    if os.path.exists(UPLOAD_FOLDER):
        for filename in os.listdir(UPLOAD_FOLDER):
            if filename == "metadata.json":
                continue
            
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            
            # Only process files, not directories
            if not os.path.isfile(file_path):
                continue
            
            # If metadata doesn't exist for this file, create it
            if filename not in metadata_dict:
                file_stat = os.stat(file_path)
                metadata_dict[filename] = {
                    "filename": filename,
                    "category": "Misc",
                    "uploaded_at": datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                    "size": file_stat.st_size
                }
    
    # Convert dict back to list
    metadata = list(metadata_dict.values())

    if category and category.lower() != "all":
        metadata = [
            item for item in metadata
            if item.get("category", "").lower() == category.lower()
        ]

    if days is not None and days > 0:
        cutoff = datetime.utcnow() - timedelta(days=days)
        metadata = [
            item for item in metadata
            if datetime.fromisoformat(item.get("uploaded_at", "")) >= cutoff
        ]

    metadata.sort(
        key=lambda item: item.get("uploaded_at", ""),
        reverse=True
    )

    return {"files": metadata}