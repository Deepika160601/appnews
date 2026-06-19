from deep_translator import GoogleTranslator
 
 
def translate_text(
    text: str,
    source_lang: str,
    target_lang: str
) -> str:
 
    if not text:
        return ""
 
    try:
        return GoogleTranslator(
            source=source_lang,
            target=target_lang
        ).translate(text)
 
    except Exception:
        return text
 