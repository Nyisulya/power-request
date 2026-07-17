import logging
from deep_translator import GoogleTranslator

logger = logging.getLogger(__name__)

def translate_text(text):
    """
    Translates input text into both English and Swahili using GoogleTranslator with 'auto' detection.
    Returns:
        (text_en, text_sw): A tuple of English and Swahili translations.
    """
    if not text or not text.strip():
        return "", ""

    text = text.strip()
    
    # Translate to English
    try:
        translated_en = GoogleTranslator(source='auto', target='en').translate(text)
    except Exception as e:
        logger.error(f"Failed to translate to English: {e}")
        translated_en = text  # Fallback to original text

    # Translate to Swahili
    try:
        translated_sw = GoogleTranslator(source='auto', target='sw').translate(text)
    except Exception as e:
        logger.error(f"Failed to translate to Swahili: {e}")
        translated_sw = text  # Fallback to original text

    # Safety checks if translation returned empty or None
    if not translated_en:
        translated_en = text
    if not translated_sw:
        translated_sw = text

    return translated_en, translated_sw
