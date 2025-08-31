#!/usr/bin/env python3

import re
import unicodedata

class TextProcessor:
    @staticmethod
    def clean_text(text: str) -> str:
        # Step 1: Use NFC normalization (composed form) to avoid decomposed characters
        text = unicodedata.normalize("NFC", text)
        
        # Step 2: Remove problematic characters that cause Piper issues
        # Remove combining diacritical marks that Piper can't handle
        text = "".join(c for c in text if unicodedata.category(c) != 'Mn')
        
        # Step 3: Replace specific problematic characters
        replacements = {
            # Remove phonetic symbols that cause Piper errors
            '\u0303': '',  # COMBINING TILDE (phonetic nasalization)
            '\u0301': '',  # COMBINING ACUTE ACCENT
            '\u0300': '',  # COMBINING GRAVE ACCENT  
            '\u0302': '',  # COMBINING CIRCUMFLEX ACCENT
            '\u030C': '',  # COMBINING CARON
            '\u0327': '',  # COMBINING CEDILLA
            # Remove zero-width characters
            '\u200B': '',  # ZERO WIDTH SPACE
            '\u200C': '',  # ZERO WIDTH NON-JOINER
            '\u200D': '',  # ZERO WIDTH JOINER
            '\uFEFF': '',  # ZERO WIDTH NO-BREAK SPACE
            # Replace problematic quotation marks
            '"': '"',      # LEFT DOUBLE QUOTATION MARK
            '"': '"',      # RIGHT DOUBLE QUOTATION MARK
            ''': "'",      # LEFT SINGLE QUOTATION MARK
            ''': "'",      # RIGHT SINGLE QUOTATION MARK
            # Replace problematic dashes
            '—': '-',      # EM DASH
            '–': '-',      # EN DASH
            # Replace ellipsis
            '…': '...',    # HORIZONTAL ELLIPSIS
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        # Step 4: Keep only safe characters for French TTS
        # Allow basic Latin, French accented characters, digits, punctuation, and whitespace
        safe_pattern = r'[a-zA-Z0-9àáâäçèéêëïîôöùúûüÿÀÁÂÄÇÈÉÊËÏÎÔÖÙÚÛÜŸ\s\.,!?;:()\-\'"«»\n]'
        text = ''.join(c for c in text if re.match(safe_pattern, c))
        
        # Step 5: Clean up whitespace
        text = re.sub(r"[ \t]+", " ", text)  # Multiple spaces/tabs -> single space
        text = re.sub(r"\n{2,}", "\n\n", text)  # Multiple newlines -> double newline
        text = re.sub(r"^\s+|\s+$", "", text, flags=re.MULTILINE)  # Trim lines
        
        return text.strip()

# Test text with problematic characters
test_text = """
Voici un texte avec des caractères problématiques :

• Caractères combinés avec tildes : ñ̃ẽ̃
• Guillemets spéciaux : "test" 'autre'
• Tirets : — et – différents
• Espaces spéciaux : test​test (zero-width)
• Ellipses : test…fin

Ce texte devrait être nettoyé pour Piper.
"""

print("🧪 Test du nettoyage de texte pour Piper TTS")
print("=" * 50)
print("AVANT nettoyage :")
print(repr(test_text))
print("\nAPRÈS nettoyage :")
cleaned = TextProcessor.clean_text(test_text)
print(repr(cleaned))
print("\nTexte final :")
print(cleaned)

print("\n✅ Test terminé - vérifiez que les caractères problématiques ont été supprimés")