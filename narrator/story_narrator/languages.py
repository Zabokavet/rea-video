"""Narration languages. Haitian Creole (Kreyòl ayisyen) is the primary language and the default."""
from __future__ import annotations

DEFAULT_LANGUAGE = "ht"

# code -> native name, English name, Meta MMS checkpoint (native voice), hint for prompted voices
LANGUAGES: dict[str, dict] = {
    "ht": {"name": "Kreyòl ayisyen", "english": "Haitian Creole", "mms": "facebook/mms-tts-hat",
           "instructions": "Speak in Haitian Creole (Kreyòl ayisyen) with a natural, native Haitian accent. "
                           "Do not use a French or English accent. Read it as a warm, expressive storyteller."},
    "fr": {"name": "Français", "english": "French", "mms": "facebook/mms-tts-fra",
           "instructions": "Speak in French with a natural accent, as a warm storyteller."},
    "en": {"name": "English", "english": "English", "mms": "facebook/mms-tts-eng",
           "instructions": "Speak in English as a warm, expressive storyteller."},
    "es": {"name": "Español", "english": "Spanish", "mms": "facebook/mms-tts-spa",
           "instructions": "Speak in Spanish with a natural accent, as a warm storyteller."},
}


def language(code: str) -> dict:
    return LANGUAGES.get(code) or LANGUAGES[DEFAULT_LANGUAGE]
