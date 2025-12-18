"""
Service d'extraction de thèmes simplifié (sans BERTopic)
"""
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from typing import List, Dict, Optional, Tuple
import logging
from collections import Counter
import numpy as np
from app.core.config import settings
from app.models.models import LanguageEnum

logger = logging.getLogger(__name__)


class TopicExtractor:
    """
    Extracteur de thèmes simple utilisant TF-IDF
    """
    
    def __init__(self):
        # Vectorizers par langue
        self._vectorizers = {
            LanguageEnum.FRENCH.value: self._get_french_vectorizer(),
            LanguageEnum.ARABIC.value: self._get_arabic_vectorizer(),
            LanguageEnum.DARIJA.value: self._get_darija_vectorizer(),
        }
    
    def _get_french_vectorizer(self) -> CountVectorizer:
        """Vectorizer pour le français avec stop words"""
        french_stop_words = [
            'le', 'la', 'les', 'un', 'une', 'des', 'de', 'du', 'à', 'au',
            'et', 'ou', 'mais', 'donc', 'or', 'ni', 'car', 'que', 'qui',
            'est', 'sont', 'était', 'ont', 'a', 'as', 'avez', 'ai',
            'ce', 'cet', 'cette', 'ces', 'mon', 'ma', 'mes', 'ton', 'ta', 'tes',
            'son', 'sa', 'ses', 'notre', 'nos', 'votre', 'vos', 'leur', 'leurs',
            'je', 'tu', 'il', 'elle', 'nous', 'vous', 'ils', 'elles',
            'pour', 'par', 'avec', 'sans', 'sur', 'sous', 'dans', 'en',
            # Mots supplémentaires trop génériques
            'tous', 'tout', 'toute', 'toutes', 'bien', 'très', 'plus', 'moins',
            'comme', 'aucun', 'aucune', 'beaucoup', 'peu', 'assez', 'trop',
            'même', 'aussi', 'encore', 'déjà', 'jamais', 'toujours', 'souvent',
            'rien', 'quelque', 'plusieurs', 'quelques', 'certains', 'certaines',
            'pas', 'non', 'oui', 'si', 'ne', 'n', 'y', 'd',
        ]
        return CountVectorizer(
            stop_words=french_stop_words,
            ngram_range=(1, 3),
            min_df=2
        )
    
    def _get_arabic_vectorizer(self) -> CountVectorizer:
        """Vectorizer pour l'arabe"""
        # Stop words arabes de base
        arabic_stop_words = [
            'في', 'من', 'إلى', 'على', 'عن', 'هذا', 'ذلك', 'التي', 'الذي',
            'هو', 'هي', 'أن', 'كان', 'لم', 'لن', 'قد', 'لكن', 'أو', 'و'
        ]
        return CountVectorizer(
            stop_words=arabic_stop_words,
            ngram_range=(1, 2),
            min_df=2
        )
    
    def _get_darija_vectorizer(self) -> CountVectorizer:
        """Vectorizer pour le Darija"""
        darija_stop_words = [
            'dyal', 'dial', 'w', 'wla', 'ola', 'bach', 'bla', 
            'hadi', 'hadak', 'hadik', 'hna', 'nta', 'nti', 'howa', 'hia'
        ]
        return CountVectorizer(
            stop_words=darija_stop_words,
            ngram_range=(1, 3),
            min_df=2
        )
    
    def extract_themes_single(
        self, 
        text: str, 
        language: str,
        top_n: int = 5
    ) -> List[str]:
        """
        Extrait les thèmes d'un texte unique en utilisant des mots-clés
        
        Args:
            text: Texte à analyser
            language: Code langue
            top_n: Nombre de thèmes à retourner
            
        Returns:
            Liste de thèmes identifiés
        """
        if not text or not text.strip():
            return []
        
        try:
            vectorizer = self._vectorizers.get(
                language, 
                self._vectorizers[LanguageEnum.FRENCH.value]
            )
            
            # Vectoriser le texte
            X = vectorizer.fit_transform([text])
            
            feature_names = vectorizer.get_feature_names_out()
            scores = X.toarray()[0]
            
            # Trier par score
            top_indices = scores.argsort()[-top_n:][::-1]
            themes = [feature_names[i] for i in top_indices if scores[i] > 0]
            
            return themes
            
        except Exception as e:
            logger.error(f"Error extracting themes: {e}")
            # Fallback: simple word frequency
            return self._simple_keyword_extraction(text, top_n)
    
    def extract_themes_batch(
        self,
        texts: List[str],
        languages: List[str],
        fit: bool = True
    ) -> Tuple[List[List[str]], Dict[str, any]]:
        """
        Extrait les thèmes d'un batch de textes (version simplifiée)
        
        Args:
            texts: Liste de textes
            languages: Liste de langues correspondantes
            fit: Ignoré (pour compatibilité)
            
        Returns:
            Tuple (themes_per_text, topic_info)
        """
        if not texts:
            return [], {}
        
        # Extraire les thèmes pour chaque texte individuellement
        all_themes = []
        for text, lang in zip(texts, languages):
            themes = self.extract_themes_single(text, lang, top_n=5)
            all_themes.append(themes)
        
        topic_info = {
            "method": "tfidf",
            "n_texts": len(texts)
        }
        
        return all_themes, topic_info
    
    def _simple_keyword_extraction(self, text: str, top_n: int = 5) -> List[str]:
        """
        Extraction simple de mots-clés par fréquence
        
        Args:
            text: Texte à analyser
            top_n: Nombre de mots-clés
            
        Returns:
            Liste de mots-clés
        """
        # Tokenisation simple
        words = text.lower().split()
        
        # Filtrer les mots courts et fréquents
        stop_words = {'le', 'la', 'les', 'un', 'une', 'de', 'du', 'et', 'ou', 'à', 'au', 'en', 'pour'}
        filtered_words = [
            word for word in words 
            if len(word) > 3 and word not in stop_words
        ]
        
        # Compter les fréquences
        word_freq = Counter(filtered_words)
        
        # Retourner les top N
        return [word for word, _ in word_freq.most_common(top_n)]
    
    def get_global_themes(
        self,
        texts: List[str],
        languages: List[str],
        top_n: int = 20
    ) -> List[Dict[str, any]]:
        """
        Obtient les thèmes globaux à travers tous les textes
        
        Args:
            texts: Liste de textes
            languages: Liste de langues
            top_n: Nombre de thèmes globaux
            
        Returns:
            Liste de dicts avec theme, frequency, language
        """
        # Extraire les thèmes pour chaque texte
        all_themes, _ = self.extract_themes_batch(texts, languages)
        
        # Compter les thèmes globaux par langue
        theme_counts = {}
        for themes, lang in zip(all_themes, languages):
            for theme in themes:
                key = (theme, lang)
                theme_counts[key] = theme_counts.get(key, 0) + 1
        
        # Trier et formater
        sorted_themes = sorted(
            theme_counts.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:top_n]
        
        return [
            {
                "theme": theme,
                "language": lang,
                "frequency": count,
                "keywords": [theme]  # Pourrait être étendu
            }
            for (theme, lang), count in sorted_themes
        ]


# Instance globale
_topic_extractor: Optional[TopicExtractor] = None


def get_topic_extractor() -> TopicExtractor:
    """Retourne l'instance singleton de TopicExtractor"""
    global _topic_extractor
    if _topic_extractor is None:
        _topic_extractor = TopicExtractor()
    return _topic_extractor
