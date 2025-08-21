import sys
from pathlib import Path
from PyPDF2 import PdfReader
from ebooklib import epub
import piper

VOICE_FILE = "voices/fr/fr_FR/siwis/low/fr_FR-siwis-low.onnx"

def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    return "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])

def extract_text_from_epub(file_path):
    book = epub.read_epub(file_path)
    texts = []
    for item in book.get_items():
        if item.get_type() == epub.EpubHtml:
            texts.append(item.get_body_content().decode("utf-8"))
    return "\n".join(texts)

def main(file_path):
    path = Path(file_path)
    if not path.exists():
        print("❌ Fichier introuvable.")
        return

    if path.suffix.lower() == ".pdf":
        text = extract_text_from_pdf(file_path)
    elif path.suffix.lower() == ".epub":
        text = extract_text_from_epub(file_path)
    else:
        print("❌ Format non supporté (PDF ou EPUB uniquement).")
        return

    synthesizer = piper.Synthesizer(VOICE_FILE, config_path = VOICE_FILE + ".json"
)
    with open("output.mp3", "wb") as f:
        for chunk in synthesizer.synthesize(text):
            f.write(chunk)

    print("✅ Audio généré : output.mp3")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Utilisation : python tts.py mon_fichier.pdf")
    else:
        main(sys.argv[1])
