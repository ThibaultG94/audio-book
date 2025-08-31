#!/usr/bin/env python3

import sys
sys.path.append('backend')

from backend.app.services.text_processor import TextProcessor

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