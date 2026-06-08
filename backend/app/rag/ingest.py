import sys
from pathlib import Path

from pypdf import PdfReader
from sqlalchemy import text
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.db.database import engine
from app.rag.embedder import generate_embedding


# =========================
# TEXT SPLITTER (IMPROVED)
# =========================
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1200,
    chunk_overlap=200,
    separators=[
        "\n\n",
        "\n",
        ". ",
        " ",
        ""
    ]
)


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
# CHUNK TEXT
# =========================
def chunk_text(text):

    chunks = splitter.split_text(text)

    # remove tiny/noisy chunks
    cleaned_chunks = []

    for chunk in chunks:

        chunk = chunk.strip()

        if len(chunk) > 50:
            cleaned_chunks.append(chunk)

    return cleaned_chunks


# =========================
# MAIN INGEST FUNCTION
# =========================
def process_pdf(pdf_path):
    pdf_name = Path(pdf_path).name
    print("📄 Reading PDF...")

    text_data = extract_text_from_pdf(pdf_path)

    if not text_data.strip():
        print("❌ No text extracted from PDF")
        return

    print("✂ Chunking text...")

    chunks = chunk_text(text_data)

    print(f"🔢 Total chunks: {len(chunks)}")

    with engine.begin() as conn:

        for i, chunk in enumerate(chunks):

            print(f"➡ Processing chunk {i+1}/{len(chunks)}")

            embedding = generate_embedding(chunk)

            embedding_str = "[" + ",".join(map(str, embedding)) + "]"

            conn.execute(
                text("""
                    INSERT INTO documents 
                     (document_name,content, embedding)
                    VALUES (
                        :document_name,
                        :content,
                        CAST(:embedding AS vector)
                    )
                """),
                {
                    "document_name": pdf_name,
                    "content": chunk,
                    "embedding": embedding_str
                }
            )
    print("Saving document:", pdf_name)
    print("✅ PDF successfully ingested into vector DB!")


# =========================
# RUN FROM COMMAND LINE
# =========================
if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("❌ Provide file or folder path")
        sys.exit(1)

    path = Path(sys.argv[1])

    # =========================
    # SINGLE PDF
    # =========================
    if path.is_file() and path.suffix.lower() == ".pdf":

        process_pdf(str(path))

    # =========================
    # FOLDER OF PDFs
    # =========================
    elif path.is_dir():

        pdf_files = list(path.rglob("*.pdf"))

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