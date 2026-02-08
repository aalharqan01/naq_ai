"""Seed script — load sample heritage texts into the database and vector store."""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.config import settings
from app.db.database import init_db, SessionLocal
from app.models.document import Document, DocumentType, ProcessingStatus
from app.services.embedding_service import embed_document
from app.services.entity_service import extract_entities
import json

SAMPLE_DIR = Path(__file__).parent / "data" / "sample"

# Metadata for each sample file
SAMPLES = [
    {
        "filename": "Pearl Diving in Qatar - Oral History.txt",
        "title": "Pearl Diving in Qatar - Oral History",
        "title_ar": "الغوص على اللؤلؤ في قطر - تاريخ شفوي",
        "description": "Traditional pearl diving practices and oral history from Qatari elders",
        "source": "National Archives of Qatar",
        "language": "en",
        "date_original": "1940s-1960s",
        "location": "Doha, Qatar",
    },
    {
        "filename": "Al Zubarah Archaeological Site - UNESCO Heritage.txt",
        "title": "Al Zubarah Archaeological Site - UNESCO Heritage",
        "title_ar": "موقع الزبارة الأثري - تراث اليونسكو",
        "description": "UNESCO World Heritage Site documentation for Al Zubarah",
        "source": "National Archives of Qatar",
        "language": "en",
        "date_original": "18th century",
        "location": "Al Zubarah, Qatar",
    },
    {
        "filename": "Traditional Qatari Architecture and the Barjeel.txt",
        "title": "Traditional Qatari Architecture and the Barjeel",
        "title_ar": "العمارة القطرية التقليدية والبارجيل",
        "description": "Traditional architectural techniques including wind towers",
        "source": "National Archives of Qatar",
        "language": "en",
        "date_original": "19th-20th century",
        "location": "Qatar",
    },
    {
        "filename": "Women of Qatar - Roles in Traditional Society.txt",
        "title": "Women of Qatar - Roles in Traditional Society",
        "title_ar": "نساء قطر - أدوار في المجتمع التقليدي",
        "description": "Roles of women in traditional Qatari society",
        "source": "National Archives of Qatar",
        "language": "en",
        "date_original": "1930s-1960s",
        "location": "Al Wakrah, Qatar",
    },
    {
        "filename": "تطور الدوحة من قرية صيد إلى عاصمة حديثة.txt",
        "title": "Evolution of Doha - From Fishing Village to Modern Capital",
        "title_ar": "تطور الدوحة من قرية صيد إلى عاصمة حديثة",
        "description": "Historical evolution of Doha from a small fishing village to a modern capital",
        "source": "National Archives of Qatar",
        "language": "ar",
        "date_original": "1820-2000",
        "location": "الدوحة، قطر",
    },
]


def seed():
    print("Initializing database...")
    init_db()
    db = SessionLocal()

    try:
        existing = db.query(Document).count()
        if existing > 0:
            print(f"Database already has {existing} documents. Skipping seed.")
            print("To re-seed, delete data/dhakira.db and data/chroma/ first.")
            return

        for sample in SAMPLES:
            filepath = SAMPLE_DIR / sample["filename"]
            if not filepath.exists():
                print(f"  SKIP: {sample['filename']} not found")
                continue

            text = filepath.read_text(encoding="utf-8")
            print(f"  Loading: {sample['title']}")

            doc = Document(
                title=sample["title"],
                title_ar=sample.get("title_ar"),
                description=sample.get("description"),
                doc_type=DocumentType.TEXT,
                file_path=str(filepath),
                file_size=len(text.encode("utf-8")),
                source=sample.get("source", "National Archives of Qatar"),
                language=sample.get("language", "en"),
                date_original=sample.get("date_original"),
                location=sample.get("location"),
                status=ProcessingStatus.PROCESSING,
                processed_text=text,
            )
            db.add(doc)
            db.commit()
            db.refresh(doc)

            # Extract entities
            entities = extract_entities(text)
            doc.entities_json = json.dumps(entities, ensure_ascii=False)

            # Embed in vector store
            metadata = {
                "title": doc.title,
                "doc_type": doc.doc_type.value,
                "source": doc.source or "National Archives of Qatar",
                "language": doc.language or "en",
                "date_original": doc.date_original or "",
                "location": doc.location or "",
            }
            embed_document(doc.id, text, metadata)

            doc.status = ProcessingStatus.COMPLETED
            db.commit()
            print(f"    Done (id={doc.id}, entities={len(entities)})")

        print(f"\nSeed complete! {len(SAMPLES)} documents loaded.")

    except Exception as e:
        print(f"Error during seeding: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
