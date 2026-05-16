import sys
from pypdf import PdfReader
from sqlalchemy import text

from app.db.database import engine
from app.rag.chunker import chunk_text
from app.rag.embedder import generate_embedding


# =========================
# EXTRACT TEXT FROM PDF
# =========================
def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text_data = ""

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text_data += page_text + "\n"

    return text_data


# =========================
# MAIN INGEST FUNCTION
# =========================
def process_pdf(pdf_path):

    print("📄 Reading PDF...")
    text_data = extract_text_from_pdf(pdf_path)

    print("✂ Chunking text...")
    chunks = chunk_text(text_data)

    print(f"🔢 Total chunks: {len(chunks)}")

    with engine.begin() as conn:

        for i, chunk in enumerate(chunks):

            print(f"➡ Processing chunk {i+1}/{len(chunks)}")

            embedding = generate_embedding(chunk)

            conn.execute(
                text("""
                    INSERT INTO documents (content, embedding)
                    VALUES (:content, :embedding)
                """),
                {
                    "content": chunk,
                    "embedding": embedding
                }
            )

    print("✅ PDF successfully ingested into vector DB!")


# =========================
# RUN FROM COMMAND LINE
# =========================
from pathlib import Path

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("❌ Provide file or folder path")
        sys.exit(1)

    path = Path(sys.argv[1])

    # CASE 1: single PDF
    if path.is_file() and path.suffix == ".pdf":
        process_pdf(str(path))

    # CASE 2: folder (MULTIPLE PDFs)
    elif path.is_dir():

        pdf_files = list(path.rglob("*.pdf"))  # IMPORTANT FIX

        if not pdf_files:
            print("❌ No PDF files found")
            sys.exit(1)

        print(f"📁 Found {len(pdf_files)} PDFs")

        for pdf in pdf_files:
            try:
                print(f"\n📄 Ingesting: {pdf.name}")
                process_pdf(str(pdf))
            except Exception as e:
                print(f"❌ Failed {pdf.name}: {e}")

        print("\n🎉 All PDFs ingested successfully!")

    else:
        print("❌ Invalid path")