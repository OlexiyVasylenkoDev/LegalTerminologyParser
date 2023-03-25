from googletrans import Translator


def translate_message(message: str) -> str:
    translator = Translator()
    translation = translator.translate(message, dest='uk')
    return translation.text
