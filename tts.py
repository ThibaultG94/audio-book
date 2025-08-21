#!/usr/bin/env python3
import sys, re, wave, unicodedata, subprocess, tempfile, os, shutil
from pathlib import Path
from PyPDF2 import PdfReader
from ebooklib import epub, ITEM_DOCUMENT
from bs4 import BeautifulSoup

VOICE_FILE = "voices/fr/fr_FR/siwis/low/fr_FR-siwis-low.onnx"
LENGTH_SCALE = "1.0"     # 0.9 = un peu plus rapide ; 1.1 = un peu plus lent
NOISE_SCALE  = "0.667"
NOISE_W      = "0.8"
SENT_SIL     = "0.35"    # pause entre phrases côté CLI
PAUSE_BETWEEN_BLOCKS = 0.35  # pause manuelle entre blocs (sécurité)

def extract_text_from_pdf(fp: Path) -> str:
    reader = PdfReader(str(fp))
    parts = []
    for page in reader.pages:
        t = page.extract_text() or ""
        parts.append(t)
    return "\n".join(parts)

def extract_text_from_epub(fp: Path) -> str:
    book = epub.read_epub(str(fp))
    chunks = []
    for item in book.get_items_of_type(ITEM_DOCUMENT):
        html = item.get_content().decode("utf-8", errors="ignore")
        text = BeautifulSoup(html, "lxml").get_text(" ", strip=True)
        chunks.append(text)
    return "\n".join(chunks)

def clean_text(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{2,}", "\n\n", text)
    return text.strip()

def chunk_paragraphs(text: str, max_chars: int = 1500):
    paras = [p.strip() for p in re.split(r"\n{2,}", text) if p.strip()]
    cur, count = [], 0
    for p in paras:
        if count + len(p) > max_chars and cur:
            yield "\n".join(cur)
            cur, count = [p], len(p)
        else:
            cur.append(p); count += len(p)
    if cur:
        yield "\n".join(cur)

def call_piper_cli_to_wav(block_text: str, out_wav: Path):
    # On passe le texte via stdin (chaque ligne = une “utterance”)
    cmd = [
        "piper",
        "--model", VOICE_FILE,
        "--output_file", str(out_wav),
        "--length_scale", LENGTH_SCALE,
        "--noise_scale", NOISE_SCALE,
        "--noise_w", NOISE_W,
        "--sentence_silence", SENT_SIL,
    ]
    # piper lit une ligne = un énoncé ; on force un seul énoncé par bloc
    subprocess.run(cmd, input=block_text.strip()+"\n", text=True, check=True)

def append_wav(dst_wf: wave.Wave_write, src_wav: Path):
    with wave.open(str(src_wav), "rb") as sf:
        # vérifier format
        assert sf.getnchannels() == dst_wf.getnchannels()
        assert sf.getsampwidth() == dst_wf.getsampwidth()
        assert sf.getframerate() == dst_wf.getframerate()
        frames = sf.readframes(sf.getnframes())
        dst_wf.writeframes(frames)

def write_silence(dst_wf: wave.Wave_write, seconds: float, sample_rate: int):
    if seconds <= 0: return
    n_samples = int(seconds * sample_rate)
    dst_wf.writeframes(b"\x00\x00" * n_samples)

def main():
    if len(sys.argv) < 2:
        print("Usage: python tts_cli.py <fichier.pdf|fichier.epub> [out.wav]")
        sys.exit(1)

    in_path = Path(sys.argv[1])
    out_path = Path(sys.argv[2]) if len(sys.argv) >= 3 else Path("output.wav")

    if not shutil.which("piper"):
        print("❌ Le binaire `piper` n'est pas trouvé dans le PATH.")
        sys.exit(1)

    if not in_path.exists():
        print("❌ Fichier introuvable:", in_path); sys.exit(1)

    if in_path.suffix.lower() == ".pdf":
        raw = extract_text_from_pdf(in_path)
    elif in_path.suffix.lower() == ".epub":
        raw = extract_text_from_epub(in_path)
    else:
        print("❌ Format non supporté (PDF ou EPUB uniquement)."); sys.exit(1)

    text = clean_text(raw)

    # On génère chaque bloc dans un wav temporaire via le CLI, puis on concatène proprement
    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        tmp_wavs = []
        print("⏳ Synthèse par blocs…")
        for i, block in enumerate(chunk_paragraphs(text)):
            wpath = td_path / f"chunk_{i:05d}.wav"
            call_piper_cli_to_wav(block, wpath)
            tmp_wavs.append(wpath)

        # Ouvrir le premier pour récupérer le format (mono, 16-bit, rate)
        if not tmp_wavs:
            print("⚠️ Aucun texte après nettoyage.")
            sys.exit(0)

        with wave.open(str(tmp_wavs[0]), "rb") as ref:
            nch, sw, sr = ref.getnchannels(), ref.getsampwidth(), ref.getframerate()

        with wave.open(str(out_path), "wb") as out_wf:
            out_wf.setnchannels(nch)
            out_wf.setsampwidth(sw)
            out_wf.setframerate(sr)

            for j, w in enumerate(tmp_wavs):
                append_wav(out_wf, w)
                # petite pause entre blocs (en plus du sentence_silence interne)
                if PAUSE_BETWEEN_BLOCKS and j < len(tmp_wavs) - 1:
                    write_silence(out_wf, PAUSE_BETWEEN_BLOCKS, sr)

    print(f"✅ Audio généré : {out_path}")

if __name__ == "__main__":
    main()
