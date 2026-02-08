"""Entity extraction service for heritage documents."""

import json
import logging
import re
from typing import Optional

logger = logging.getLogger("dhakira.entity")

# Lazy-loaded models
_nlp_en = None
_nlp_ar_available = False


def _get_spacy_en():
    """Load English spaCy model."""
    global _nlp_en
    if _nlp_en is None:
        try:
            import spacy
            _nlp_en = spacy.load("en_core_web_sm")
            logger.info("spaCy English model loaded")
        except (ImportError, OSError):
            logger.warning(
                "spaCy or en_core_web_sm not available. "
                "Run: pip install spacy && python -m spacy download en_core_web_sm"
            )
            _nlp_en = None
    return _nlp_en


def _detect_language(text: str) -> str:
    """Simple heuristic to detect Arabic vs English."""
    arabic_chars = sum(1 for c in text if "\u0600" <= c <= "\u06FF")
    return "ar" if arabic_chars > len(text) * 0.3 else "en"


def _extract_arabic_entities(text: str) -> list[dict]:
    """
    Extract entities from Arabic text using pattern matching.
    Falls back to regex patterns when CAMeL Tools is unavailable.
    """
    entities = []

    try:
        from camel_tools.ner import NERecognizer
        ner = NERecognizer.pretrained()
        words = text.split()
        labels = ner.predict(words)

        current_entity = []
        current_label = None

        for word, label in zip(words, labels):
            if label.startswith("B-"):
                if current_entity:
                    entities.append({
                        "text": " ".join(current_entity),
                        "label": _map_label(current_label),
                    })
                current_entity = [word]
                current_label = label[2:]
            elif label.startswith("I-") and current_label:
                current_entity.append(word)
            else:
                if current_entity:
                    entities.append({
                        "text": " ".join(current_entity),
                        "label": _map_label(current_label),
                    })
                    current_entity = []
                    current_label = None

        if current_entity:
            entities.append({
                "text": " ".join(current_entity),
                "label": _map_label(current_label),
            })

        logger.info(f"CAMeL NER extracted {len(entities)} entities")

    except (ImportError, Exception) as e:
        logger.info(f"CAMeL Tools not available ({e}), using pattern-based extraction")
        entities = _pattern_based_arabic_ner(text)

    return entities


def _pattern_based_arabic_ner(text: str) -> list[dict]:
    """Fallback pattern-based entity extraction for Arabic text."""
    entities = []

    # Date patterns (Hijri and Gregorian)
    date_patterns = [
        r"\b\d{4}\s*[مم]?\b",  # Year
        r"\b\d{1,2}/\d{1,2}/\d{4}\b",  # DD/MM/YYYY
        r"\b\d{1,2}\s+(?:يناير|فبراير|مارس|أبريل|مايو|يونيو|يوليو|أغسطس|سبتمبر|أكتوبر|نوفمبر|ديسمبر)\s+\d{4}\b",
        r"\b\d{1,2}\s+(?:محرم|صفر|ربيع الأول|ربيع الآخر|جمادى الأولى|جمادى الآخرة|رجب|شعبان|رمضان|شوال|ذو القعدة|ذو الحجة)\s+\d{4}\b",
    ]
    for pattern in date_patterns:
        for match in re.finditer(pattern, text):
            entities.append({"text": match.group(), "label": "DATE"})

    # Location patterns — common Qatari/Gulf places
    qatar_locations = [
        "الدوحة", "قطر", "الخور", "الوكرة", "الريان", "أم صلال",
        "الشمال", "الذخيرة", "مسيعيد", "دخان", "الزبارة",
        "سوق واقف", "كتارا", "اللؤلؤة", "الخليج", "الجزيرة",
    ]
    for loc in qatar_locations:
        if loc in text:
            entities.append({"text": loc, "label": "LOCATION"})

    return entities


def _extract_english_entities(text: str) -> list[dict]:
    """Extract entities from English text using spaCy."""
    nlp = _get_spacy_en()
    if nlp is None:
        return []

    doc = nlp(text)
    entities = []

    label_map = {
        "PERSON": "PERSON",
        "GPE": "LOCATION",
        "LOC": "LOCATION",
        "ORG": "ORG",
        "DATE": "DATE",
        "EVENT": "EVENT",
        "NORP": "ORG",
        "FAC": "LOCATION",
    }

    for ent in doc.ents:
        mapped_label = label_map.get(ent.label_)
        if mapped_label:
            entities.append({
                "text": ent.text,
                "label": mapped_label,
                "start": ent.start_char,
                "end": ent.end_char,
            })

    return entities


def _map_label(label: str) -> str:
    """Map NER labels to our standard set."""
    mapping = {
        "PER": "PERSON",
        "PERS": "PERSON",
        "LOC": "LOCATION",
        "GPE": "LOCATION",
        "ORG": "ORG",
        "DATE": "DATE",
        "TIME": "DATE",
        "EVENT": "EVENT",
        "MISC": "OTHER",
    }
    return mapping.get(label, label)


def extract_entities(text: str) -> list[dict]:
    """
    Extract named entities from text (auto-detects language).

    Returns list of {"text": "...", "label": "PERSON|LOCATION|DATE|ORG|EVENT"}.
    """
    if not text or not text.strip():
        return []

    language = _detect_language(text)

    if language == "ar":
        entities = _extract_arabic_entities(text)
    else:
        entities = _extract_english_entities(text)

    # Deduplicate
    seen = set()
    unique = []
    for e in entities:
        key = (e["text"], e["label"])
        if key not in seen:
            seen.add(key)
            unique.append(e)

    logger.info(f"Extracted {len(unique)} unique entities ({language})")
    return unique
