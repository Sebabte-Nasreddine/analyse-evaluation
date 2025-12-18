"""
Service de détection de langue pour Français, Arabe et Darija
"""
import re
from typing import Optional
from langdetect import detect, DetectorFactory
from app.models.models import LanguageEnum

# Pour des résultats reproductibles
DetectorFactory.seed = 0


class LanguageDetector:
    """
    Détecteur de langue avec support spécial pour Darija
    """
    
    # Mots/expressions typiques du Darija
    DARIJA_MARKERS = {
        # Mots couramment utilisés en Darija
        'daba', 'bezzaf', 'mezyan', 'mzyan', 'dyal', 'kayn', 'makaynch',
        'wakha', 'ach', 'chno', 'kifach', 'fach', 'wach', 'smiya', 
        'kheddam', 'khdam', 'bach', 'hna', 'nta', 'ntina', 
        'ghir', 'bghit', 'bgha', 'machi', 'yallah', 'safi',
        # Expressions mixtes
        'had chi', 'dial', 'rah', 'ghi', 'bhal', 'w-', 'u',
    }
    
    # Patterns darija (mélange d'arabe et français)
    DARIJA_PATTERNS = [
        r'\b(ach|chno|kifach|fach|wach)\b',
        r'\b(daba|bezzaf|mezyan|mzyan)\b',
        r'\b(dyal|dial)\s+\w+',
        r'\b(kayn|makaynch)\b',
        r'\b(ghir|ghi)\s+\w+',
        r'\w+\s+(dyal|dial)\s+\w+',
    ]
    
    @classmethod
    def detect_language(cls, text: str) -> str:
        """
        Détecte la langue du texte
        
        Args:
            text: Texte à analyser
            
        Returns:
            Code langue: 'FR', 'AR', ou 'DARIJA'
        """
        if not text or not text.strip():
            return LanguageEnum.FRENCH.value
        
        text_lower = text.lower()
        
        # 1. Vérifier si c'est du Darija
        if cls._is_darija(text_lower):
            return LanguageEnum.DARIJA.value
        
        # 2. Détecter la langue avec langdetect
        try:
            detected = detect(text)
            
            # Mapper les codes de langue
            if detected == 'fr':
                return LanguageEnum.FRENCH.value
            elif detected == 'ar':
                # Re-vérifier si c'est pas du Darija malgré tout
                if cls._has_darija_features(text_lower):
                    return LanguageEnum.DARIJA.value
                return LanguageEnum.ARABIC.value
            elif detected in ['en', 'es', 'it']:
                # Langues latines, probablement français par défaut
                return LanguageEnum.FRENCH.value
            else:
                # Par défaut, on suppose français
                return LanguageEnum.FRENCH.value
                
        except Exception:
            # En cas d'erreur, on utilise des heuristiques
            return cls._detect_by_script(text)
    
    @classmethod
    def _is_darija(cls, text: str) -> bool:
        """
        Vérifie si le texte est principalement en Darija
        """
        # Compter les marqueurs Darija
        darija_count = sum(1 for marker in cls.DARIJA_MARKERS if marker in text)
        
        # Vérifier les patterns
        pattern_matches = sum(
            1 for pattern in cls.DARIJA_PATTERNS 
            if re.search(pattern, text, re.IGNORECASE)
        )
        
        return darija_count >= 2 or pattern_matches >= 1
    
    @classmethod
    def _has_darija_features(cls, text: str) -> bool:
        """
        Vérifie si le texte a des caractéristiques du Darija
        """
        darija_count = sum(1 for marker in cls.DARIJA_MARKERS if marker in text)
        return darija_count >= 1
    
    @classmethod
    def _detect_by_script(cls, text: str) -> str:
        """
        Détection basique par script (caractères arabes vs latins)
        """
        # Compter les caractères arabes
        arabic_chars = sum(1 for c in text if '\u0600' <= c <= '\u06FF')
        # Compter les caractères latins
        latin_chars = sum(1 for c in text if c.isalpha() and c < '\u0600')
        
        if arabic_chars > latin_chars:
            # Plus de caractères arabes
            if cls._has_darija_features(text.lower()):
                return LanguageEnum.DARIJA.value
            return LanguageEnum.ARABIC.value
        else:
            # Plus de caractères latins
            return LanguageEnum.FRENCH.value
    
    @classmethod
    def detect_batch(cls, texts: list[str]) -> list[str]:
        """
        Détecte la langue pour un batch de textes
        
        Args:
            texts: Liste de textes
            
        Returns:
            Liste de codes langue
        """
        return [cls.detect_language(text) for text in texts]
    
    @classmethod
    def get_confidence(cls, text: str, detected_lang: str) -> float:
        """
        Calcule un score de confiance pour la langue détectée
        
        Args:
            text: Texte original
            detected_lang: Langue détectée
            
        Returns:
            Score de confiance entre 0 et 1
        """
        if not text or not text.strip():
            return 0.5
        
        text_lower = text.lower()
        
        if detected_lang == LanguageEnum.DARIJA.value:
            # Compter les marqueurs Darija
            markers = sum(1 for marker in cls.DARIJA_MARKERS if marker in text_lower)
            patterns = sum(
                1 for pattern in cls.DARIJA_PATTERNS 
                if re.search(pattern, text_lower, re.IGNORECASE)
            )
            # Score basé sur le nombre de marqueurs
            score = min(1.0, (markers + patterns) / 5)
            return max(0.6, score)  # Minimum 60% si Darija détecté
        
        elif detected_lang == LanguageEnum.ARABIC.value:
            # Vérifier proportion de caractères arabes
            arabic_chars = sum(1 for c in text if '\u0600' <= c <= '\u06FF')
            total_chars = len([c for c in text if c.isalpha()])
            if total_chars > 0:
                return arabic_chars / total_chars
            return 0.5
        
        else:  # French
            # Utiliser langdetect pour le français
            try:
                from langdetect import detect_langs
                langs = detect_langs(text)
                for lang in langs:
                    if lang.lang == 'fr':
                        return lang.prob
                return 0.7  # Par défaut si français non trouvé
            except:
                return 0.7
